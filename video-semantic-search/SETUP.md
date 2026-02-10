# Video Semantic Search - Setup Guide

## Prerequisites

### 1. Install Python 3.8+
Download from: https://www.python.org/downloads/

Verify installation:
```bash
python --version
```

### 2. Install Node.js 16+
Download from: https://nodejs.org/

Verify installation:
```bash
node --version
npm --version
```

### 3. Install FFmpeg (REQUIRED)

#### Option A: Using winget (Windows 10/11)
```bash
winget install FFmpeg
```

#### Option B: Manual Installation
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Open System Properties → Environment Variables
   - Edit "Path" under System Variables
   - Add: `C:\ffmpeg\bin`
4. Restart command prompt and verify:
```bash
ffmpeg -version
```

---

## Installation Steps

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
```

3. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate
```

4. **Install dependencies:**
```bash
pip install -r requirements.txt
```

**Note:** First run will download AI models (~570MB):
- Whisper base: ~140MB
- SentenceTransformer: ~80MB
- CLIP: ~350MB

5. **Create required directories:**
```bash
mkdir uploads processed temp indexes
```

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

---

## Running the Application

### Start Backend (Terminal 1)

```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```

Backend will run on: http://127.0.0.1:8000

### Start Frontend (Terminal 2)

```bash
cd frontend
npm run dev
```

Frontend will run on: http://localhost:5173

---

## Usage

### 1. Upload a Video File
- Click "Choose File" and select MP4, MOV, AVI, or MKV
- Click "Upload & Index"
- Wait for processing (may take 1-5 minutes depending on video length)
- Video player will appear when ready

### 2. Process YouTube URL
- Paste a YouTube URL in the text field
- Click "Analyze URL"
- A small YouTube window will open
- Search results will control this window

### 3. Search Inside Videos
- Enter a natural language query (e.g., "What is machine learning?")
- Click "Search" or press Enter
- Results appear with timestamps

### 4. Jump to Timestamps
- Click any search result
- **Uploaded videos:** Player seeks to that timestamp
- **YouTube videos:** Small window jumps to that timestamp

### 5. Download Notes
- After video is processed, click "Download Notes (PDF)"
- PDF contains:
  - Summary (top 3 key points)
  - Keywords (top 8 concepts)
  - Full transcript with timestamps
  - Visual highlights (frame snapshots)

---

## Troubleshooting

### FFmpeg Not Found
**Error:** `FFmpeg not found!`

**Solution:**
1. Install FFmpeg (see Prerequisites)
2. Restart your terminal
3. Verify: `ffmpeg -version`

### Port Already in Use
**Error:** `Address already in use`

**Backend Solution:**
```bash
# Use different port
python -m uvicorn app.main:app --port 8001
```

**Frontend Solution:**
Edit `vite.config.js`:
```javascript
export default {
  server: {
    port: 5174
  }
}
```

### Module Not Found
**Error:** `No module named 'app'`

**Solution:**
```bash
# Make sure you're in the backend directory
cd backend
# Activate venv
venv\Scripts\activate
```

### YouTube Download Failed
**Error:** `YouTube processing failed`

**Possible causes:**
1. Invalid URL
2. Video is private/restricted
3. Network issues

**Solution:**
- Verify URL is public
- Check internet connection
- Try a different video

### Slow Processing
**Performance tips:**
- Use shorter videos for testing (< 10 minutes)
- Processing time: ~30 seconds per minute of video
- Close other CPU-intensive applications

---

## File Structure

```
video-semantic-search/
├── backend/
│   ├── app/
│   │   ├── main.py              # API endpoints
│   │   ├── config.py            # Configuration
│   │   ├── models.py            # Data models
│   │   └── services/
│   │       ├── video.py         # Video processing
│   │       ├── search.py        # Search logic
│   │       ├── store.py         # FAISS storage
│   │       ├── url_video.py     # YouTube support
│   │       ├── pdf_builder.py   # PDF generation
│   │       ├── summarizer.py    # Text summarization
│   │       └── keywords.py      # Keyword extraction
│   ├── uploads/                 # Uploaded videos
│   ├── processed/               # Processed data
│   ├── temp/                    # Temporary files
│   ├── indexes/                 # FAISS indexes (persistent)
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── App.jsx              # Main component
    │   ├── services/
    │   │   └── api.js           # API calls
    │   └── assets/
    ├── package.json
    └── vite.config.js
```

