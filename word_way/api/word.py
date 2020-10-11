""":mod:`word_way.api.word` --- Word API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from flask import Blueprint, jsonify, request
from flask_restx import Api, Resource, fields
from sqlalchemy import or_

from word_way.api.constant import API_PRE_PATH
from word_way.api.serializer import serialize
from word_way.context import session

__all__ = 'blueprint',

from word_way.models import Pronunciation

blueprint = Blueprint('word', __name__, url_prefix=f'{API_PRE_PATH}/words')
api = Api(blueprint, doc='/doc/')

parser = api.parser()
parser.add_argument(
    'keywords',
    type=fields.List(fields.String, description='사용자가 입력한 검색 키워드 리스트'),
    location='query',
)


@api.route('/')
class WordApi(Resource):
    from word_way.api.type import pronunciationList

    @api.expect(parser)
    @api.response(200, '성공. 단어 검색 결과', model=pronunciationList)
    def get(self):
        """
        단어 검색 API

            NOTE 1: related_pronunciations 유의어
            NOTE 2: words.related_pronunciations 포함어
            NOTE 3: words length가 2 이상일 경우 동음이의어
            NOTE 4: words length가 1 미만일 경우 조회 X

            ** 검색 결과 순서
            - 검색어와 동일한 발음을 가진 단어 (:class:`Word`)
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
        keywords = request.args.getlist('keywords')
        query = session.query(Pronunciation)

        if keywords:
            query = query.filter(
                or_(*[
                    Pronunciation.pronunciation.like(f'%{keyword.strip()}%')
                    for keyword in keywords
                ]),
            )

        pronunciations = query.all()
        return jsonify(
            data=serialize([
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
