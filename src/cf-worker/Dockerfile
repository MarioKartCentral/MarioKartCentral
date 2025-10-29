# syntax=docker/dockerfile:1
FROM --platform=linux/amd64 node:24.10.0-bookworm-slim
WORKDIR /usr/src/app
RUN chown node:node /usr/src/app
USER node
COPY --chown=node:node ["package.json", "package-lock.json*", "./"]
RUN npm install
COPY . .
CMD npx wrangler dev --port 5000 --ip 0.0.0.0