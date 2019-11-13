""":mod:`word_way.config` --- Word Way application configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import os

from configparser import ConfigParser
from flask import current_app
from typeguard import typechecked

__all__ = 'load_config', 'get_word_api_config'


@typechecked
def load_config(config_name: str) -> ConfigParser:
    config = ConfigParser()
    # 옵션 이름을 case sensitive 하게 가져오기 위해서
    config.optionxform = str
    config.read(f'conf/{config_name}.conf')
    config['WORD_API']['TOKEN'] = os.environ.get('WORD_API_TOKEN')
    return config


def get_word_api_config() -> dict:
    word_api_config = current_app.config['APP_CONFIG']['WORD_API']
    url = word_api_config['URL']
    token = word_api_config['TOKEN']
    return dict(url=url, token=token)
