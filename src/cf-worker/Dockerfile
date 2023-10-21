# syntax=docker/dockerfile:1
FROM node:18.18.2-bookworm-slim
WORKDIR /usr/src/app
COPY ["package.json", "package-lock.json*", "./"]
RUN npm install
COPY . .
CMD npx wrangler dev --port 5000 --ip 0.0.0.0 --local