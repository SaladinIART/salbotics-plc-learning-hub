@echo off
setlocal

cd /d "%~dp0"

set "HOST=127.0.0.1"
set "PORT=8733"
set "URL=http://%HOST%:%PORT%"

echo.
echo PLC Traffic-Light Trainer
echo =========================
echo Project: %CD%
echo URL:     %URL%
echo.

netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul
if %ERRORLEVEL% EQU 0 (
    echo Server already running on port %PORT%.
    echo Opening browser...
    start "" "%URL%"
    exit /b 0
)

if not exist ".venv\Scripts\python.exe" (
    echo Creating Python virtual environment...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Failed to create .venv. Make sure Python is installed and available as "python".
        pause
        exit /b 1
    )
)

echo Installing / checking dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Starting server in a new window...
start "PLC Traffic-Light Trainer Server" cmd /k ""%CD%\.venv\Scripts\python.exe" -m uvicorn main:app --host %HOST% --port %PORT%"

echo Waiting for server...
timeout /t 3 /nobreak >nul

echo Opening browser...
start "" "%URL%"

echo.
echo Launcher done. Keep the server window open while using the trainer.
timeout /t 2 /nobreak >nul

