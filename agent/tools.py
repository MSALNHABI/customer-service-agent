from langchain.tools import tool
from datetime import datetime, time
from zoneinfo import ZoneInfo
from urllib.parse import quote
import requests

BASE_URL = "http://127.0.0.1:8000"

@tool
def check_order_status(order_id: str) -> str:
    """
    Use this tool when a customer asks about
    the status of an order.

    Input should be a 5-digit order ID.
    """

    response = requests.get(
        f"{BASE_URL}/orders/{order_id}"
    )

    return str(response.json())


@tool
def check_inventory(
    branch_name: str,
    item_name: str
) -> str:
    """
    Use this tool when a customer asks whether
    a menu item is available in a specific branch.

    Inputs:
    - branch_name
    - item_name
    """

    response = requests.get(
        f"{BASE_URL}/inventory/{branch_name}/{item_name}"
    )

    return str(response.json())


@tool
def verify_vip(phone_number: str) -> str:
    """
    Use this tool when a customer wants to check:

    - VIP membership
    - loyalty points
    - free drink eligibility

    Input should be a Saudi mobile number.
    """

    response = requests.get(
        f"{BASE_URL}/vip/{phone_number}"
    )

    return str(response.json())

@tool
def check_branch_open_now(branch_name: str) -> str:
    """
    Use this tool when a customer asks whether a specific Nawader Coffee branch
    is currently open right now.

    Input should be the branch name, for example:
    - Hittin
    - Al-Malqa
    - Riyadh Front
    - Al-Zahra
    - Jeddah Yacht Club

    This tool checks the current Saudi Arabia time and compares it with
    Nawader Coffee official opening hours.
    """

    saudi_time = datetime.now(ZoneInfo("Asia/Riyadh"))
    current_time = saudi_time.time()
    weekday = saudi_time.weekday()

    # Python weekday:
    # Monday = 0, Tuesday = 1, ..., Sunday = 6
    # Friday = 4

    if weekday == 4:
        opening_time = time(16, 0)
        closing_time = time(2, 0)
        schedule = "Friday: 4:00 PM - 2:00 AM"
    else:
        opening_time = time(6, 0)
        closing_time = time(1, 0)
        schedule = "Saturday to Thursday: 6:00 AM - 1:00 AM"

    # Handles closing after midnight
    if closing_time < opening_time:
        is_open = current_time >= opening_time or current_time <= closing_time
    else:
        is_open = opening_time <= current_time <= closing_time

    return str({
        "branch_name": branch_name,
        "is_open_now": is_open,
        "current_saudi_time": saudi_time.strftime("%Y-%m-%d %H:%M"),
        "official_hours": schedule
    })

@tool
def find_product_in_other_branches(item_name: str) -> str:
    """
    Use this tool when a customer asks about a product that is not available
    in a specific branch, or when you need to recommend other branches that
    have the product in stock.

    Input should be the English inventory item name, for example:
    - Saffron Cake
    - Spanish Latte
    - Iced Matcha
    - Cold Brew
    - Flat White
    """

    encoded_item = quote(item_name)

    response = requests.get(
        f"{BASE_URL}/recommendations/inventory/{encoded_item}"
    )

    return str(response.json())