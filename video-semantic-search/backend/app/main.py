from fastapi import FastAPI, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
import uuid

from app.config import get_settings, setup_directories
from app.models import (
    UploadResponse, 
    SearchResponse, 
    SearchResult, 
    ProcessingStatus,
    UrlUploadRequest
)
from app.services.video import process_video, process_audio_only
from app.services.search import semantic_search
from app.services.url_video import download_youtube_audio, get_youtube_info
from app.services.store import (
    add_video_metadata, 
    load_indexes, 
    save_indexes,
    get_video_metadata,
    stats
)

settings = get_settings()

app = FastAPI(
    title="Video Semantic Search API",
    description="Search inside videos using semantic similarity",
    version="2.0.0",
)

# CORS (allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup folders at startup
setup_directories()

# Load existing indexes
load_indexes()

# Mount static files for serving processed videos/PDFs
app.mount(
    "/processed",
    StaticFiles(directory=settings.PROCESSED_DIR),
    name="processed"
)


@app.get("/")
def root():
    """API health check"""
    return {
        "message": "Video Semantic Search API running",
        "version": "2.0.0",
        "stats": stats()
    }


@app.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile, background_tasks: BackgroundTasks):
    """Upload and process a video file"""
    
    # Validate file type
    if not file.filename.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported video format. Supported: MP4, MOV, AVI, MKV"
        )
    
    # Generate unique ID
    video_id = str(uuid.uuid4())
    save_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}_{file.filename}")
    
    # Save uploaded file
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File save failed: {str(e)}")
    
    # Store metadata
    add_video_metadata(video_id, file.filename, source="upload")
    
    # Process video in background
    try:
        process_video(video_id, save_path, source="upload")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
    
    return UploadResponse(
        video_id=video_id,
        filename=file.filename,
        status=ProcessingStatus.COMPLETED,
        message="Video uploaded and indexed successfully",
    )


@app.post("/upload-url")
async def upload_video_url(data: UrlUploadRequest, background_tasks: BackgroundTasks):
    """Process video from URL (YouTube, etc.)"""
    
    print(f"📥 URL received: {data.url}")
    
    # Validate URL
    if not data.url or not data.url.strip():
        raise HTTPException(status_code=400, detail="URL is required")
    
    # Check if it's a YouTube URL
    if "youtube.com" not in data.url and "youtu.be" not in data.url:
        raise HTTPException(
            status_code=400, 
            detail="Currently only YouTube URLs are supported"
        )
    
    video_id = str(uuid.uuid4())
    
    try:
        # Get video info
        info = get_youtube_info(data.url)
        print(f"📺 Video: {info['title']}")
        
        # Store metadata
        add_video_metadata(
            video_id, 
            info['title'], 
            source="url",
            url=data.url
        )
        
        # Download and process audio
        print(f"⬇️ Downloading audio...")
        audio_path = download_youtube_audio(data.url, video_id)
        
        if not os.path.exists(audio_path):
            raise RuntimeError("Audio download failed")
        
        print(f"🎤 Processing audio...")
        process_audio_only(video_id, audio_path)
        
        return {
            "video_id": video_id,
            "filename": info['title'],
            "status": ProcessingStatus.COMPLETED,
            "message": "YouTube video processed successfully",
            "url": data.url
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500, 
            detail=f"YouTube processing failed: {str(e)}"
        )


@app.get("/search", response_model=SearchResponse)
def search(query: str, video_id: str = None):
    """
    Search inside videos using semantic similarity
    
    Args:
        query: Search query text
        video_id: Optional - filter results to specific video
    """
    
    if not query or not query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        results = semantic_search(query, video_id=video_id)
        
        formatted = [
            SearchResult(
                video_id=r["video_id"],
                timestamp=r["timestamp"],
                text=r.get("text"),
                score=r.get("score"),
                source=r.get("source", "upload"),
                deep_link=r.get("deep_link")
            )
            for r in results
        ]
        
        return SearchResponse(
            query=query,
            results=formatted,
            total_results=len(formatted),
        )
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@app.get("/notes/{video_id}")
def get_notes(video_id: str):
    """Get PDF notes for a video"""
    
    pdf_path = os.path.join(settings.PROCESSED_DIR, video_id, "notes.pdf")
    
    if not os.path.exists(pdf_path):
        raise HTTPException(
            status_code=404, 
            detail="Notes not found. Video may not have been processed yet."
        )
    
    return {
        "video_id": video_id,
        "pdf_url": f"/processed/{video_id}/notes.pdf"
    }


@app.get("/video/{video_id}")
def get_video_info(video_id: str):
    """Get metadata for a specific video"""
    
    metadata = get_video_metadata(video_id)
    
    if not metadata:
        raise HTTPException(status_code=404, detail="Video not found")
    
    return metadata


@app.get("/stats")
def get_stats():
    """Get system statistics"""
    return stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
