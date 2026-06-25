
import os
import json
from flask import Blueprint, request, session, jsonify, redirect, url_for

from services.transcription import transcribe
from services.media import convert_video_to_audio, get_duration
from database.db import get_db

upload = Blueprint("upload", __name__)

UPLOAD_FOLDER  = "project/uploads"
ALLOWED_AUDIO  = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
ALLOWED_VIDEO  = {".mp4", ".mkv", ".mov", ".avi", ".webm"}
ALLOWED_ALL    = ALLOWED_AUDIO | ALLOWED_VIDEO


@upload.route("/upload", methods=["POST"])
def upload_file():
    if "user" not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]
    if not file or file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_ALL:
        return jsonify({"error": f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_ALL))}"}), 400

    # Save uploaded file
    safe_name = file.filename.replace(" ", "_")
    filepath  = os.path.join(UPLOAD_FOLDER, safe_name)
    file.save(filepath)

    # Get duration
    duration = get_duration(filepath)

    # Convert video → audio if needed
    if ext in ALLOWED_VIDEO:
        try:
            filepath = convert_video_to_audio(filepath)
        except Exception as e:
            return jsonify({"error": f"Video conversion failed: {str(e)}"}), 500

    # Transcribe
    try:
        transcript = transcribe(filepath)
    except Exception as e:
        return jsonify({"error": f"Transcription failed: {str(e)}"}), 500

    # Persist to history (no summary yet)
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute(
            "INSERT INTO history(email, filename, transcript) VALUES(?, ?, ?)",
            (session["user"], safe_name, transcript)
        )
        db.commit()
        db.close()
    except Exception:
        pass  # Non-fatal

    return jsonify({
        "duration":   round(duration / 60, 2),
        "filename":   safe_name,
        "transcript": transcript
    })
