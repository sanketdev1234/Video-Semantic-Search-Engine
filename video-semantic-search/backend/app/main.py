from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import uuid

from app.config import get_settings, setup_directories
from app.models import UploadResponse, SearchResponse, SearchResult, ProcessingStatus
from app.services.video import process_video
from app.services.search import semantic_search

settings = get_settings()

app = FastAPI(
    title="Video Semantic Search API",
    description="Search inside videos using semantic similarity",
    version="1.0.0",
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


@app.get("/")
def root():
    return {"message": "Video Semantic Search API running"}


@app.post("/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile):
    if not file.filename.endswith((".mp4", ".mov", ".avi")):
        raise HTTPException(status_code=400, detail="Unsupported video format")

    video_id = str(uuid.uuid4())
    save_path = os.path.join(settings.UPLOAD_DIR, f"{video_id}_{file.filename}")

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Process video (audio → transcript → embeddings)
    # try:
    #     process_video(video_id, save_path)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))
    try:
      process_video(video_id, save_path)
    except Exception as e:
      import traceback
      traceback.print_exc()   # 🔥 THIS SHOWS THE REAL ERROR
      raise HTTPException(status_code=500, detail=str(e))

    return UploadResponse(
        video_id=video_id,
        filename=file.filename,
        status=ProcessingStatus.COMPLETED,
        message="Video uploaded and indexed successfully",
    )


@app.get("/search", response_model=SearchResponse)
def search(query: str):
    results = semantic_search(query)

    formatted = [
        SearchResult(
            timestamp=r["timestamp"],
            text=r.get("text"),
            score=r.get("score"),
        )
        for r in results
    ]

    return SearchResponse(
        query=query,
        results=formatted,
        total_results=len(formatted),
    )
