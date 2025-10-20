from flask import Flask, request
from src.site.api.routers.object_router import object_bp
from src.site.api.routers.connection_router import connection_bp
from src.site.api.routers.session_router import session_bp
from auth import add_login_auth

from flask_cors import CORS

from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SESSION_SECRET_KEY")

CORS(app, supports_credentials=True, origins=[os.getenv("FRONT_END_DOMAIN")])

add_login_auth(app)

app.register_blueprint(object_bp, url_prefix='/api/object')
app.register_blueprint(connection_bp, url_prefix='/api/connection')
app.register_blueprint(session_bp, url_prefix='/session')


@app.before_request
def log_request_info():
    print(f"{request.method} {request.path}")


if __name__ == '__main__':
    app.run(debug=True)
