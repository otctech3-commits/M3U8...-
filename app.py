from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import subprocess
import uuid
import threading
import json

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB

UPLOAD_FOLDER = 'uploads'
HLS_FOLDER = 'static/hls'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(HLS_FOLDER, exist_ok=True)

jobs = {}

def convert_to_hls(job_id, input_path, output_dir):
    try:
        jobs[job_id]['status'] = 'processing'

        # Get all audio streams info
        probe_cmd = [
            'ffprobe', '-v', 'quiet', '-print_format', 'json', 
            '-show_streams', input_path
        ]
        probe_result = subprocess.run(probe_cmd, capture_output=True, text=True)
        streams = json.loads(probe_result.stdout)['streams']

        audio_streams = [s for s in streams if s['codec_type'] == 'audio']
        audio_count = len(audio_streams)

        # Build FFmpeg command for HLS with all audio tracks
        os.makedirs(output_dir, exist_ok=True)

        # Master playlist with multiple audio renditions
        cmd = [
            'ffmpeg', '-i', input_path,
            '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '23',
            '-c:a', 'aac', '-b:a', '128k',
            '-map', '0:v:0'
        ]

        # Map all audio streams
        for i in range(audio_count):
            cmd.extend(['-map', f'0:a:{i}'])

        # HLS settings
        cmd.extend([
            '-f', 'hls',
            '-hls_time', '6',
            '-hls_list_size', '0',
            '-hls_segment_filename', f'{output_dir}/segment_%v_%03d.ts',
            '-master_pl_name', 'master.m3u8',
            '-var_stream_map'
        ])

        # Create variants for each audio
        var_map = 'v:0'
        for i in range(audio_count):
            var_map += f',a:{i},name:audio_{i}'
        cmd.append(var_map)
        cmd.append(f'{output_dir}/stream_%v.m3u8')

        subprocess.run(cmd, check=True)

        # Update master.m3u8 with audio metadata
        master_path = os.path.join(output_dir, 'master.m3u8')
        with open(master_path, 'r') as f:
            content = f.read()

        # Add audio group tags
        audio_tags = []
        for idx, stream in enumerate(audio_streams):
            lang = stream.get('tags', {}).get('language', f'track{idx}')
            title = stream.get('tags', {}).get('title', lang)
            audio_tags.append(f'#EXT-X-MEDIA:TYPE=AUDIO,GROUP-ID="audio",NAME="{title}",LANGUAGE="{lang}",DEFAULT={"YES" if idx==0 else "NO"},URI="stream_audio_{idx}.m3u8"')

        lines = content.split('\n')
        new_lines = []
        inserted = False
        for line in lines:
            new_lines.append(line)
            if line.startswith('#EXT-X-VERSION') and not inserted:
                new_lines.extend(audio_tags)
                inserted = True

        # Add AUDIO="audio" to stream inf
        final_lines = []
        for line in new_lines:
            if line.startswith('#EXT-X-STREAM-INF'):
                line = line.rstrip() + ',AUDIO="audio"'
            final_lines.append(line)

        with open(master_path, 'w') as f:
            f.write('\n'.join(final_lines))

        jobs[job_id]['status'] = 'completed'
        jobs[job_id]['m3u8_url'] = f'/static/hls/{job_id}/master.m3u8'

    except Exception as e:
        jobs[job_id]['status'] = 'failed'
        jobs[job_id]['error'] = str(e)
    finally:
        if os.path.exists(input_path):
            os.remove(input_path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'video' not in request.files:
        return jsonify({'error': 'No file'}), 400

    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    job_id = str(uuid.uuid4())
    filename = f"{job_id}_{file.filename}"
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_dir = os.path.join(HLS_FOLDER, job_id)

    file.save(input_path)
    jobs[job_id] = {'status': 'queued'}

    thread = threading.Thread(target=convert_to_hls, args=(job_id, input_path, output_dir))
    thread.start()

    return jsonify({'job_id': job_id})

@app.route('/status/<job_id>')
def status(job_id):
    job = jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)

@app.route('/static/hls/<path:path>')
def serve_hls(path):
    return send_from_directory(HLS_FOLDER, path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
