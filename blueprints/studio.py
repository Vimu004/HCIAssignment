from flask import Blueprint, render_template, redirect, url_for, session

# === Flask Blueprint ===
studio_bp = Blueprint("studio_bp", __name__, url_prefix="/studio")

# === Route: Studio Main Page ===
@studio_bp.route("/", methods=["GET"])
def studio():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))
    return render_template("studio.html")
