from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
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


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class SearchResult(BaseModel):
    timestamp: float
    text: Optional[str] = None
    score: Optional[float] = None


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
