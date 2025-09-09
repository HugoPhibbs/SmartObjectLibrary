from flask import Flask
from src.site.api.routers.object_router import object_bp
from src.site.api.routers.connection_router import connection_bp

from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(object_bp, url_prefix='/object')
app.register_blueprint(connection_bp, url_prefix='/connection')

if __name__ == '__main__':
    app.run(debug=True)
