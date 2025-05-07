from flask import Blueprint, render_template, request, redirect, url_for, session
from pathlib import Path
import json, datetime, uuid

checkout_bp = Blueprint("checkout_bp", __name__, url_prefix="/checkout")
CATALOG_DB = Path("data/furniture_catalog.json")
USERS_DB = Path("data/users.json")

def load_catalog():
    return json.loads(CATALOG_DB.read_text()) if CATALOG_DB.exists() else []

def load_users():
    return json.loads(USERS_DB.read_text()) if USERS_DB.exists() else []

def get_user_full_name(username):
    users = load_users()
    user = next((u for u in users if u["username"] == username), None)
    if user:
        return f"{user['first_name']} {user['last_name']}"
    return "Unknown User"

@checkout_bp.route("/", methods=["GET"])
def checkout():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))

    item_id = request.args.get("item_id")
    item = next((f for f in load_catalog() if f["id"] == item_id), None)

    full_name = get_user_full_name(session["username"])

    return render_template("checkout.html", item=item, buyer_name=full_name)

@checkout_bp.route("/confirm", methods=["POST"])
def confirm():
    if not session.get("username"):
        return redirect(url_for("auth_bp.login"))

    name = request.form.get("name")
    item_id = request.form.get("item_id")
    catalog = load_catalog()
    item = next((i for i in catalog if i["id"] == item_id), None)

    order_id = "ORD-" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + str(uuid.uuid4())[:6].upper()

    return render_template(
        "checkout_confirm.html",
        buyer=name,
        item=item,
        order_id=order_id,
        timestamp=datetime.datetime.now()
    )
