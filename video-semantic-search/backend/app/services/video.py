import subprocess
import os
import whisper
from sentence_transformers import SentenceTransformer
from app.config import get_settings
from app.services.store import add_embedding, save_indexes
from app.services.pdf_builder import build_pdf
from app.services.summarizer import summarize
from app.services.keywords import extract_key_concepts
from app.services.notes_generator import format_transcript
from PIL import Image
import shutil

settings = get_settings()

# Load models ONCE (CPU optimized)
print("🔄 Loading AI models (CPU mode)...")
whisper_model = whisper.load_model(settings.WHISPER_MODEL, device="cpu")
text_embedder = SentenceTransformer(settings.EMBEDDING_MODEL, device="cpu")
clip_embedder = SentenceTransformer("clip-ViT-B-32", device="cpu")
print("✅ Models loaded successfully")


def check_ffmpeg_exists():
    """Check if ffmpeg is installed and accessible"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], 
            capture_output=True, 
            timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"FFmpeg check error: {e}")
        return False


def extract_audio(video_path: str, output_path: str = None) -> str:
    """Extract audio from video file using ffmpeg"""
    
    if not check_ffmpeg_exists():
        raise RuntimeError(
            "FFmpeg not found! Please install FFmpeg:\n"
            "Windows: Download from https://ffmpeg.org/download.html and add to PATH\n"
            "Or use: winget install FFmpeg"
        )
    
    if output_path is None:
        output_path = os.path.join(settings.TEMP_DIR, "audio.wav")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-ac", "1",
        "-ar", "16000",
        "-vn",  # No video
        output_path
    ]
    
    try:
        # Windows-specific: hide console window
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300,
            startupinfo=startupinfo
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        if not os.path.exists(output_path):
            raise RuntimeError("Audio extraction failed: output file not created")
        
        return output_path
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg audio extraction timed out (>5 minutes)")
    except Exception as e:
        raise RuntimeError(f"Audio extraction error: {str(e)}")


def extract_frames(video_path: str, output_dir: str, interval=10, max_frames=10):
    """Extract frames from video file using ffmpeg"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    if not check_ffmpeg_exists():
        raise RuntimeError(
            "FFmpeg not found! Please install FFmpeg:\n"
            "Windows: Download from https://ffmpeg.org/download.html and add to PATH"
        )
    
    # Extract frames efficiently (1 frame every N seconds)
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"fps=1/{interval}",
        "-frames:v", str(max_frames),  # Limit frames during extraction
        f"{output_dir}/frame_%04d.jpg"
    ]
    
    try:
        # Windows-specific: hide console window
        startupinfo = None
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=300,
            startupinfo=startupinfo
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg failed: {result.stderr}")
        
        frames = sorted([f for f in os.listdir(output_dir) if f.endswith('.jpg')])
        return frames
        
    except subprocess.TimeoutExpired:
        raise RuntimeError("FFmpeg frame extraction timed out (>5 minutes)")
    except Exception as e:
        raise RuntimeError(f"Frame extraction error: {str(e)}")


def embed_frame(image_path: str):
    """Generate CLIP embedding for image frame"""
    try:
        image = Image.open(image_path).convert("RGB")
        return clip_embedder.encode(image)
    except Exception as e:
        print(f"⚠️ Failed to embed frame {image_path}: {e}")
        return None


def process_video(video_id: str, video_path: str, source: str = "upload"):
    """
    MULTIMODAL processing:
    - Audio → Whisper → embeddings
    - Frames → CLIP → embeddings
    - Generate PDF notes
    """
    
    print(f"🔄 Processing video {video_id}...")
    
    # -------- AUDIO PIPELINE --------
    try:
        print("  📢 Extracting audio...")
        audio_path = extract_audio(video_path)
        
        print("  🎤 Transcribing with Whisper (CPU)...")
        result = whisper_model.transcribe(
            audio_path,
            fp16=False,  # Must be False for CPU
            verbose=False,
            language='en'  # Specify language for faster processing
        )
        
        segments = result.get("segments", [])
        transcript_lines = format_transcript(segments)
        
        # Extract full text for summarization
        full_text = " ".join([seg["text"] for seg in segments])
        
        print(f"  💾 Indexing {len(segments)} text segments...")
        for segment in segments:
            text = segment["text"].strip()
            timestamp = segment["start"]
            
            if text:
                embedding = text_embedder.encode(text)
                add_embedding(video_id, embedding, timestamp, text, modality="text")
        
        # Clean up temp audio
        try:
            os.remove(audio_path)
        except:
            pass
            
    except Exception as e:
        print(f"❌ Audio processing failed: {e}")
        raise
    
    # -------- VISUAL PIPELINE --------
    try:
        print("  🎬 Extracting frames...")
        frames_dir = os.path.join(settings.PROCESSED_DIR, video_id)
        frames = extract_frames(
            video_path, 
            frames_dir, 
            interval=settings.FRAME_INTERVAL_SECONDS,
            max_frames=settings.MAX_FRAMES
        )
        
        print(f"  🖼️ Indexing {len(frames)} visual frames...")
        frame_image_paths = []
        for i, frame_name in enumerate(frames):
            frame_path = os.path.join(frames_dir, frame_name)
            timestamp = i * settings.FRAME_INTERVAL_SECONDS
            
            embedding = embed_frame(frame_path)
            if embedding is not None:
                add_embedding(video_id, embedding, timestamp, "visual_frame", modality="visual")
                frame_image_paths.append(frame_path)
        
    except Exception as e:
        print(f"⚠️ Visual processing failed (continuing anyway): {e}")
        frame_image_paths = []
    
    # -------- GENERATE NOTES --------
    try:
        print("  📝 Generating PDF notes...")
        summary = summarize(full_text, top_k=3)
        keywords = extract_key_concepts(full_text, top_k=8)
        
        pdf_path = os.path.join(frames_dir, "notes.pdf")
        build_pdf(pdf_path, summary, keywords, transcript_lines, frame_image_paths)
        
        print(f"✅ PDF notes generated: {pdf_path}")
        
    except Exception as e:
        print(f"⚠️ PDF generation failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Save all indexes
    save_indexes()
    print(f"✅ Video {video_id} processed successfully!")


def process_audio_only(video_id: str, audio_path: str):
    """Process audio file directly (for YouTube URLs)"""
    
    print(f"🔄 Processing audio for {video_id}...")
    
    try:
        print("  🎤 Transcribing with Whisper (CPU)...")
        result = whisper_model.transcribe(
            audio_path,
            fp16=False,
            verbose=False,
            language='en'
        )
        
        segments = result.get("segments", [])
        full_text = " ".join([seg["text"] for seg in segments])
        
        print(f"  💾 Indexing {len(segments)} text segments...")
        for segment in segments:
            text = segment["text"].strip()
            timestamp = segment["start"]
            
            if text:
                embedding = text_embedder.encode(text)
                add_embedding(video_id, embedding, timestamp, text, modality="text")
        
        # Clean up temp audio
        try:
            os.remove(audio_path)
        except:
            pass
        
        save_indexes()
        print(f"✅ Audio processed successfully!")
        
        return full_text, segments
        
    except Exception as e:
        print(f"❌ Audio processing failed: {e}")
        raise
