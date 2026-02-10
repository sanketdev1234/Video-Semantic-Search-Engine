# 🚀 QUICK START GUIDE

## Get Running in 10 Minutes!

### Step 1: Install FFmpeg (REQUIRED!)

**Windows 10/11:**
```bash
winget install FFmpeg
```

**Manual:**
1. Download: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to System PATH
4. Restart terminal
5. Verify: `ffmpeg -version`

---

### Step 2: Setup Backend

```bash
# Extract the zip file first!

# Go to backend folder
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install packages (will download ~570MB AI models on first run)
pip install -r requirements.txt
```

---

### Step 3: Setup Frontend

```bash
# Open NEW terminal
cd frontend

# Install packages
npm install
```

---

### Step 4: Run Everything

**Terminal 1 (Backend):**
```bash
cd backend
venv\Scripts\activate
python -m uvicorn app.main:app --reload
```
✅ Backend runs on http://127.0.0.1:8000

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```
✅ Frontend runs on http://localhost:5173

---

### Step 5: Test It!

1. Open browser to http://localhost:5173
2. Upload a short video (< 5 minutes recommended for first test)
3. Wait for processing
4. Search: "What is this video about?"
5. Click a result to jump to that moment!

---

## 🎬 What You Can Do

### Upload Video File
1. Click "Choose File"
2. Select MP4/MOV/AVI/MKV
3. Click "Upload & Index"
4. Wait 1-5 minutes

### Use YouTube URL
1. Copy YouTube URL
2. Paste in text field
3. Click "Analyze URL"
4. Small YouTube window opens
5. Search results control this window!

### Search Inside Videos
1. Type natural language: "machine learning explanation"
2. Press Enter
3. Click results to jump to exact moments

### Get PDF Notes
1. Click "Download Notes (PDF)"
2. Get summary, keywords, full transcript, and screenshots

---

## ⚡ Quick Troubleshooting

**"FFmpeg not found"**
→ Install FFmpeg and restart terminal

**"Port already in use"**
→ Close other apps on ports 8000 or 5173

**"Module not found"**
→ Make sure virtual environment is activated

**"Out of memory"**
→ Use shorter videos (< 10 minutes)

**"YouTube download failed"**
→ Check video is public, try different video

---

## 💡 Pro Tips

1. **First time?** Use a 2-3 minute video for testing
2. **Processing time:** ~30 seconds per minute of video
3. **Best search:** Use natural language, not keywords
4. **Multiple videos:** Each video is indexed separately
5. **PDF notes:** Generated automatically during processing

---

## 📁 What Gets Created

After first video upload, you'll see:
```
backend/
├── uploads/        # Your uploaded videos
├── processed/      # Frame images and PDFs
├── temp/           # Temporary audio files
└── indexes/        # AI embeddings (saved automatically!)
```

---

## 🎯 Example Searches That Work Well

- "What is machine learning?"
- "Explain the conclusion"
- "Show me the funny part"
- "When does he mention statistics?"
- "Introduction section"
- "Main argument"
- "Key takeaway"

---

## ✅ Verification Checklist

Before reporting issues, verify:
- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] FFmpeg installed and in PATH
- [ ] Virtual environment activated
- [ ] Both backend and frontend running
- [ ] No firewall blocking ports 8000/5173

---

## 🆘 Still Having Issues?

1. Check terminal for error messages
2. Read SETUP.md for detailed guide
3. Check CHANGES.md for known issues
4. Verify all prerequisites installed

---

## 🎉 You're Ready!

Now go upload some videos and start searching! 

The first video upload will download AI models (~570MB), so be patient. After that, it's fast!

---

**Need more help?** See SETUP.md for detailed instructions.
