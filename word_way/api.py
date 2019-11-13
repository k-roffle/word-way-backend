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
    res = requests.get(config.get('url') + 'search', params=params)
    data = to_dict(parse(res.text))
    items = data.get('channel').get('item')
    # item 갯수에 따라 list 또는 dict로 들어옵니다.
    if not isinstance(items, list):
        items = [items]
    result = []
    for item in items:
        senses = []
        senses.append(item.get('sense'))
        for sense in senses:
            if not isinstance(sense, dict):
                continue
            get_example(sense.get('target_code'))
            result.append(sense)
    return jsonify(result)


def get_example(target_code: str):
    config = get_word_api_config()
    params = {
        'key': config.get('token'),
        'q': target_code,
        'target_type': 'view',
        'method': 'target_code',
    }
    res = requests.get(config.get('url') + 'view', params=params)
    data = to_dict(parse(res.text)).get('channel').get('item') \
        .get('senseInfo').get('example_info')

    example_infos = []
    example_infos.append(data)

    for item in data:
        # TODO: 예문 넣어야 함
        pass
    return


def to_dict(input_ordered_dict: OrderedDict):
    return loads(dumps(input_ordered_dict))
