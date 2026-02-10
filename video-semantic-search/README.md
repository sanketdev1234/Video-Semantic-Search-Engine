# 🎥 Video Semantic Search Engine

> Search inside videos using AI-powered semantic search. Upload videos or YouTube URLs and find exact moments using natural language queries.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)
![Node](https://img.shields.io/badge/node-16%2B-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

- 🎬 **Upload Videos** - Process MP4, MOV, AVI, MKV files
- 📺 **YouTube Support** - Paste YouTube URLs for instant analysis
- 🔍 **Semantic Search** - Find moments using natural language (not just keywords)
- ⏱️ **Timestamp Jumping** - Click results to jump to exact video moments
- 📄 **Auto Notes** - Get PDF notes with summary, keywords, and transcript
- 🎨 **Visual Search** - CLIP embeddings for frame-level search (infrastructure ready)
- 💾 **Persistent Storage** - All data saved automatically

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- FFmpeg ([Install Guide](https://ffmpeg.org/download.html))

### Installation

```bash
# Clone or extract the project
cd video-semantic-search

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend setup
cd ../frontend
npm install
```

### Run

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser!

---

## 📖 How to Use

### 1️⃣ Upload a Video
- Click "Choose File" and select your video
- Click "Upload & Index" 
- Wait for processing (1-5 minutes)

### 2️⃣ Or Use YouTube
- Paste a YouTube URL
- Click "Analyze URL"
- Small YouTube window opens automatically

### 3️⃣ Search
- Enter natural language query: "What is machine learning?"
- Press Enter or click Search
- Get results with timestamps

### 4️⃣ Jump to Moments
- **Uploaded videos:** Click result → Player seeks to timestamp
- **YouTube videos:** Click result → YouTube window jumps to timestamp

### 5️⃣ Get Notes
- Click "Download Notes (PDF)"
- Includes summary, keywords, full transcript, and frame snapshots

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - High-performance async API
- **Whisper** - Audio transcription (OpenAI)
- **SentenceTransformers** - Text embeddings (384-dim)
- **CLIP** - Visual embeddings (512-dim)
- **FAISS** - Vector similarity search
- **yt-dlp** - YouTube download

### Frontend
- **React 19** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling

---

## 📁 Project Structure

```
video-semantic-search/
├── backend/
│   ├── app/
│   │   ├── main.py           # API endpoints
│   │   ├── config.py         # Settings
│   │   └── services/         # Core logic
│   ├── uploads/              # Uploaded videos
│   ├── processed/            # Processed data & PDFs
│   ├── indexes/              # FAISS indexes (persistent)
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── App.jsx           # Main UI
    │   └── services/api.js   # API client
    └── package.json
```

---

## ⚙️ Configuration

Edit `backend/app/config.py`:

```python
# Model selection
WHISPER_MODEL = "base"  # tiny, base, small, medium, large
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Processing settings
FRAME_INTERVAL_SECONDS = 10  # Frame extraction interval
MAX_FRAMES = 10              # Maximum frames per video
TOP_K_RESULTS = 5            # Search results count
```

---

## 🔧 Troubleshooting

### FFmpeg Not Found
```bash
# Windows (using winget)
winget install FFmpeg

# Verify
ffmpeg -version
```

### Port Already in Use
```bash
# Backend: Use different port
python -m uvicorn app.main:app --port 8001

# Frontend: Edit vite.config.js
```

### Out of Memory
- Use shorter videos (< 10 minutes)
- Close other applications
- Upgrade to `tiny` Whisper model

### YouTube Download Failed
- Check video is public
- Verify internet connection
- Try different video

---

## 📊 Performance

### Processing Times (CPU)
- **10-minute video:** ~5 minutes
- **30-minute video:** ~15 minutes
- **YouTube audio:** ~2-3 minutes per 10 min

### Memory Usage
- **Idle:** ~500MB
- **Processing:** ~2-3GB
- **Peak:** ~4-5GB

---

## 🎯 Features Fixed in v2.0

✅ **Data Persistence** - FAISS indexes saved to disk  
✅ **YouTube Support** - Full URL video processing  
✅ **Video Filtering** - Search within specific videos  
✅ **Error Handling** - Better error messages and recovery  
✅ **Windows Compatibility** - FFmpeg console hiding  
✅ **Deep Links** - YouTube timestamp URLs  
✅ **Small Window** - YouTube opens in popup  
✅ **Source Tracking** - Distinguishes upload vs URL videos

---

## 🐛 Known Limitations

- ⚠️ YouTube only (no Vimeo, Dailymotion, etc.)
- ⚠️ CPU only (no GPU acceleration)
- ⚠️ Synchronous processing (blocks during upload)
- ⚠️ No multi-user support
- ⚠️ No authentication

---

## 🚧 Roadmap

### Coming Soon
- [ ] GPU acceleration support
- [ ] Multiple video comparison
- [ ] Visual search UI
- [ ] Export search results
- [ ] Progress indicators
- [ ] Video duration display

### Future
- [ ] User authentication
- [ ] Database integration (PostgreSQL)
- [ ] Async processing (Celery)
- [ ] Cloud deployment guides
- [ ] Mobile app
- [ ] Collaborative notes

---

## 📝 API Endpoints

### `POST /upload`
Upload video file
```json
Response: {
  "video_id": "uuid",
  "filename": "video.mp4",
  "status": "completed"
}
```

### `POST /upload-url`
Process YouTube URL
```json
Request: {"url": "https://youtube.com/..."}
Response: {
  "video_id": "uuid",
  "filename": "Video Title",
  "status": "completed"
}
```

### `GET /search?query={q}&video_id={id}`
Semantic search
```json
Response: {
  "query": "machine learning",
  "results": [
    {
      "video_id": "uuid",
      "timestamp": 45.2,
      "text": "Machine learning is...",
      "score": 0.89,
      "source": "upload",
      "deep_link": null
    }
  ]
}
```

### `GET /notes/{video_id}`
Get PDF notes
```json
Response: {
  "video_id": "uuid",
  "pdf_url": "/processed/uuid/notes.pdf"
}
```

---

## 🔒 Security Notice

⚠️ **This is designed for local/development use!**

Current limitations:
- No authentication
- CORS wide open
- No rate limiting
- No input validation
- Not HTTPS

**Do not expose to public internet without proper security measures.**

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch
3. Make your changes
4. Submit pull request

---

## 🙏 Acknowledgments

Built with:
- [Whisper](https://github.com/openai/whisper) by OpenAI
- [SentenceTransformers](https://www.sbert.net/)
- [CLIP](https://github.com/openai/CLIP) by OpenAI
- [FAISS](https://github.com/facebookresearch/faiss) by Meta
- [FastAPI](https://fastapi.tiangolo.com/)
- [React](https://react.dev/)

---

## 📞 Support

For detailed setup instructions, see [SETUP.md](SETUP.md)

Having issues? Check:
1. FFmpeg is installed and in PATH
2. Python virtual environment is activated
3. All dependencies installed
4. Ports 8000 and 5173 are free

---

**Made with ❤️ for video content creators and researchers**

**Version 2.0.0** | CPU Optimized | Windows Compatible
