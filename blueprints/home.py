from flask import Blueprint, render_template, redirect, url_for, session
from pathlib import Path
import json

home_bp = Blueprint("home_bp", __name__, url_prefix="/home")

USERS_DB = Path("data/users.json")

def load_users():
    with open(USERS_DB, "r") as f:
        return json.load(f)

@home_bp.route("/")
def home():
    username = session.get("username")
    if not username:
        return redirect(url_for("auth_bp.login"))

    users = load_users()
    user = next((u for u in users if u["username"] == username), None)

    if not user:
        return redirect(url_for("auth_bp.logout"))

    return render_template("home.html", user=user)
