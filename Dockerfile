FROM python:3.12.6-alpine3.20
LABEL authors="maksymkorniev88@gmail.com"

ENV PYTHONUNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p /files/media

RUN adduser \
    --disabled-password \
    --no-create-home \
    airport_user

RUN chown -R airport_user /files/media
RUN chmod 755 /files/media

USER airport_user
