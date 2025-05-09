from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from pathlib import Path
import json, uuid, datetime, os
from utils.trellis_runner import generate_glb_with_trellis
from supabase import create_client, Client
from dotenv import load_dotenv
from PIL import Image
import io

# Load Supabase credentials
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BUCKET_NAME = "furniture"
BUCKET_URL = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}"

furniture_bp = Blueprint("furniture_bp", __name__, url_prefix="/furniture")

MODELS_DB = Path("data/models.json")
MODEL_FOLDER = Path("static/models")
MODEL_FOLDER.mkdir(parents=True, exist_ok=True)

def load_json(path): return json.loads(path.read_text()) if path.exists() else []
def save_json(path, data): path.write_text(json.dumps(data, indent=2))

# ---------- Catalog Viewer ----------
@furniture_bp.route("/", methods=["GET"])
def catalog():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))

    response = supabase.table("furniture_metadata").select("*").execute()
    catalog = [
        {**item, "image": f"{BUCKET_URL}/{item['image_url']}"}
        for item in (response.data or [])
    ]
    return render_template("furniture.html", catalog=catalog)

# ---------- Upload Furniture ----------
@furniture_bp.route("/upload_furniture", methods=["POST"])
def upload_furniture():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))

    image_file = request.files.get("image")
    name = request.form.get("name")

    if not image_file or not name:
        return redirect(url_for("furniture_bp.catalog"))

    image_id = str(uuid.uuid4())
    filename = f"{image_id}.jpg"

    # ✅ Resize image
    try:
        img = Image.open(image_file.stream).convert("RGB")
        img.thumbnail((1024, 1024))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        image_bytes = buffer.read()
    except Exception as e:
        return jsonify({"error": f"Image processing failed: {str(e)}"}), 500

    # ✅ Upload to Supabase
    supabase.storage.from_(BUCKET_NAME).upload(filename, image_bytes)

    # ✅ Store metadata
    supabase.table("furniture_metadata").insert({
        "id": image_id,
        "name": name,
        "image_url": filename,
        "model_path": None,
        "uploaded_by": session["username"],
        "uploaded_at": datetime.datetime.utcnow().isoformat()
    }).execute()

    return redirect(url_for("furniture_bp.catalog"))

# ---------- Generate or Load .glb ----------
@furniture_bp.route("/load_model", methods=["POST"])
def load_model():
    if not session.get("username"):
        return jsonify({"error": "unauthorized"}), 403

    data = request.get_json()
    item_id = data.get("id")
    if not item_id:
        return jsonify({"error": "Missing furniture ID"}), 400

    models = load_json(MODELS_DB)
    model_entry = next((m for m in models if m["image_id"] == item_id), None)

    if model_entry:
        return jsonify({"glb_path": f"/{model_entry['model_path']}"})

    response = supabase.table("furniture_metadata").select("*").eq("id", item_id).execute()
    if not response.data:
        return jsonify({"error": "Furniture item not found"}), 404

    item = response.data[0]
    image_url = item["image_url"]
    public_image_url = f"{BUCKET_URL}/{image_url}"

    try:
        glb_path = generate_glb_with_trellis(public_image_url)
    except Exception as e:
        return jsonify({"error": f"Trellis failed: {str(e)}"}), 500

    new_model = {
        "id": str(uuid.uuid4()),
        "image_id": item_id,
        "model_path": str(glb_path),
        "uploaded_by": session["username"],
        "uploaded_at": datetime.datetime.utcnow().isoformat()
    }
    models.append(new_model)
    save_json(MODELS_DB, models)

    return jsonify({"glb_path": f"/{glb_path}"})

# ---------- Catalog Selector ----------
@furniture_bp.route("/catalog_selector", methods=["GET"])
def catalog_selector():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))

    response = supabase.table("furniture_metadata").select("*").execute()
    catalog = [
        {**item, "image": f"{BUCKET_URL}/{item['image_url']}"}
        for item in (response.data or [])
    ]
    return render_template("catalog_selector.html", catalog=catalog)
