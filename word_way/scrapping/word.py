""":mod:`word_way.scrapping.word` --- 단어 정보 저장(DB)과 관련된 함수
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import logging
import typing
import uuid
import xml.etree.ElementTree as elemTree

from requests import get as requests_get
from sqlalchemy import literal
from sqlalchemy.orm.session import Session
from urllib.parse import urljoin

from word_way.celery import celery
from word_way.context import session
from word_way.config import get_word_api_config
from word_way.models import (IncludeWordRelation, Pronunciation, Sentence,
                             Word, WordSentenceAssoc)
from word_way.scrapping.word_parser import WordParser
from word_way.utils import convert_word_part

__all__ = 'save_word', 'save_word_task',

logger = logging.getLogger(__name__)


@celery.task
def save_word_task(target_word: str):
    save_word(target_word, session)


def save_word(
    target_word: str, session: Session,
) -> typing.Optional[uuid.UUID]:
    """우리말샘 API로 단어 정보를 가져와서 DB에 저장하는 함수

    :param target_word: 정보를 저장할 단어
    :type target_word: :class:`str`
    :param session: 사용할 세션
    :type session: :class:`sqlalchemy.orm.session.Session`
    :return: target_word와 발음이 정확히 일치하는 발음 ID
    :rtype: typing.Optional[uuid.UUID]

    """
    log = logger.getChild('save_word')
    # 단어 기본 정보 요청
    config = get_word_api_config()
    params = {
        'key': config.get('token'),
        'q': target_word,
        'target_type': 'search',
        'part': 'word',
        'sort': 'dict',
    }
    url = urljoin(config.get('url'), 'search')
    res = requests_get(url, params=params)
    if not res.ok:
        return

    pronunciation_id = None
    tree = elemTree.fromstring(res.text)
    for item in tree.findall('item'):
        pronunciation_word = item.findtext('word')
        if not pronunciation_word:
            continue
        pronunciation_word = \
            pronunciation_word.replace('-', '').replace('^', ' ')
        log.info(f'Start saving the word ({pronunciation_word})')
        pronunciation = session.query(Pronunciation).filter(
            Pronunciation.pronunciation == pronunciation_word
        ).one_or_none()
        if not pronunciation:
            pronunciation = Pronunciation(pronunciation=pronunciation_word)
            session.add(pronunciation)
            session.flush()
        if pronunciation_word == target_word:
            pronunciation_id = pronunciation.id
        for sense in item.findall('sense'):
            target_code = sense.findtext('target_code')
            q = session.query(Word).filter(Word.target_code == target_code)
            word_exists = session.query(literal(True)).filter(
                q.exists()
            ).scalar()
            if word_exists:
                continue
            word = Word(
                target_code=int(target_code),
                part=convert_word_part(sense.findtext('pos')),
                contents=sense.findtext('definition'),
                pronunciation_id=pronunciation.id,
            )
            session.add(word)
            session.flush()
            save_include_word(word, session)
            save_example_sentence(word, session)
        log.info(f'Done saving the word ({pronunciation_word})')
    session.commit()
    return pronunciation_id


def save_example_sentence(word: Word, session: Session) -> None:
    """단어의 예문을 가져와 저장합니다.

    :param word: 추가 정보를 저장할 단어
    :type word: :class:`Word`
    :param session: 사용할 세션
    :type session: :class:`sqlalchemy.orm.session.Session

    """
    log = logger.getChild('save_example_sentence')
    # 단어 추가 정보 요청
    config = get_word_api_config()
    params = {
        'key': config.get('token'),
        'q': word.target_code,
        'target_type': 'view',
        'method': 'target_code',
    }
    url = urljoin(config.get('url'), 'view')
    res = requests_get(url, params=params)
    if not res.ok:
        session.expunge(word)

    tree = elemTree.fromstring(res.text)
    sense_info = tree.find('item').find('senseInfo')

    for example_info in sense_info.findall('example_info'):
        example = example_info.findtext('example')
        log.info(f'Start saving the sentence({example}) about {word.id}')
        sentence = Sentence(sentence=example)
        session.add(sentence)
        session.flush()
        assoc = WordSentenceAssoc(word_id=word.id, sentence_id=sentence.id)
        session.add(assoc)
        session.flush()
        log.info(f'Done saving the sentence({example}) about {word.id}')


def save_include_word(word: Word, session: Session) -> None:
    """단어의 포함어를 저장합니다.

    :param word: 포함어를 저장할 대상 단어
    :type word: :class:`Word`
    :param session: 사용할 세션
    :type session: :class:`sqlalchemy.orm.session.Session

    """
    log = logger.getChild('save_include_word')
    word_parser = WordParser()
    for include_word, part in word_parser.parse(word.contents):
        log.info(f'Start saving the word ({include_word}) in {word.id}')
        if part in word_parser.unused_parts:
            log.info(f'The word ({include_word}, {part}) is in unused_parts')
            continue
        pronunciation = session.query(Pronunciation).filter(
            Pronunciation.pronunciation == include_word
        ).one_or_none()
        relation = None
        if not pronunciation:
            pronunciation = Pronunciation(pronunciation=include_word)
            session.add(pronunciation)
            session.flush()
        else:
            relation = session.query(IncludeWordRelation).filter(
                IncludeWordRelation.criteria_id == word.id,
                IncludeWordRelation.relation_id == pronunciation.id,
            ).one_or_none()
        if not relation:
            relation = IncludeWordRelation(
                criteria_id=word.id, relation_id=pronunciation.id,
            )
            session.add(relation)
            session.flush()
        log.info(f'Done saving the word ({include_word}) in {word.id}')
