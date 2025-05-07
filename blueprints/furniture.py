from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from pathlib import Path
import json, uuid, datetime
from utils.trellis_runner import generate_glb_with_trellis  # Your Trellis integration

furniture_bp = Blueprint("furniture_bp", __name__, url_prefix="/furniture")

# === Directories & DB paths ===
CATALOG_DB = Path("data/furniture_catalog.json")
MODELS_DB = Path("data/models.json")
CATALOG_FOLDER = Path("static/assets/catalog/")
UPLOAD_FOLDER = Path("static/assets/uploads/")
MODEL_FOLDER = Path("static/models/")

# === Ensure folders exist ===
CATALOG_FOLDER.mkdir(parents=True, exist_ok=True)
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
MODEL_FOLDER.mkdir(parents=True, exist_ok=True)

def load_json(file):
    return json.loads(file.read_text()) if file.exists() else []

def save_json(file, data):
    file.write_text(json.dumps(data, indent=2))

# ---------- Catalog Viewer (Upload Page) ----------
@furniture_bp.route("/", methods=["GET"])
def catalog():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))
    catalog = load_json(CATALOG_DB)
    return render_template("furniture.html", catalog=catalog)

# ---------- Upload New Furniture ----------
@furniture_bp.route("/upload_furniture", methods=["POST"])
def upload_furniture():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))

    if "image" not in request.files or "name" not in request.form:
        return redirect(url_for("furniture_bp.catalog"))

    image_file = request.files["image"]
    name = request.form["name"]
    image_id = str(uuid.uuid4())[:8]
    filename = f"{image_id}.jpg"
    save_path = CATALOG_FOLDER / filename
    image_file.save(save_path)

    catalog = load_json(CATALOG_DB)
    catalog.append({
        "id": image_id,
        "name": name,
        "image": f"/static/assets/catalog/{filename}",
        "uploaded_by": session["username"],
        "uploaded_at": datetime.datetime.now().isoformat()
    })
    save_json(CATALOG_DB, catalog)

    return redirect(url_for("furniture_bp.catalog"))

# ---------- Generate/Load Model from Catalog Image ----------
@furniture_bp.route("/load_model", methods=["POST"])
def load_model():
    if not session.get("username"):
        return jsonify({ "error": "unauthorized" }), 403

    data = request.get_json()
    if not data:
        return jsonify({ "error": "No data received" }), 400

    item_id = data.get("id")
    image_path = data.get("image_path", "").lstrip("/")

    if not item_id or not image_path:
        return jsonify({ "error": "Missing required fields" }), 400

    models = load_json(MODELS_DB)
    model_entry = next((m for m in models if m["image"].endswith(item_id + ".jpg")), None)

    if model_entry:
        return jsonify({ "glb_path": f"/{model_entry['model']}" })

    # If model not found, generate using Trellis
    src_path = Path(image_path)
    if not src_path.exists():
        src_path = Path("static/assets/catalog") / f"{item_id}.jpg"

    if not src_path.exists():
        return jsonify({ "error": "Image file not found" }), 404

    try:
        glb_path = generate_glb_with_trellis(src_path)
    except Exception as e:
        return jsonify({ "error": f"Trellis failed: {str(e)}" }), 500

    new_model = {
        "id": str(uuid.uuid4())[:8],
        "image": str(src_path),
        "model": str(glb_path),
        "uploaded_by": session["username"]
    }

    models.append(new_model)
    save_json(MODELS_DB, models)

    return jsonify({ "glb_path": f"/{glb_path}" })

# ---------- Catalog Selector for Studio Integration ----------
@furniture_bp.route("/catalog_selector", methods=["GET"])
def catalog_selector():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))

    catalog = load_json(CATALOG_DB)
    return render_template("catalog_selector.html", catalog=catalog)
