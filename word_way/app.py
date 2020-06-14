""":mod:`word_way.app` --- web app
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Flask
from flask_cors import CORS
from typeguard import typechecked

from word_way.api import blueprint as basic_api
from word_way.api.word import blueprint as word_api
from word_way.config import load_config

__all__ = 'create_app',


@typechecked
def create_app(config_name: str) -> Flask:
    app = Flask(__name__)
    app.register_blueprint(basic_api)
    app.register_blueprint(word_api)
    config = load_config(config_name)
    app.config.update(config['WEB'])
    app.config['APP_CONFIG'] = config
    CORS(app, origins=config['WEB']['CROSS_ORIGIN_URLS'])

    return app
