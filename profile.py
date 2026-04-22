

from flask import Blueprint, session, redirect, render_template
from database.db import db
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

    return render_template(
        "profile.html",
        email=user_doc.get("email"),
        name=user_doc.get("name"),
        picture=user_doc.get("picture"),
        login_success=True
    )


