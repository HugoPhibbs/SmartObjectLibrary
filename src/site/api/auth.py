import os
from datetime import timedelta
from functools import wraps

from flask import request
from flask_httpauth import HTTPTokenAuth
from flask_login import current_user, LoginManager
from src.site.user_store import get_username
from src.site.user_store import User
import hmac
from dotenv import load_dotenv

load_dotenv()

token_auth = HTTPTokenAuth(scheme="Bearer")


def add_login_auth(app):
    login_manager = LoginManager(app)

    app.config.update(
        SESSION_COOKIE_SAMESITE="None",  # allow cross-site
        SESSION_COOKIE_SECURE=True,  # must be HTTPS in prod
        SESSION_COOKIE_HTTPONLY=True,
        PERMANENT_SESSION_LIFETIME=timedelta(days=3),
        SESSION_REFRESH_EACH_REQUEST=True
    )

    @login_manager.user_loader
    def load_user(user_id: id):
        print(f"id: {user_id}")
        username = get_username(str(user_id))
        if username:
            return User(user_id, username)
        return None


@token_auth.verify_token
def verify_token(token):
    return token if hmac.compare_digest(token, os.getenv("API_TOKEN") or "") else None


def check_auth():
    # I'm shoehorning token auth in here, for simplicity when using check_auth(). Decorators are over-complicated
    token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
    user = token_auth.verify_token_callback(token)

    if not (current_user.is_authenticated or user):
        return "Unauthorized", 401
    return None