@echo off
cd /d "%~dp0.."
if not exist ".venv\Scripts\python.exe" py -3.12 -m venv .venv
call .venv\Scripts\activate
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env
python manage.py makemigrations hospital --noinput
python manage.py migrate --noinput
python manage.py seed_base_data
start "" http://127.0.0.1:8000/
python manage.py runserver
pause
