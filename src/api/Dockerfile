# syntax=docker/dockerfile:1
FROM python:3.8.10-slim-buster as base
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt
COPY app.py .

FROM base as api-no-debug
CMD [ "uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8000" ]

FROM base as api-debug
RUN pip3 install debugpy
CMD ["python", "-m", "debugpy", "--wait-for-client", "--listen", "0.0.0.0:5678", "-m", "uvicorn app:app --reload --host 0.0.0.0 --port 8000"]