from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import hashlib, uuid, json
from pathlib import Path

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/auth")
USERS_DB = Path("data/users.json")

def load_users():
    if not USERS_DB.exists():
        return []
    with open(USERS_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_DB, "w") as f:
        json.dump(users, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def get_user_by_username(username):
    return next((u for u in load_users() if u["username"] == username.lower()), None)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username").lower()
        password = request.form.get("password")

        user = get_user_by_username(username)
        if user and user["password"] == hash_password(password):
            session["username"] = user["username"]
            session["theme"] = user.get("theme", "dark")
            flash("Login successful!", "success")
            return redirect(url_for("home_bp.home"))

        flash("Invalid username or password.", "error")
    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").lower()
        fname = request.form.get("first_name")
        lname = request.form.get("last_name")
        email = request.form.get("email").lower()
        password = request.form.get("password")
        confirm = request.form.get("confirm")

        users = load_users()

        if any(u["username"] == username for u in users):
            flash("Username already exists.", "error")
            return redirect(url_for("auth_bp.register"))

        if any(u["email"] == email for u in users):
            flash("Email already registered.", "error")
            return redirect(url_for("auth_bp.register"))

        if password != confirm:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth_bp.register"))

        users.append({
            "id": str(uuid.uuid4())[:8],
            "first_name": fname,
            "last_name": lname,
            "username": username,
            "email": email,
            "password": hash_password(password),
            "theme": "dark"
        })

        save_users(users)
        session["username"] = username
        session["theme"] = "dark"
        flash("Account created successfully!", "success")
        return redirect(url_for("home_bp.home"))

    return render_template("register.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("auth_bp.login"))

@auth_bp.route("/restore", methods=["GET", "POST"])
def restore():
    if request.method == "POST":
        flash("Password reset link sent (mock).", "info")
        return redirect(url_for("auth_bp.login"))
    return render_template("restore.html")
