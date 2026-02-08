import os
import subprocess

def extract_frames(video_path: str, output_dir: str, interval=5):
    os.makedirs(output_dir, exist_ok=True)

    cmd = [
        "ffmpeg",
        "-y",
        "-i", video_path,
        "-vf", f"fps=1/{interval}",
        f"{output_dir}/frame_%04d.jpg"
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
