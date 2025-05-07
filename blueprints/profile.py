from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from pathlib import Path
import json

profile_bp = Blueprint("profile_bp", __name__, url_prefix="/profile")
USERS_DB = Path("data/users.json")

def load_users():
    with open(USERS_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_DB, "w") as f:
        json.dump(users, f, indent=2)

@profile_bp.route("/", methods=["GET", "POST"])
def profile():
    username = session.get("username")
    if not username:
        return redirect(url_for("auth_bp.login"))

    users = load_users()
    user = next((u for u in users if u["username"] == username), None)

    if not user:
        flash("User not found", "error")
        return redirect(url_for("auth_bp.logout"))

    if request.method == "POST":
        user["first_name"] = request.form.get("first_name", user["first_name"])
        user["last_name"] = request.form.get("last_name", user["last_name"])
        save_users(users)
        flash("Profile updated successfully", "success")
        return redirect(url_for("profile_bp.profile"))

    return render_template("profile.html", user=user)

@profile_bp.route("/theme", methods=["POST"])
def update_theme():
    username = session.get("username")
    if not username:
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json()
    theme = data.get("theme", "dark")

    users = load_users()
    for user in users:
        if user["username"] == username:
            user["theme"] = theme
            session["theme"] = theme
            break

    save_users(users)
    return jsonify({ "status": "ok" })
