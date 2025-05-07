import os
import requests
import time
import uuid
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def generate_glb_with_trellis(image_path: Path) -> Path:
    api_key = os.getenv("PIAPI_KEY")
    if not api_key:
        raise Exception("PIAPI_KEY not found in environment variables.")
    
    headers = {"X-API-KEY": api_key}

    # 1. Create generation task
    with open(image_path, "rb") as f:
        files = {"image": f}
        res = requests.post("https://api.piapi.xyz/v1/trellis", headers=headers, files=files)

    if res.status_code != 200:
        raise Exception(f"Trellis API error: {res.text}")

    task_id = res.json().get("task_id")
    if not task_id:
        raise Exception("Trellis API did not return a task_id.")

    # 2. Poll until ready
    for _ in range(20):
        task_res = requests.get(f"https://api.piapi.xyz/v1/trellis/{task_id}", headers=headers)
        if task_res.status_code != 200:
            raise Exception("Failed to get Trellis task status.")

        data = task_res.json()
        if data.get("status") == "success":
            model_url = data.get("model_url")
            break
        time.sleep(1)
    else:
        raise Exception("Trellis model generation timed out.")

    # 3. Download .glb
    output_dir = Path("static/models")
    output_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid.uuid4()}.glb"
    output_path = output_dir / filename

    r = requests.get(model_url)
    with open(output_path, "wb") as f:
        f.write(r.content)

    return output_path
