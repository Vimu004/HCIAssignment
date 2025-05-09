import os
import time
import uuid
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.piapi.ai/api/v1"
API_KEY = os.getenv("PIAPI_KEY")
HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}

def generate_glb_with_trellis(image_url: str, poll_interval=2, max_retries=30) -> Path:
    if not API_KEY:
        raise Exception("Missing PIAPI_KEY in environment variables")

    # ✅ FIX: Use only "image", not "images"
    payload = {
        "model": "Qubico/trellis",
        "task_type": "image-to-3d",
        "input": {
            "image": image_url,  # Must be public and direct JPG/PNG
            "ss_sampling_steps": 50,
            "slat_sampling_steps": 50,
            "ss_guidance_strength": 7.5,
            "slat_guidance_strength": 3.0,
            "seed": 0,
            "texture_size": 1024
        }
    }

    print("📤 Sending request to Trellis...")
    try:
        res = requests.post(f"{BASE_URL}/task", json=payload, headers=HEADERS, timeout=10)
        res.raise_for_status()
        task_id = res.json().get("data", {}).get("task_id") or res.json().get("id")
        if not task_id:
            raise Exception("No task_id returned from Trellis API")
    except Exception as e:
        raise Exception(f"Trellis task creation failed: {str(e)}")

    # Polling for task completion
    print("⏳ Polling Trellis for model status...")
    for _ in range(max_retries):
        try:
            task_res = requests.get(f"{BASE_URL}/task/{task_id}", headers=HEADERS, timeout=10)
            task_data = task_res.json().get("data", {})
            status = task_data.get("status", "")
            if status.lower() == "completed":
                model_url = task_data.get("output", {}).get("model_file")
                if not model_url:
                    raise Exception("Model generated but no model_file found")
                break
            elif status.lower() == "failed":
                raise Exception("Trellis generation failed")
        except Exception as e:
            raise Exception(f"Trellis polling failed: {str(e)}")
        time.sleep(poll_interval)
    else:
        raise Exception("Trellis model generation timed out")

    # Download .glb
    output_dir = Path("static/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.glb"
    output_path = output_dir / filename

    try:
        r = requests.get(model_url, timeout=20)
        r.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(r.content)
    except Exception as e:
        raise Exception(f"Failed to download .glb file: {str(e)}")

    return output_path
