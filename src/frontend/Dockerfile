# syntax=docker/dockerfile:1
FROM node:18.15.0-buster-slim
WORKDIR /usr/src/app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install
COPY . .
CMD npx vite --port 8001 --host 0.0.0.0