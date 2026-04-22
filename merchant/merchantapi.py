

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
        return render_template("merchant_accounts.html", accounts=[], error="Network error reaching Merchant API")

    if response.status_code == 401:
        logger.error("Unauthorized")
        return render_template("merchant_accounts.html", accounts=[], error="Unauthorized")

    if response.status_code == 403:
        logger.error("Access Forbidden")
        return render_template("merchant_accounts.html", accounts=[], error="Access forbidden")

    if response.status_code != 200:
        logger.error("Failed to fetch merchant accounts")
        return render_template("merchant_accounts.html", accounts=[], error="Failed to fetch merchant accounts")

    data = response.json()

    accounts_data = data.get("accounts", [])

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

    logger.info(f"Added {len(accounts)} merchant accounts of the user to the database")

    return render_template("merchant_accounts.html", accounts=accounts, error=None)


@merchant_bp.route("/merchant/change-account")
def change_google_account():
    session.clear()
    return redirect("/auth/google/login")





