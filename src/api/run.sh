#!/bin/bash
source .venv/bin/activate
uvicorn app:app
deactivate