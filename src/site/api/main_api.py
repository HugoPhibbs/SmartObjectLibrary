from flask import Flask
from src.site.api.routers.object_router import object_bp
from src.site.api.routers.connection_router import connection_bp
import argparse
from flask_cors import CORS

parser = argparse.ArgumentParser(description="Run the Flask API server.")

parser.add_argument("--host", type=str, default="127.0.0.1")
parser.add_argument("--port", type=int, default=5000)
args = parser.parse_args()

app = Flask(__name__)
CORS(app)

app.register_blueprint(object_bp, url_prefix='/object')
app.register_blueprint(connection_bp, url_prefix='/connection')

if __name__ == '__main__':
    app.run(host=args.host, port=args.port, debug=True)
