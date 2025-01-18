# Not yet Tested
FROM python:3.11.9

LABEL team="navyojan"

ENV PYTHONUNBUFFERED 1

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

RUN mkdir -p /navyojan-project/

COPY ./requirements.txt /navyojan-project/requirements.txt

# Upgrade pip and install requirements
RUN pip install --upgrade pip && \
    pip install -r /navyojan-project/requirements.txt

WORKDIR /navyojan-project/
COPY ./ai /navyojan-project/ai
COPY ./navyojan /navyojan-project/navyojan
COPY ./scripts /navyojan-project/scripts
COPY ./userapp /navyojan-project/userapp
COPY ./manage.py /navyojan-project/manage.py
COPY ./logs /navyojan-project/logs
COPY ./tasks /navyojan-project/tasks
