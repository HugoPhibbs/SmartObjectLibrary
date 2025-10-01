from flask import Flask, request, jsonify
from src.site.api.routers.object_router import object_bp
from src.site.api.routers.connection_router import connection_bp

from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from dotenv import load_dotenv
import os
import hmac

load_dotenv()

app = Flask(__name__)
CORS(app)

auth = HTTPTokenAuth(scheme="Bearer")

app.register_blueprint(object_bp, url_prefix='/object')
app.register_blueprint(connection_bp, url_prefix='/connection')


@app.before_request
def log_request_info():
    print(f"{request.method} {request.path}")


@auth.verify_token
def verify_token(token):
    # Implement your token verification logic here
    return token if hmac.compare_digest(token, os.getenv("API_TOKEN") or "") else None


@app.errorhandler(401)
def _unauthorized(e):
    return jsonify(error="Unauthorized"), 401


if __name__ == '__main__':
    app.run(debug=True)
