import re

import requests


BASE_URL = "http://127.0.0.1:8000"


def normalize_phone_number(phone_number: str) -> str:
    """
    Remove spaces and non-numeric characters from the phone number.
    """

    return "".join(
        character
        for character in phone_number
        if character.isdigit()
    )


def mask_phone_number(phone_number: str) -> str:
    """
    Hide most digits before displaying the number in the interface.
    """

    if len(phone_number) != 10:
        return phone_number

    return f"{phone_number[:2]}******{phone_number[-2:]}"


def get_customer_profile(phone_number: str) -> dict:
    """
    Validate the customer's Saudi phone number and retrieve their
    membership profile through the FastAPI VIP endpoint.

    Unknown valid numbers are treated as new customers.
    """

    normalized_phone = normalize_phone_number(phone_number)

    if not re.fullmatch(r"05\d{8}", normalized_phone):
        return {
            "success": False,
            "error": (
                "رقم الجوال يجب أن يتكون من 10 أرقام "
                "ويبدأ بـ 05."
            ),
        }

    try:
        response = requests.get(
            f"{BASE_URL}/vip/{normalized_phone}",
            timeout=10,
        )

        if response.status_code == 400:
            error_data = response.json()

            return {
                "success": False,
                "error": error_data.get(
                    "detail",
                    "رقم الجوال غير صحيح.",
                ),
            }

        response.raise_for_status()
        customer_data = response.json()

    except requests.ConnectionError:
        return {
            "success": False,
            "error": (
                "تعذر الاتصال بخادم Nawader Coffee. "
                "تأكد أن FastAPI يعمل."
            ),
        }

    except requests.Timeout:
        return {
            "success": False,
            "error": "انتهت مهلة الاتصال بالخادم.",
        }

    except requests.RequestException as error:
        return {
            "success": False,
            "error": f"حدث خطأ أثناء التحقق من العميل: {error}",
        }

    # A valid number that does not exist in the VIP database
    if customer_data.get("found") is False:
        return {
            "success": True,
            "phone_number": normalized_phone,
            "masked_phone": mask_phone_number(normalized_phone),
            "registered": False,
            "customer_type": "new",
            "is_vip": False,
            "loyalty_points": 0,
            "free_drink_eligible": False,
        }

    is_vip = customer_data.get("is_vip", False)

    return {
        "success": True,
        "phone_number": normalized_phone,
        "masked_phone": mask_phone_number(normalized_phone),
        "registered": True,
        "customer_type": "vip" if is_vip else "regular",
        "is_vip": is_vip,
        "loyalty_points": customer_data.get("loyalty_points", 0),
        "free_drink_eligible": customer_data.get(
            "free_drink_eligible",
            False,
        ),
    }