@echo off
cd /d "%~dp0.."
call .venv\Scripts\activate
python manage.py makemigrations hospital --noinput
python manage.py migrate --noinput
python manage.py seed_base_data
start "" http://127.0.0.1:8000/
python manage.py runserver
pause
