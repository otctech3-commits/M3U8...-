# M3U8...-
~
# 🎬 MK Anime HLS Uploader

Upload anime → Auto convert to M3U8 → All audio tracks preserved → Stream anywhere

![Luffy](https://media.tenor.com/GfSXNpmLNv8AAAAC/luffy-one-piece.gif)

## ✨ Features
- 📤 Upload MP4/MKV upto 2GB
- 🎵 **All Audio Tracks** - Tamil/English/Japanese auto detected
- 🔗 **M3U8 Link** - Works in VLC, MX Player, Browser
- ⚡ **Auto HLS Convert** - FFmpeg + Multi-quality
- 🌐 **Browser Preview** - HLS.js player built-in
- 🚀 **Render Ready** - One-click deploy

## 🔧 Deploy to Render

1. **Fork this repo** or upload files
2. **Render.com** → New Web Service → Connect GitHub
3. **Runtime: Docker** → Deploy
4. Done! `https://yourapp.onrender.com`

## 📱 How to Use

1. Open site → Click upload
2. Select anime video with multi audio
3. Wait for convert - progress bar shows
4. Copy M3U8 link → Paste in VLC or Blog
5. In VLC: Audio → Audio Track → Select language

## 🎮 Tech Stack
- **Backend**: Flask + Gunicorn
- **Video**: FFmpeg HLS with audio mapping
- **Frontend**: Vanilla JS + HLS.js
- **Deploy**: Docker on Render Free Tier

## ⚠️ Notes
- Free Render sleeps after 15min idle
- First request takes ~30s to wake
- Files stored in `/static/hls/` - delete manually
- Max 2GB per file - Telegram API limit

## 📝 License
MIT - Use anywhere da 🔥

Made with ❤️ by MK
