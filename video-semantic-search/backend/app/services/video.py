import subprocess
import os
import whisper
from sentence_transformers import SentenceTransformer
from app.config import get_settings
from app.services.store import add_embedding
from PIL import Image

settings = get_settings()

# Load models ONCE
whisper_model = whisper.load_model(settings.WHISPER_MODEL)
text_embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
clip_embedder = SentenceTransformer("clip-ViT-B-32")


def extract_audio(video_path: str) -> str:
    audio_path = os.path.join(settings.TEMP_DIR, "audio.wav")

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-ac", "1",
        "-ar", "16000",
        audio_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return audio_path


def extract_frames(video_path: str, output_dir: str, interval=5):
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"fps=1/{interval}",
        f"{output_dir}/frame_%04d.jpg"
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return sorted(os.listdir(output_dir))


def embed_frame(image_path: str):
    image = Image.open(image_path).convert("RGB")
    return clip_embedder.encode(image)


def process_video(video_id: str, video_path: str):
    """
    MULTIMODAL processing:
    - Audio → Whisper → embeddings
    - Frames → CLIP → embeddings
    """

    # -------- AUDIO PIPELINE --------
    audio_path = extract_audio(video_path)
    # result = whisper_model.transcribe(audio_path)
    result = whisper_model.transcribe(
     audio_path,
     fp16=False,
     verbose=False
    )

    for segment in result["segments"]:
        text = segment["text"].strip()
        timestamp = segment["start"]

        if text:
            embedding = text_embedder.encode(text)
            add_embedding(video_id, embedding, timestamp, text)

    # -------- VISUAL PIPELINE --------
    frames_dir = os.path.join(settings.PROCESSED_DIR, video_id)
    # frames = extract_frames(video_path, frames_dir, interval=5)
    frames = extract_frames(video_path, frames_dir, interval=10)
    frames = frames[:10]   # 🔥 LIMIT FRAMES FOR MVP

    for i, frame_name in enumerate(frames):
        frame_path = os.path.join(frames_dir, frame_name)
        timestamp = i * 5  # approx timestamp

        embedding = embed_frame(frame_path)
        add_embedding(video_id, embedding, timestamp, "visual_frame")
