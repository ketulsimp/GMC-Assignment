

from flask import Blueprint, session, redirect, render_template
from db import db, TokenRevokedError
from utils import get_valid_token
import logging

profile_bp = Blueprint("profile", __name__)

logger = logging.getLogger(__name__)


@profile_bp.route("/profile")
def profile():
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
        logger.error("Token validation error for user session")
        return redirect("/?error=token_error")

    return render_template(
        "profile.html",
        email=user_doc.get("email"),
        name=user_doc.get("name"),
    )

