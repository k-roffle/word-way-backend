""":mod:`word_way.api` --- Word Way API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import xml.etree.ElementTree as elemTree

import requests
from flask import Blueprint, jsonify, request

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

    # TODO: DB에서 검색하는 과정 필요

    config = get_word_api_config()
    params = {
        'key': config.get('token'),
        'q': word,
        'target_type': 'search',
        'part': 'word',
        'sort': 'dict',
    }
    res = requests.get(config.get('url') + 'search', params=params)

    word = []
    tree = elemTree.fromstring(res.text)
    for item in tree.findall('item'):
        for sense in item.findall('sense'):
            extra_info = get_extra_info(sense.findtext('target_code'))
            word.append(serialize_sense(sense, extra_info))

    return jsonify(word)


def serialize_sense(sense: elemTree.Element, extra_info: tuple) -> dict:
    result = {
        'target_code': sense.findtext('target_code'),
        'definition': sense.findtext('definition'),
        'pos': sense.findtext('pos'),
        'sentence': extra_info[0],
        'relation': extra_info[1],
    }
    return result


# TODO: DB 모델 반환하도록 변경해야 합니다.
def get_extra_info(target_code: str) -> tuple:
    '''예문과 유의어를 가져옵니다.'''
    config = get_word_api_config()
    params = {
        'key': config.get('token'),
        'q': target_code,
        'target_type': 'view',
        'method': 'target_code',
    }
    res = requests.get(config.get('url') + 'view', params=params)

    example_infos = []
    relation_infos = []
    tree = elemTree.fromstring(res.text)
    sense_info = tree.find('item').find('senseInfo')

    for example_info in sense_info.findall('example_info'):
        example = example_info.findtext('example')
        example_infos.append({'sentence': example})

    for relation_info in sense_info.findall('relation_info'):
        word = relation_info.findtext('word')
        relation_type = relation_info.findtext('type')
        target_code = relation_info.findtext('link_target_code')
        relation_infos.append({
            'word': word,
            'target_code': target_code,
            'type': relation_type,
        })
    return example_infos, relation_infos
