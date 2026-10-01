import logging 
from flask import Flask
from .config import config

def create_app():
    app = Flask(__name__)
    app.confg_from_object(config)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime) s[%(levelname)s] %(name)s: %(message)s",
    )
    from.routes.webhook_routes import (webhook_bp)

    return app