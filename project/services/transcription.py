
import whisper

print("Loading Whisper model (small)...")
model = whisper.load_model("small")
print("✓ Whisper loaded")


def transcribe(filepath):
    """Transcribe audio/video file to text using Whisper."""
    result = model.transcribe(filepath)
    return result["text"].strip()
