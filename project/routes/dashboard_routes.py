
from flask import Blueprint, render_template, session, redirect, url_for, jsonify
from database.db import get_db

dash = Blueprint("dash", __name__)


@dash.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("auth.login"))
    return render_template("dashboard.html", user=session["user"])


@dash.route("/history")
def history():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    db  = get_db()
    cur = db.cursor()
    cur.execute(
        "SELECT id, filename, transcript, summary, created_at FROM history WHERE email=? ORDER BY id DESC LIMIT 20",
        (session["user"],)
    )
    rows = [dict(r) for r in cur.fetchall()]
    db.close()
    return jsonify({"history": rows})
