from flask import Flask

from config import config_by_name
from app.extensions import db, migrate, jwt, cors


def create_app(config_name="development"):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    _init_extensions(app)

    return app


def _init_extensions(app):
    db.init_app(app)
    from app import models  
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app)

    