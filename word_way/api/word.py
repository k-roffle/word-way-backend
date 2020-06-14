""":mod:`word_way.api.word` --- Word API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Blueprint, jsonify
from flask_restx import Api, Resource

from word_way.api.constant import API_PRE_PATH
from word_way.api.serializer import serialize
from word_way.context import session

__all__ = 'blueprint',

from word_way.models import Pronunciation

blueprint = Blueprint('word', __name__, url_prefix=f'{API_PRE_PATH}/words')
api = Api(blueprint, doc='/doc/')


@api.route('/')
class WordApi(Resource):
    def get(self):
        """

        [GET] /api/words/

        Arguments
            words: ["분리하다", "절단하다", "떨어지다", "분리"]

        Response
            [
                {
                    "id": "00000000-0000-0000-0000-000000000001",
                    "pronunciation": "떼다",
                    "words": [
                        {
                            "id": "00000000-0000-0000-0000-000000000001",
                            "contents": "붙어 있거나 잇닿은 것을 떨어지게 하다.",
                            "part": "verb",
                            "related_pronunciations": ["잇닿은", "떨어지게 하다"]
                        },
                        {
                            "id": "00000000-0000-0000-0000-000000000002",
                            "contents": "남에게서 빌려 온 돈 따위를 돌려주지 않다.",
                            "part": "verb",
                            "related_pronunciations": ["남", "돈"]
                        }
                    ],
                    "related_pronunciations": []
                },
                {
                    "id": "00000000-0000-0000-0000-000000000002",
                    "pronunciation": "꺾다",
                    "words": [
                        {
                            "id": "00000000-0000-0000-0000-000000000003",
                            "contents": "길고 탄력이 있거나 단단한 물체를 구부려...",
                            "part": "verb",
                            "related_pronunciations": []
                        }
                    ]
                    "related_words": ["나아가다", "진보하다"]
                }
            ]

            NOTE 1: related_pronunciations 유의어
            NOTE 2: words.related_pronunciations 포함어
            NOTE 3: words length가 2 이상일 경우 동음이의어
            NOTE 4: words length가 1 미만일 경우 조회 X

            ** 검색 결과 순서
            - 검색어와 동일한 발음을 가진 단어 (:class:`Word`)
                : select * from pronunciation where pronunciation like '%단어%';
            - 검색어가 유의어에 포함된 단어 (:class:`SynonymsWordRelation`)
                : select * from pronunciation where id in (
                    select criteria_id from synonyms_word_relation
                    where related_id = (
                        select id from pronunciation where pronunciation = '단어'
                    )
                );
            - 검색어가 의미에 포함된 단어 (:class:`IncludeWordRelation`)
                : select * from word where id in (
                    select criteria_id from include_word_relation
                    where related_id in (
                        select id from pronunciation where pronunciation = '단어'
                    )
                );

        """
        pronunciations = session.query(Pronunciation).all()

        return jsonify(
            serialize([
                {
                    'id': p.id,
                    'pronunciation': p.pronunciation,
                    'words': [
                        {
                            'id': word.id,
                            'contents': word.contents,
                            'part': word.part,
                            'related_pronunciations':
                                word.related_include_pronunciations,
                        } for word in p.words
                    ],
                    'related_words': p.related_synonyms_pronunciations,
                } for p in pronunciations
            ])
        )
