from flask import Flask, redirect, request, render_template, session
from pymongo import MongoClient
import os, time
import requests
from dotenv import load_dotenv
import logging
import secrets

load_dotenv()

app = Flask(__name__)

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")
SECRET_KEY = os.getenv("SECRET_KEY")

app.secret_key = SECRET_KEY

client = MongoClient("mongodb://localhost:27017")
db = client["oauth_db"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app.logger.setLevel(logging.INFO)
logging.getLogger("google.auth.transport.requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("werkzeug").setLevel(logging.WARNING)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/auth/google/login")
def login():
    state = secrets.token_hex(16)
    session['oauth_state'] = state
    app.logger.info("Login Attempt!")
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


@app.route("/auth/google/callback")
def callback():
    if request.args.get("error") == "access_denied":
        app.logger.error("Access denined!")
        return "Login cancelled by user.", 400

    code = request.args.get("code")
    state = request.args.get("state")

    if not code:
        app.logger.error("Missing Auth code")
        return "Missing authorization code", 400

    if session.get('oauth_state') != state:
        app.logger.error("Invalid State!")
        return "Invalid state", 400

    session.pop('oauth_state', None)

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
        return "Token request failed", 500

    if token_res.status_code != 200:
        app.logger.error("Token exchange failed")
        return "OAuth failed", 400

    token_data = token_res.json()

    if "access_token" not in token_data:
        app.logger.error("Access token missing in response")
        return "OAuth failed", 400

    access_token = token_data["access_token"]
    refresh_token = token_data.get("refresh_token")
    expiry = time.time() + token_data.get("expires_in", 3600)

    try:
        user_res = requests.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
    except requests.exceptions.RequestException:
        return "User info request failed", 500

    if user_res.status_code != 200:
        return "Failed to fetch user info", 400

    user = user_res.json()

    if "email" not in user:
        return "Invalid user data", 400
    app.logger.info("Login Successfully")
    user_doc = db.users.find_one_and_update(
        {"email": user["email"]},
        {"$set": user},
        upsert=True,
        return_document=True
    )

    db.oauth_tokens.update_one(
        {"user_id": user_doc["_id"]},
        {
            "$set": {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expiry": expiry
            }
        },
        upsert=True
    )

    return render_template("success.html", user=user)


def refresh_token(user_id):
    record = db.oauth_tokens.find_one({"user_id": user_id})

    if not record or "refresh_token" not in record:
        raise Exception("No refresh token available")

    try:
        res = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": record["refresh_token"],
                "grant_type": "refresh_token",
            },
            timeout=5
        )
    except requests.exceptions.RequestException:
        raise Exception("Network error")

    if res.status_code != 200:
        raise Exception("Token refresh failed")

    new_token = res.json()

    if "access_token" not in new_token:
        raise Exception("Invalid refresh response")

    db.oauth_tokens.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "access_token": new_token["access_token"],
                "expiry": time.time() + new_token["expires_in"]
            }
        }
    )
    app.logger.info("New Access Token generated!")
    return new_token["access_token"]


@app.route("/profile/<email>")
def profile(email):
    user = db.users.find_one({"email": email})

    if not user:
        return "Invalid request", 404

    token_data = db.oauth_tokens.find_one({"user_id": user["_id"]})

    if not token_data:
        return "Token not found", 404

    try:
        if time.time() > token_data["expiry"]:
            access_token = refresh_token(user["_id"])
        else:
            access_token = token_data["access_token"]
    except Exception as e:
        return str(e), 401

    return {"email": email}


if __name__ == "__main__":
    app.run(debug=True)