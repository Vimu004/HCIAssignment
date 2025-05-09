from flask import Blueprint, render_template, redirect, url_for, session

studio_bp = Blueprint("studio_bp", __name__, url_prefix="/studio")

@studio_bp.route("/", methods=["GET"])
def studio():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))
    return render_template("studio.html")
