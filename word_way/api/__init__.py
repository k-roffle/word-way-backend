""":mod:`word_way.api` --- Word Way API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Blueprint
from flask_restx import Api, Resource

__all__ = 'blueprint',


blueprint = Blueprint('api', __name__)
api = Api(blueprint)


@api.route('/ping/')
class HealthCheckApi(Resource):
    def get(self):
        return 'pong'
