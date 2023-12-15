# syntax=docker/dockerfile:1
FROM node:20.9.0-bookworm-slim
WORKDIR /usr/src/app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install
COPY . .
CMD npx wrangler dev --port 5000 --ip 0.0.0.0 --local