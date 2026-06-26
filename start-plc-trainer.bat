@echo off
setlocal EnableDelayedExpansion

cd /d "%~dp0"

set "HOST=127.0.0.1"
set "PORT=8733"
set "URL=http://%HOST%:%PORT%"

echo.
echo Salbotics PLC Learning Hub
echo ==========================
echo Project: %CD%
echo URL:     %URL%
echo.

netstat -ano | findstr ":%PORT% " | findstr "LISTENING" >nul
if %ERRORLEVEL% EQU 0 (
    echo A server is already running on port %PORT%.
    echo Checking whether it is the current Salbotics PLC Learning Hub...

    powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $r = Invoke-WebRequest -UseBasicParsing '%URL%/api/version' -TimeoutSec 2; if ($r.StatusCode -eq 200 -and $r.Content -match 'phase_3_analytics') { exit 0 } else { exit 1 } } catch { exit 1 }"
    if !ERRORLEVEL! EQU 0 (
        echo Current server looks healthy.
        echo Opening browser...
        start "" "%URL%"
        exit /b 0
    )

    set "EXISTING_PID="
    for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":%PORT% " ^| findstr "LISTENING"') do set "EXISTING_PID=%%P"

    echo.
    echo The server on port %PORT% looks outdated or belongs to another app.
    echo This is why Phase 3 analytics can show 404 / no data.
    if defined EXISTING_PID echo Existing process PID: !EXISTING_PID!
    if not defined EXISTING_PID (
        echo Could not identify the process using port %PORT%.
        echo Close the old server window manually, then run this launcher again.
        pause
        exit /b 1
    )
    echo.
    choice /C YN /M "Stop the existing process on port %PORT% and restart this trainer"
    if ERRORLEVEL 2 (
        echo.
        echo Not restarted. Close the old server window manually, then run this launcher again.
        pause
        exit /b 1
    )

    if defined EXISTING_PID (
        taskkill /PID !EXISTING_PID! /F
        if !ERRORLEVEL! NEQ 0 (
            echo.
            echo Could not stop PID !EXISTING_PID!. Close the old server window manually, then run this launcher again.
            pause
            exit /b 1
        )
        timeout /t 2 /nobreak >nul
    )
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
start "Salbotics PLC Learning Hub Server" cmd /k ""%CD%\.venv\Scripts\python.exe" -m uvicorn main:app --host %HOST% --port %PORT%"

echo Waiting for server...
timeout /t 3 /nobreak >nul

echo Opening browser...
start "" "%URL%"

echo.
echo Launcher done. Keep the server window open while using the trainer.
timeout /t 2 /nobreak >nul
