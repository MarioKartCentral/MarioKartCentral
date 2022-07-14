#!/bin/bash
(cp .env-example .env)
(cd ./src/api && python3.10 -m pip install -r requirements.txt)
(cd ./src/frontend && npm install)
(cd ./src/cf-worker && npm install)
