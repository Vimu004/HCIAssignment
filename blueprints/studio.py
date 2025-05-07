from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify, current_app
from pathlib import Path
import json, uuid, datetime
from utils.trellis_runner import generate_glb_with_trellis  

studio_bp = Blueprint("studio_bp", __name__, url_prefix="/studio")

CATALOG_DB = Path("data/furniture_catalog.json")
MODELS_DB = Path("data/models.json")
MODEL_FOLDER = Path("static/models")
CATALOG_FOLDER = Path("static/assets/catalog")

MODEL_FOLDER.mkdir(parents=True, exist_ok=True)
CATALOG_FOLDER.mkdir(parents=True, exist_ok=True)

def load_json(path):
    return json.loads(path.read_text()) if path.exists() else []

def save_json(path, data):
    path.write_text(json.dumps(data, indent=2))

@studio_bp.route("/", methods=["GET"])
def studio():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))
    return render_template("studio.html")

# 📦 JSON API to fetch catalog data
@studio_bp.route("/catalog_data", methods=["GET"])
def catalog_data():
    if not session.get("username"):
        return jsonify({ "error": "unauthorized" }), 403
    return jsonify(load_json(CATALOG_DB))

# 🔄 Load or Generate 3D Model
@studio_bp.route("/load_model/<item_id>", methods=["GET"])
def load_model(item_id):
    if not session.get("username"):
        return jsonify({ "error": "unauthorized" }), 403

    catalog = load_json(CATALOG_DB)
    models = load_json(MODELS_DB)

    item = next((c for c in catalog if c["id"] == item_id), None)
    if not item:
        return jsonify({ "error": "Furniture item not found" }), 404

    # ✅ Reuse model if already exists
    existing = next((m for m in models if m["image"].endswith(f"{item_id}.jpg")), None)
    if existing:
        return jsonify({ "glb_path": f"/{existing['model']}" })

    # 🧠 Safeguard image path
    image_path = Path(item["image"].lstrip("/"))
    if not image_path.exists():
        image_path = CATALOG_FOLDER / f"{item_id}.jpg"
    if not image_path.exists():
        return jsonify({ "error": "Catalog image not found" }), 404

    # 🔁 Generate .glb using Trellis
    try:
        glb_path = generate_glb_with_trellis(image_path)
    except Exception as e:
        return jsonify({ "error": f"Trellis generation failed: {str(e)}" }), 500

    new_entry = {
        "id": str(uuid.uuid4())[:8],
        "image": str(image_path),
        "model": str(glb_path),
        "uploaded_by": session["username"],
        "uploaded_at": datetime.datetime.now().isoformat()
    }

    models.append(new_entry)
    save_json(MODELS_DB, models)

    return jsonify({ "glb_path": f"/{glb_path}" })
