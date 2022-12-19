# syntax=docker/dockerfile:1
FROM python:3.10.8-slim-buster
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
CMD uvicorn api.app:app --reload --host 0.0.0.0 --port $PORT