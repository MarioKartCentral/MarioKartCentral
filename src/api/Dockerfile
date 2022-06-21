# syntax=docker/dockerfile:1
FROM python:3.10.5-slim-buster
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY app.py .
CMD [ "uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]