# 글길 백엔드 [![Build Status]](https://travis-ci.org/word-way/word-way-backend)

개요
---

글길 백엔드 저장소입니다.


요구사항
-----

- [Python](https://www.python.org/) 3.7+


설치하는 법
--------
- Python 설치

   다른 방법으로 설치하셔도 무방하나 [pyenv](https://github.com/pyenv/pyenv)를 기준으로 설명합니다

   - pyenv 설치
      ```
      $ brew install pyenv
      ```
   - python 3.7+ 설치

      그냥 설치하면 sqlite3를 못 찾아서 `CFLAGS`를 붙여서 설치합니다.
      ```
      $ CFLAGS="-I$(xcrun --show-sdk-path)/usr/include" pyenv install <Python Version>
      $ pyenv shell <Python Version>
      ```

- virtualenv 세팅

   다른 라이브러리를 사용하셔도 무방합니다
    ```
    $ mkvirtualenv -a `pwd` -p $(which python) venv
    ```

- 필요한 환경 변수 셋팅

   [우리말샘 API](https://opendict.korean.go.kr/) 토큰
   ```
   $ export WORD_API_TOKEN=<Token>
   ```

- dependencies 설치
   ```
   $ ./scripts/install.sh
   ```
   만약 `flake8` 실행시 `segmentation fault`가 발생한다면 재설치하거나 venv 밖의 flake8을 사용해주세요.


실행하는 법
--------

- dev.conf 파일을 생성합니다.
   ```
   $ cp conf/dev.conf.example conf/dev.conf
   ```

- 웹 서버를 실행합니다.
   ```
   $ ./run.py -d -c dev
   ```

 ### Docker로 실행하기

 1. 이미지를 빌드합니다.

    ```bash
    docker build -t word-way/backend .
    ```

 1. 컨테이너를 실행합니다.

    ```bash
    docker run --rm -d -p <Port Number You Want>:2222 -v $PWD/word_way:/app/word_way word-way/backend:latest
    ```

[Build Status]: https://travis-ci.org/word-way/word-way-backend.svg?branch=master
