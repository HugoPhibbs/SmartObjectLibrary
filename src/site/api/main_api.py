import datetime

from flask import Flask, request
from src.site.api.routers.object_router import object_bp
from src.site.api.routers.connection_router import connection_bp
from src.site.api.routers.auth_router import auth_bp
from src.site.user_store import get_username
from src.site.user_store import User

from flask_cors import CORS
from flask_login import LoginManager

from dotenv import load_dotenv
import os
from datetime import timedelta

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET_KEY")


app.config.update(
    SESSION_COOKIE_SAMESITE="None",   # allow cross-site
    SESSION_COOKIE_SECURE=True,       # must be HTTPS in prod
    SESSION_COOKIE_HTTPONLY=True,
    PERMANENT_SESSION_LIFETIME=timedelta(days=3),
    SESSION_REFRESH_EACH_REQUEST=True
)

CORS(app, supports_credentials=True, origins=[os.getenv("FRONT_END_DOMAIN")])

# auth = HTTPTokenAuth(scheme="Bearer")

login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id: id):
    print(f"id: {user_id}")
    username = get_username(str(user_id))
    if username:
        return User(user_id, username)
    return None


app.register_blueprint(object_bp, url_prefix='/api/object')
app.register_blueprint(connection_bp, url_prefix='/api/connection')
app.register_blueprint(auth_bp, url_prefix='/auth')


@app.before_request
def log_request_info():
    print(f"{request.method} {request.path}")


if __name__ == '__main__':
    app.run(debug=True)
