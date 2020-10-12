""":mod:`word_way.api.word` --- Word API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from typing import List, Optional, Tuple

from flask import Blueprint, jsonify, request
from flask_restx import Api, Resource, fields
from sqlalchemy import or_, literal

from word_way.api.constant import API_PRE_PATH
from word_way.api.serializer import serialize
from word_way.context import session
from word_way.models import (
    IncludeWordRelation,
    Pronunciation,
    SynonymsWordRelation,
    Word,
)

__all__ = 'blueprint',

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

    @staticmethod
    def serialize_response(
        pronunciation: Pronunciation,
        words: List[Word],
        priority: int,
    ) -> dict:
        p = pronunciation

        return {
            'id': p.id,
            'pronunciation': p.pronunciation,
            'words': [
                {
                    'id': word.id,
                    'contents': word.contents,
                    'part': word.part,
                    'related_pronunciations':
                        word.related_include_pronunciations,
                } for word in words
            ],
            'related_words': p.related_synonyms_pronunciations,
            'priority': priority,
        }

    @staticmethod
    def distinct_pronunciation(serialized_response: List[dict]):
        pronunciation_ids = set()
        distinct_items = []
        for res in serialized_response:
            pronunciation_id = res['id']
            if pronunciation_id in pronunciation_ids:
                continue
            distinct_items.append(res)
            pronunciation_ids.add(pronunciation_id)
        return distinct_items

    def make_response(
        self,
        pronunciations: List[Tuple[Pronunciation, int]],
        words: Optional[List[Tuple[Word, int]]] = None,
    ):
        response = [
            self.serialize_response(p, p.words, priority)
            for p, priority in pronunciations
        ]
        if words:
            response += [
                self.serialize_response(word.pronunciation, [word], priority)
                for word, priority in words
            ]

        return jsonify(
            data=serialize(self.distinct_pronunciation(response))
        )

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
            - 검색어가 의미에 포함된 단어 (:class:`IncludeWordRelation`)

        """
        keywords = request.args.getlist('keywords')
        query = session.query(Pronunciation)
        words = None

        if keywords:
            base_query = query
            order_column = 'priority'

            # 검색어와 동일한 발음을 가진 단어
            word_query = base_query.filter(
                or_(*[
                    Pronunciation.pronunciation.like(f'%{keyword.strip()}%')
                    for keyword in keywords
                ]),
            ).add_column(literal(0).label(order_column))

            # 검색어가 유의어에 포함된 단어
            synonyms_query = base_query.filter(
                Pronunciation.id.in_(
                    session.query(SynonymsWordRelation.criteria_id).filter(
                        SynonymsWordRelation.related_pronunciations.any(
                            Pronunciation.pronunciation.in_(keywords)
                        ),
                    ).subquery()
                ),
            ).add_column(literal(1).label(order_column))

            query = word_query.union(synonyms_query).order_by(order_column)

            # 검색어가 의미에 포함된 단어
            words = session.query(Word, literal(2).label(order_column)).filter(
                Word.id.in_(
                    session.query(IncludeWordRelation.criteria_id).filter(
                        IncludeWordRelation.related_pronunciations.any(
                            Pronunciation.pronunciation.in_(keywords)
                        ),
                    ).subquery()
                )
            ).all()

        pronunciations = query.all()
        return self.make_response(pronunciations, words)
