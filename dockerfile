# Not yet Tested
FROM python:3.11.9

LABEL team="navyojan"

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /navyojan-project/

COPY ./requirements.txt /navyojan-project/requirements.txt

RUN pip install -r /navyojan-project/requirements.txt

WORKDIR /navyojan-project/
COPY ./ai /navyojan-project/ai
COPY ./navyojan /navyojan-project/navyojan
COPY ./scripts /navyojan-project/scripts
COPY ./userapp /navyojan-project/userapp
COPY ./manage.py /navyojan-project/manage.py
COPY ./logs /navyojan-project/logs
COPY ./tasks /navyojan-project/tasks
