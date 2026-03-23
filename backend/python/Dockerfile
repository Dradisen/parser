FROM python:3.14-slim

WORKDIR /parser

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /parser/requirements.txt

RUN apt-get update

RUN pip install --no-cache-dir --upgrade -r /parser/requirements.txt

COPY . /parser/backend

