# syntax=docker/dockerfile:1
FROM python:3.11.2-slim-buster
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY api api
COPY common common
CMD uvicorn api.app:app --reload --host 0.0.0.0 --port $PORT