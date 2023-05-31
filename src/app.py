"""
Simple flask app serving as the Cloud Run Service.
"""
import logging
from flask import Flask
from src.blueprints.root import root


def create_app() -> Flask:
    """Application factory"""
    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)

    app.register_blueprint(root, url_prefix="")

    return app
