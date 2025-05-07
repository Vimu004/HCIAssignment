from flask import Blueprint, render_template, request, jsonify
import os
import uuid

catalog_bp = Blueprint('catalog_bp', __name__, url_prefix='/furniture')

# Simulated in-memory furniture catalog (you can load this from a DB)
CATALOG_DIR = 'static/assets/uploads'
GENERATED_MODELS_DIR = 'furniture_models'

# Show furniture catalog
@catalog_bp.route('/catalog_selector')
def catalog_selector():
    catalog = []
    for filename in os.listdir(CATALOG_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            catalog.append({
                'id': str(uuid.uuid4()),  # Unique ID for frontend
                'name': filename,
                'image': f'/{CATALOG_DIR}/{filename}'
            })
    return render_template("catalog_selector.html", catalog=catalog)


# Generate or load 3D model from 2D image
@catalog_bp.route('/load_model', methods=['POST'])
def load_model():
    data = request.get_json()
    image_path = data.get('image_path')
    image_filename = os.path.basename(image_path)

    # Example of converting filename to .glb path
    model_filename = os.path.splitext(image_filename)[0] + '.glb'
    model_path = os.path.join(GENERATED_MODELS_DIR, model_filename)

    # 🔁 Fake model generation for now (in production, run your pipeline here)
    if not os.path.exists(model_path):
        # Simulate generation
        with open(model_path, 'w') as f:
            f.write('Mock GLB content')  # Replace with actual model export

    return jsonify({ "glb_path": f"/{model_path}" })
