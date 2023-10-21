# syntax=docker/dockerfile:1
FROM python:3.12.0-slim-bookworm
WORKDIR /usr/src/app
RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY worker worker
COPY common common
CMD python -m worker.app