# syntax=docker/dockerfile:1
FROM node:16.15.1-buster-slim
WORKDIR /usr/src/app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install
COPY . .
CMD npx svelte-kit dev -p 8001 --host 0.0.0.0