from flask import Blueprint, session, request, redirect, render_template
from database.db import db
from auth.utils import get_valid_token
import requests
import logging

merchant_bp = Blueprint("merchant", __name__)

logger = logging.getLogger(__name__)


@merchant_bp.route("/merchant/accounts")
def get_merchant_accounts():
    email = session.get("user_email")
    if not email:
        return redirect("/?error=not_logged_in")

    user_doc = db.users.find_one({"email": email})
    if not user_doc:
        return redirect("/?error=not_logged_in")

    access_token = get_valid_token(user_doc["_id"]) 

    try:
        response = requests.get(
            "https://merchantapi.googleapis.com/accounts/v1/accounts",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            },
            timeout=5
        )
    except requests.exceptions.RequestException:
        logger.error("Network error calling Merchant API")
        logger.error("Network error in Merchant API")
        return render_template("merchant_accounts.html", accounts=[], error="Network error in Merchant API", active_merchant_id=None)

    if response.status_code == 401:
        logger.error("Unauthorized person")
        return render_template("merchant_accounts.html", accounts=[], error="Unauthorized", active_merchant_id=None)

    if response.status_code == 403:
        logger.error("Access Forbidden")
        return render_template("merchant_accounts.html", accounts=[], error="Access forbidden", active_merchant_id=None)

    if response.status_code != 200:
        logger.error("Failed to fetch merchant accounts")
        return render_template("merchant_accounts.html", accounts=[], error="Failed to fetch merchant accounts", active_merchant_id=None)

    data = response.json()
    # print(data)

    accounts_data = data.get("accounts", [])
    #return accounts_data

    for acc in accounts_data:
        merchant_id = acc.get("name", "").split("/")[-1]
        db.merchant_accounts.update_one(
            {
                "user_id": user_doc["_id"],
                "merchant_id": merchant_id
            },
            {
                "$set": {
                    "merchant_name": acc.get("accountName"),
                    "google_account_selected": user_doc.get("email"),
                }
            },
            upsert=True
        )

    accounts = [
        {
            "merchant_id": a["merchant_id"],
            "merchant_name": a.get("merchant_name", ""),
            "user_id": str(a["user_id"]),
            "google_account_selected": a.get("google_account_selected", ""),
        }
        for a in db.merchant_accounts.find(
            {"user_id": user_doc["_id"]},
            sort=[("_id", 1)]
        )
    ]

    active_doc = db.merchant_accounts.find_one(
        {"user_id": user_doc["_id"], "active_account": True}
    )

    if not active_doc and accounts:
        first_id = accounts[0]["merchant_id"]
        db.merchant_accounts.update_one(
            {"user_id": user_doc["_id"], "merchant_id": first_id},
            {"$set": {"active_account": True}}
        )
        active_merchant_id = first_id
    else:
        active_merchant_id = active_doc["merchant_id"] if active_doc else None

    logger.info(f"Saved {len(accounts)} merchant accounts for user, active: {active_merchant_id}")

    return render_template("merchant_accounts.html", accounts=accounts, error=None, active_merchant_id=active_merchant_id)


@merchant_bp.route("/merchant/accounts/select", methods=["POST"])
def select_merchant_account():
    email = session.get("user_email")
    if not email:
        return redirect("/?error=not_logged_in")

    user_doc = db.users.find_one({"email": email})
    if not user_doc:
        return redirect("/?error=not_logged_in")

    merchant_id = request.form.get("merchant_id")
    if not merchant_id:
        return redirect("/merchant/accounts")

    db.merchant_accounts.update_many(
        {"user_id": user_doc["_id"]},
        {"$set": {"active_account": False}}
    )

    db.merchant_accounts.update_one(
        {"user_id": user_doc["_id"], "merchant_id": merchant_id},
        {"$set": {"active_account": True}}
    )

    logger.info(f"Active merchant set to {merchant_id} for user {email}")

    return redirect("/merchant/accounts")


@merchant_bp.route("/merchant/change-account")
def change_google_account():
    session.clear()
    return redirect("/auth/google/login")

# @merchant_bp.route("/merchant/show/details")
# def post_request():
#     email = session.get("user_email")
#     user_doc= db.users.find_one({"email":email})
#     access_token = get_valid_token(user_doc["_id"])

#     response= requests.get(
#         "https://merchantapi.googleapis.com/accounts/v1/accounts",
#         headers={
#             "Authorization": f"Bearer {access_token}",
#             "Content-Type": "application/json"
#         },
#         timeout=5
#     )
#     data= response.json()
#     return data