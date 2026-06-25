
import subprocess
from moviepy.editor import VideoFileClip


def get_duration(filepath):
    """Return duration in seconds; 0 on failure."""
    try:
        clip = VideoFileClip(filepath)
        duration = clip.duration
        clip.close()
        return duration
    except Exception:
        return 0


def convert_video_to_audio(video_path):
    """Extract audio track from video as mp3."""
    audio_path = video_path + ".mp3"
    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",
        "-acodec", "mp3",
        audio_path
    ], check=True)
    return audio_path
