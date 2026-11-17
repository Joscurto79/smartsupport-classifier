from flask import Flask
from app.routes import api_bp


def create_app() -> Flask:
    """Application factory isolating live servers from QA test clients."""
    app = Flask(__name__)
    app.register_blueprint(api_bp)
    return app