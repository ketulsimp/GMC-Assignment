

import requests
import time
from configuration.config import CLIENT_ID, CLIENT_SECRET
from database.db import db, TokenRevokedError
import logging

logger = logging.getLogger(__name__)


def refresh_access_token(user_id):
    record = db.oauth_tokens.find_one({"user_id": user_id})

    if not record or "refresh_token" not in record:
        raise Exception("No refresh token")

    stored_refresh_token = record["refresh_token"]

    try:
        response = requests.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,
                "refresh_token": stored_refresh_token,
                "grant_type": "refresh_token",
            },
            timeout=5
        )
    except requests.exceptions.RequestException:
        logger.error("Network error during token refresh")
        raise Exception("Temporary network issue")

    try:
        data = response.json()
    except ValueError:
        logger.error("Invalid JSON response from Google during refresh")
        raise Exception("Invalid response")

    if response.status_code == 400 and data.get("error") == "invalid_grant":
        logger.warning(f"Refresh token revoked for user {user_id}")
        db.oauth_tokens.delete_one({"user_id": user_id})
        raise TokenRevokedError("User needs to re-authenticate")

    if response.status_code != 200:
        logger.error(f"Token refresh failed with status {response.status_code}: {data.get('error', 'unknown_error')}")
        raise Exception("Refresh failed")

    access_token = data.get("access_token")
    if not access_token:
        raise Exception("No access token in response")

    db.oauth_tokens.update_one(
        {"user_id": user_id},
        {
            "$set": {
                "access_token": access_token,
                "expiry": time.time() + data.get("expires_in", 3600)
            }
        }
    )

    logger.info(f"Token refreshed successfully for user {user_id}")
    return access_token


def verify_token_with_google(access_token):
    try:
        response = requests.get(
            "https://www.googleapis.com/oauth2/v1/tokeninfo",
            params={"access_token": access_token},
            timeout=5
        )
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException:
        logger.error("Network error during token verification")
        return False


def get_valid_token(user_id):
    record = db.oauth_tokens.find_one({"user_id": user_id})

    if not record:
        raise Exception("No token record found")

    if time.time() < record.get("expiry", 0) - 60:
        access_token = record["access_token"]

        if verify_token_with_google(access_token):
            return access_token

        logger.warning(f"Token failed Google verification for user {user_id}, attempting refresh")
        return refresh_access_token(user_id)

    logger.info(f"Access token expired for user {user_id}, refreshing")
    return refresh_access_token(user_id)

