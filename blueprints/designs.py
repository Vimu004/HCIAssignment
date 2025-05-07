from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from pathlib import Path
import json, uuid, datetime

designs_bp = Blueprint("designs_bp", __name__, url_prefix="/designs")
DESIGNS_DB = Path("data/designs.json")

def load_designs():
    return json.loads(DESIGNS_DB.read_text()) if DESIGNS_DB.exists() else []

def save_designs(data):
    DESIGNS_DB.write_text(json.dumps(data, indent=2))

@designs_bp.route("/", methods=["GET"])
def designs():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))

    username = session["username"]
    all_designs = load_designs()
    user_designs = [d for d in all_designs if d["username"] == username]

    return render_template("designs.html", designs=user_designs)

@designs_bp.route("/save", methods=["POST"])
def save():
    if not session.get("username"):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json()
    if not data.get("design_name") or not data.get("furniture"):
        return jsonify({"error": "incomplete data"}), 400

    all_designs = load_designs()
    new_design = {
        "id": str(uuid.uuid4())[:8],
        "username": session["username"],
        "design_name": data["design_name"],
        "room_config": data.get("room_config", {}),
        "furniture": data["furniture"],
        "created_at": datetime.datetime.now().isoformat()
    }
    all_designs.append(new_design)
    save_designs(all_designs)
    return jsonify({ "status": "ok", "design_id": new_design["id"] })

@designs_bp.route("/load/<design_id>", methods=["GET"])
def load(design_id):
    if not session.get("username"):
        return jsonify({"error": "unauthorized"}), 403

    all_designs = load_designs()
    design = next((d for d in all_designs if d["id"] == design_id and d["username"] == session["username"]), None)
    if not design:
        return jsonify({ "error": "not found" }), 404

    return jsonify(design)
