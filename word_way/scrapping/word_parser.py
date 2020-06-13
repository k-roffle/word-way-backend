import typing

from konlpy.tag import Okt


__all__ = 'WordParser',


class WordParser:
    def __new__(cls, *args, **kwargs):
        # Okt class 로딩 속도를 줄이기 위해 한 번만 생성합니다.
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls, *args, **kwargs)
        return cls.instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.parser = Okt()

    def parse(self, contents: str) -> typing.Sequence[typing.Tuple]:
        return self.parser.pos(contents, norm=True, stem=True)
