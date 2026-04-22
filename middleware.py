from flask import session, redirect, request
from database.db import db, TokenRevokedError
from auth.utils import get_valid_token
import logging

logger = logging.getLogger(__name__)

PROTECTED_ROUTES = ["/profile","/merchant/accounts"]

def register_middleware(app):
    @app.before_request
    def token_refresh_middleware():
        if request.path not in PROTECTED_ROUTES:
            return None

        email = session.get("user_email")
        if not email:
            return redirect("/?error=not_logged_in")

        user_doc = db.users.find_one({"email": email})
        if not user_doc:
            session.clear()
            return redirect("/?error=not_logged_in")

        try:
            get_valid_token(user_doc["_id"])
        except TokenRevokedError:
            session.clear()
            db.oauth_tokens.delete_one({"user_id": user_doc["_id"]})
            return redirect("/?error=access_revoked")
        except Exception:
            logger.error("Middleware token validation failed")
            return redirect("/?error=token_error")

        return None
