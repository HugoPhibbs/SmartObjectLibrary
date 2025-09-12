from flask import Flask
from src.site.api.routers.object_router import object_bp
from src.site.api.routers.connection_router import connection_bp

from flask_cors import CORS
from flask_httpauth import HTTPTokenAuth
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.register_blueprint(object_bp, url_prefix='/object')
app.register_blueprint(connection_bp, url_prefix='/connection')

auth = HTTPTokenAuth(scheme="Bearer")

@auth.verify_token
def verify_token(token):
    # Implement your token verification logic here
    return token == os.getenv("API_TOKEN")


@app.before_request
@auth.login_required
def before_request():
    if not auth.current_user():
        return 401, 'Unauthorized'

if __name__ == '__main__':
    app.run(debug=True)
