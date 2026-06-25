
from flask import Blueprint, request, session, jsonify
from services.summarization import summarize_long
from database.db import get_db

summ = Blueprint("summ", __name__)


@summ.route("/summarize", methods=["POST"])
def summarize():
    if "user" not in session:
        return jsonify({"error": "Unauthorized. Please log in."}), 401

    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No transcript text provided."}), 400

    try:
        summary = summarize_long(text)
    except Exception as e:
        return jsonify({"error": f"Summarization failed: {str(e)}"}), 500

    # Update most recent history row for this user with the summary
    try:
        db  = get_db()
        cur = db.cursor()
        cur.execute(
            """UPDATE history SET summary=?
               WHERE id=(SELECT MAX(id) FROM history WHERE email=? AND summary IS NULL)""",
            (summary, session["user"])
        )
        db.commit()
        db.close()
    except Exception:
        pass  # Non-fatal

    return jsonify({"summary": summary})
