from flask import Blueprint, request, session
from flask_login import login_user, current_user, logout_user
from werkzeug.exceptions import UnsupportedMediaType
from src.site.user_store import verify_user, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/login')
def login():
    try:
        data = request.get_json() or {}
    except UnsupportedMediaType:
        data = {}

    username = data.get('username')
    password = data.get('password')

    session.permanent = True

    if not verify_user(username, password):
        return {"message": "Missing or invalid credentials"}, 401

    login_user(User(id=username, username=username))
    return {"message": "Login successful"}, 200


@auth_bp.post("/logout")
def logout():
    logout_user()
    return {"message": "Logout successful"}, 200


@auth_bp.get("/session-status")
def session_status():
    print(current_user)
    if current_user.is_authenticated:
        return {"authenticated": True, "username": current_user.username}, 200
    else:
        return {"authenticated": False}, 200
