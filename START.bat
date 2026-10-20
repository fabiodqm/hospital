@echo off
setlocal
cd /d "%~dp0"

echo ========================================
echo   Centro Médico SHINE - START
echo ========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual com Python 3.12...
    py -3.12 -m venv .venv
    if errorlevel 1 (
        echo Não foi possível criar a venv com py -3.12.
        echo Instale Python 3.12 e tente novamente.
        pause
        exit /b 1
    )
)

call .venv\Scripts\activate

echo Usando:
python --version

echo.
if not exist ".install.ok" (
    echo Instalando dependências...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Falha ao instalar dependências.
        pause
        exit /b 1
    )
    echo ok > .install.ok
)

if not exist ".env" copy .env.example .env >nul

echo Preparando banco de dados...
python manage.py makemigrations hospital --noinput
python manage.py migrate --noinput
python manage.py seed_base_data

echo.
echo Abrindo o site em http://127.0.0.1:8000/
start "" http://127.0.0.1:8000/

echo.
echo Servidor iniciado. Para fechar, use CTRL + C nesta janela.
python manage.py runserver

pause
