from flask_restx import fields

from word_way.api.word import api as word_api
from word_way.enum import WordPart

__all__ = 'wordModel', 'pronunciationWithWordModel', 'pronunciationList',


wordModel = word_api.model('Word', {
    'id': fields.String(
        description='단어 id',
        example='00000000-0000-0000-0000-000000000000',
    ),
    'contents': fields.String(
        description='단어 의미',
        example='붙어 있거나 잇닿은 것을 떨어지게 하다.',
    ),
    'part': fields.String(
        '품사',
        example='verb',
        enum=[p.value for p in WordPart],
    ),
    'related_pronunciations': fields.List(
        fields.String,
        description='관련된 발음',
        example=['잇닿은', '떨어지게 하다'],
    )
})

pronunciationWithWordModel = word_api.model('PronunciationWithWord', {
    'id:': fields.String(
        description='발음 id',
        example='00000000-0000-0000-0000-000000000000',
    ),
    'pronunciation': fields.String(
        description='발음',
        example='떼다'
    ),
    'words': fields.List(fields.Nested(wordModel))
})

pronunciationList = word_api.model('PronunciationList', {
    'data': fields.List(fields.Nested(pronunciationWithWordModel))
})
