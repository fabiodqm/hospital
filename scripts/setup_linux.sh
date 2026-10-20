#!/usr/bin/env bash
set -e
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
if [ ! -f .env ]; then cp .env.example .env; fi
python manage.py makemigrations
python manage.py migrate
python manage.py seed_base_data
python manage.py runserver
