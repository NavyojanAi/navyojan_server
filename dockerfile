# Not yet Tested
FROM python:3.11.9

LABEL team="navyojan"

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /navyojan-project/

COPY ./requirements.txt /navyojan-project/requirements.txt

RUN pip install -r /navyojan-project/requirements.txt

WORKDIR /navyojan-project/
COPY ./navyojan /navyojan-project/navyojan
COPY ./ai /navyojan-project/ai
COPY ./scripts /navyojan-project/scripts
