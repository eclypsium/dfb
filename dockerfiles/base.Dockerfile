FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y git && \
    pip install poetry==1.8.5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /opt/dfb

COPY you_shall_not_parse/ ./you_shall_not_parse/
COPY dev_from_baseline/ ./dev_from_baseline/
COPY istari_linters/ ./istari_linters/

RUN cd you_shall_not_parse && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    cd ../dev_from_baseline && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev
