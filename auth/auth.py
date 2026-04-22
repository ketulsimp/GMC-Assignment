
from flask import Blueprint, redirect, request, render_template, session, current_app
import secrets, time, requests
from configuration.config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from database.db import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/auth/google/login")
def login():
    state = secrets.token_hex(16)
    session['oauth_state'] = state

    current_app.logger.info("Login Started!")

    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile https://www.googleapis.com/auth/content"
        "&access_type=offline"
        f"&state={state}"
        "&prompt=consent"
    )

    return redirect(url)


@auth_bp.route("/auth/google/callback")
def callback():
    if request.args.get("error") == "access_denied":
        current_app.logger.error("Access Denied, Login Failed!")
        return redirect("/?error=access_denied")

    code = request.args.get("code")
    state = request.args.get("state")

    if 'oauth_state' not in session:
        current_app.logger.error("Session lost!")
        return redirect("/?error=session_expired")

    if not code:
        current_app.logger.error("Missing Code!")
        return redirect("/?error=missing_code")

    if session.get("oauth_state") != state:
        current_app.logger.error("Invalid State")
        return redirect("/?error=invalid_state")

    session.pop("oauth_state", None)

    try:
        token_res = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "redirect_uri": REDIRECT_URI,
                "grant_type": "authorization_code",
            },
            timeout=5
        )
    except requests.exceptions.RequestException:
        current_app.logger.error("Network Error during token exchange!")
        return redirect("/?error=network_error")

    if token_res.status_code != 200:
        current_app.logger.error("OAuth Failed")
        return redirect("/?error=oauth_failed")

    token_data = token_res.json()

    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")
    expiry = time.time() + token_data.get("expires_in", 3600)

    if not access_token:
        return redirect("/?error=oauth_failed")

    try:
        user_res = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
    except requests.exceptions.RequestException:
        current_app.logger.error("Network Error during user fetch!")
        return redirect("/?error=network_error")

    if user_res.status_code != 200:
        return redirect("/?error=user_fetch_failed")

    user = user_res.json()

    if "email" not in user:
        return redirect("/?error=invalid_user")

    user_doc = db.users.find_one_and_update(
        {"email": user["email"]},
        {"$set": user},
        upsert=True,
        return_document=True
    )

    existing = db.oauth_tokens.find_one({"user_id": user_doc["_id"]})

    update_data = {
        "access_token": access_token,
        "expiry": expiry
    }

    if refresh_token:
        update_data["refresh_token"] = refresh_token
    elif existing and "refresh_token" in existing:
        pass
    else:
        current_app.logger.error("No refresh token received!")
        return redirect("/?error=missing_refresh_token")

    db.oauth_tokens.update_one(
        {"user_id": user_doc["_id"]},
        {"$set": update_data},
        upsert=True
    )

    current_app.logger.info("Login Successful! Token Stored.")

    session["user_email"] = user["email"]

    return redirect("/profile")
