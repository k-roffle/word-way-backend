""":mod:`word_way.api` --- Word Way API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from collections import OrderedDict
from json import loads, dumps

import requests
from flask import Blueprint, jsonify, request
from xmltodict import parse

from .config import get_word_api_config

__all__ = 'api', 'ping', 'get_word'


api = Blueprint('api', __name__)


@api.route('/ping/', methods=['GET'])
def ping():
    return 'pong'


@api.route('/word/', methods=['POST'])
def get_word():
    def to_dict(input_ordered_dict: OrderedDict):
        return loads(dumps(input_ordered_dict))
    params = request.get_json()
    word = params.get('word')
    config = get_word_api_config()
    params = {
        'key': config.get('token'),
        'q': word,
        'target_type': 'search',
        'part': 'word',
        'sort': 'dict',
    }
    res = requests.get(config.get('url'), params=params)
    data = to_dict(parse(res.text))
    items = data.get('channel').get('item')
    result = []
    for item in items:
        for sense in item.get('sense'):
            if not isinstance(sense, dict):
                continue
            result.append(sense)
    return jsonify(result)
