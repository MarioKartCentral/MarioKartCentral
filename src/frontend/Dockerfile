# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 node:24.10.0-bookworm-slim
WORKDIR /usr/src/app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install
COPY . .
CMD npx vite --port 8001 --host 0.0.0.0