
from flask import Blueprint, render_template, request, redirect, session, url_for
from database.db import get_db

auth = Blueprint("auth", __name__)


@auth.route("/", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dash.dashboard"))

    error = None
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            error = "Please fill in all fields."
        else:
            db  = get_db()
            cur = db.cursor()
            cur.execute(
                "SELECT * FROM users WHERE email=? AND password=?",
                (email, password)
            )
            user = cur.fetchone()
            db.close()

            if user:
                session["user"] = email
                return redirect(url_for("dash.dashboard"))
            else:
                error = "Invalid email or password."

    return render_template("login.html", error=error)


@auth.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            error = "Please fill in all fields."
        else:
            db  = get_db()
            cur = db.cursor()
            try:
                cur.execute(
                    "INSERT INTO users(email, password) VALUES(?, ?)",
                    (email, password)
                )
                db.commit()
                db.close()
                return redirect(url_for("auth.login"))
            except Exception:
                db.close()
                error = "An account with this email already exists."

    return render_template("register.html", error=error)


@auth.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
