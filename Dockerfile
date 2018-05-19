# This image implements an intepreter for pycharm/idea to help run/test/develop
FROM python:3.5.5-alpine as builder

RUN set -x \
    && apk add --no-cache gcc g++ python3-dev \
    && python -m venv /venv

COPY setup.py README.rst /resources/

RUN set -x \
    && source /venv/bin/activate \
    && pip install -U setuptools wheel pip \
    && cd resources \
    && pip install -e .

FROM python:3.5.5-alpine
MAINTAINER Nickolas Fox <tarvitz@blacklibrary.ru>
COPY --from=builder venv venv
ENV PATH=/venv/bin:$PATH
ENTRYPOINT ["/venv/bin/python"]