---

## API Endpoints

### POST /upload
Upload a video file for processing
- **Input:** multipart/form-data with video file
- **Output:** `{video_id, filename, status, message}`

### POST /upload-url
Process a YouTube video
- **Input:** `{url: "https://youtube.com/..."}`
- **Output:** `{video_id, filename, status, message, url}`

### GET /search?query={query}&video_id={optional}
Search inside videos
- **Input:** `query` (required), `video_id` (optional)
- **Output:** `{query, results[], total_results}`

### GET /notes/{video_id}
Get PDF notes for a video
- **Output:** `{video_id, pdf_url}`

### GET /stats
Get system statistics
- **Output:** `{text_index_size, visual_index_size, total_videos}`

---

## Configuration

Edit `backend/app/config.py` to customize:

```python
# Model selection
WHISPER_MODEL: str = "base"  # Options: tiny, base, small, medium, large
EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

# Processing
FRAME_INTERVAL_SECONDS: int = 10  # Frame extraction interval
MAX_FRAMES: int = 10  # Maximum frames to extract
MAX_VIDEO_SIZE_MB: int = 200

# Search
TOP_K_RESULTS: int = 5  # Number of search results
```

---

## Performance Notes

### CPU Optimization
All models run on CPU with optimizations:
- FP16 disabled for Whisper
- CPU device explicitly set for all models
- FFmpeg configured for efficient processing

### Expected Processing Times
- **10-minute video:** ~5 minutes
- **30-minute video:** ~15 minutes
- **YouTube audio only:** ~2-3 minutes per 10 minutes

### Memory Usage
- **Idle:** ~500MB
- **Processing:** ~2-3GB
- **With large video:** ~4-5GB

---

## Data Persistence

### Automatic Saving
FAISS indexes are automatically saved to `indexes/` directory:
- `text_index.faiss` - Text embeddings
- `visual_index.faiss` - Visual embeddings
- `text_metadata.pkl` - Text metadata
- `visual_metadata.pkl` - Visual metadata
- `video_metadata.pkl` - Video information

### Manual Backup
To backup your data:
```bash
# Backup indexes
cp -r backend/indexes/ backup/indexes/

# Backup processed files
cp -r backend/processed/ backup/processed/
```

---

## Supported Video Formats

### Upload
- ✅ MP4 (recommended)
- ✅ MOV
- ✅ AVI
- ✅ MKV

### URL
- ✅ YouTube videos
- ❌ Other platforms (not supported yet)

---

## Security Notes

⚠️ **This is for local/development use only!**

Current setup:
- CORS is wide open (`allow_origins=["*"]`)
- No authentication
- No file size validation
- Temporary files not cleaned up

For production use, implement:
- Authentication (JWT, OAuth)
- File validation
- Rate limiting
- HTTPS
- Proper CORS configuration

---

## Getting Help

### Logs
Backend logs appear in terminal where you ran `uvicorn`

### Common Issues
1. **Models not loading:** Check internet connection (first run downloads models)
2. **FFmpeg errors:** Verify FFmpeg is in PATH
3. **Out of memory:** Use smaller videos or close other applications
4. **Search returns nothing:** Make sure video was fully processed

---

## Next Steps

### Enhancements You Can Make
1. Add video duration display
2. Show processing progress
3. Multi-video comparison
4. Export search results
5. Visual search UI
6. Dark/light theme toggle

### Production Deployment
1. Add authentication
2. Use PostgreSQL instead of pickle files
3. Add Redis for caching
4. Implement task queue (Celery)
5. Deploy to cloud (AWS, Azure, GCP)
6. Add monitoring and logging

---

**Version:** 2.0.0  
**Last Updated:** February 2026  
**Python:** 3.8+  
**Node.js:** 16+
