from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from pathlib import Path
import json
import datetime

testing_bp = Blueprint("testing_bp", __name__, url_prefix="/testing")
TESTING_DB = Path("data/testing.json")

def load_feedback():
    if not TESTING_DB.exists():
        return []
    with open(TESTING_DB, "r") as f:
        return json.load(f)

def save_feedback(entries):
    with open(TESTING_DB, "w") as f:
        json.dump(entries, f, indent=2)

@testing_bp.route("/", methods=["GET"])
def show_form():
    return render_template("testing.html")

@testing_bp.route("/submit", methods=["POST"])
def submit_feedback():
    feedback = {
        "timestamp": datetime.datetime.now().isoformat(),
        "name": request.form.get("name", "").strip(),
        "email": request.form.get("email", "").strip(),
        "rating": int(request.form.get("rating", 3)),
        "liked": request.form.get("liked", "").strip(),
        "suggestions": request.form.get("suggestions", "").strip()
    }

    entries = load_feedback()
    entries.append(feedback)
    save_feedback(entries)

    flash("✅ Thank you for your feedback!", "success")
    return redirect(url_for("home_bp.home"))
