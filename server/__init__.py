# -*- coding: utf-8 -*-
from flask import Flask

from config import config
from arch.storage.session import Session


def create_app(config_name):
    app = Flask(__name__)

    from .register import register

    app.register_blueprint(register)

    app.config.from_object(config[config_name])

    setattr(app, "db", Session(app.config["SQLALCHEMY_DATABASE_URI"]))

    return app
