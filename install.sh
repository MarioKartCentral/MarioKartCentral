#!/bin/bash
(cp -n .env-example .env)
(cd ./src/backend && python -m pip install -r requirements.txt)
(cd ./src/frontend && npm install)
(cd ./src/cf-worker && npm install)
