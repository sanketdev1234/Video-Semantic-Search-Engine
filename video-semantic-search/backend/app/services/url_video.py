import yt_dlp
import os
from app.config import get_settings

settings = get_settings()


def download_youtube_audio(url: str, video_id: str) -> str:
    """Download audio from YouTube URL using yt-dlp"""
    
    output_path = os.path.join(settings.TEMP_DIR, f"{video_id}_audio.wav")
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(settings.TEMP_DIR, f"{video_id}_temp.%(ext)s"),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ar', '16000',
            '-ac', '1',
        ],
        'keepvideo': False,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # yt-dlp saves with the new extension
            temp_file = os.path.join(settings.TEMP_DIR, f"{video_id}_temp.wav")
            
            # Rename to expected output
            if os.path.exists(temp_file):
                if os.path.exists(output_path):
                    os.remove(output_path)
                os.rename(temp_file, output_path)
            
            return output_path
            
    except Exception as e:
        raise RuntimeError(f"Failed to download YouTube audio: {str(e)}")


def get_youtube_info(url: str) -> dict:
    """Get video information from YouTube URL"""
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title', 'Unknown'),
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
            }
    except Exception as e:
        print(f"⚠️ Could not fetch video info: {e}")
        return {
            'title': 'Unknown Video',
            'duration': 0,
            'thumbnail': ''
        }
