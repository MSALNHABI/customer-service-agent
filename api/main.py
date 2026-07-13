from fastapi import FastAPI, HTTPException
import json
import re
from pathlib import Path

app = FastAPI(
    title="Nawader Coffee Backend API"
)

DATA_DIR = Path(__file__).parent / "data"


def load_json(filename):
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


orders = load_json("orders.json")
inventory = load_json("inventory.json")
vip_customers = load_json("vip_customers.json")


@app.get("/orders/{order_id}")
def get_order_status(order_id: str):

    if not re.fullmatch(r"\d{5}", order_id):
        raise HTTPException(
            status_code=400,
            detail="order_id must be a 5-digit number"
        )

    if order_id not in orders:
        return {
            "found": False,
            "message": "Order not found"
        }

    return orders[order_id]


@app.get("/inventory/{branch_name}/{item_name}")
def check_inventory(branch_name: str, item_name: str):

    if branch_name not in inventory:
        return {
            "found": False,
            "message": "Branch or item not found"
        }

    if item_name not in inventory[branch_name]:
        return {
            "found": False,
            "message": "Branch or item not found"
        }

    return inventory[branch_name][item_name]


@app.get("/vip/{phone_number}")
def verify_vip(phone_number: str):

    if not re.fullmatch(r"05\d{8}", phone_number):
        raise HTTPException(
            status_code=400,
            detail="phone_number must be 10 digits and start with 05"
        )

    if phone_number not in vip_customers:
        return {
            "found": False,
            "message": "Customer not in VIP database"
        }

    return vip_customers[phone_number]

@app.get("/recommendations/inventory/{item_name}")
def recommend_branches_for_item(item_name: str):

    available_branches = []

    for branch_name, items in inventory.items():
        if item_name in items:
            item_data = items[item_name]

            if item_data["in_stock"] is True:
                available_branches.append(
                    {
                        "branch_name": branch_name,
                        "quantity_remaining": item_data["quantity_remaining"]
                    }
                )

    if not available_branches:
        return {
            "found": False,
            "message": "Item not available in any branch"
        }

    return {
        "found": True,
        "item_name": item_name,
        "available_branches": available_branches
    }