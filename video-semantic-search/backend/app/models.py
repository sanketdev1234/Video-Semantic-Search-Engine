from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class UploadResponse(BaseModel):
    video_id: str
    filename: str
    status: ProcessingStatus
    message: str

class SearchResult(BaseModel):
    video_id: str
    timestamp: float
    text: Optional[str] = None
    score: float
    source: str
    deep_link: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int

class UrlUploadRequest(BaseModel):
    url: str

class VideoMetadata(BaseModel):
    video_id: str
    filename: str
    source: str
    url: Optional[str] = None
    duration: Optional[float] = None
