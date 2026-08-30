@echo off
setlocal
title PathFinder AI Launcher

REM Get the folder containing this script
set "PROJECT_DIR=%~dp0"
set "BACKEND_DIR=%PROJECT_DIR%backend"
set "FRONTEND_DIR=%PROJECT_DIR%frontend"

echo.
echo ==========================================
echo        PathFinder AI - Launcher
echo ==========================================
echo.

REM Check required folders
if not exist "%BACKEND_DIR%" (
    echo ERROR: Backend folder not found:
    echo %BACKEND_DIR%
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%" (
    echo ERROR: Frontend folder not found:
    echo %FRONTEND_DIR%
    pause
    exit /b 1
)

if not exist "%BACKEND_DIR%\venv\Scripts\activate.bat" (
    echo ERROR: Python virtual environment not found.
    echo Expected:
    echo %BACKEND_DIR%\venv
    pause
    exit /b 1
)

if not exist "%FRONTEND_DIR%\package.json" (
    echo ERROR: Frontend package.json not found.
    pause
    exit /b 1
)

echo Starting backend...
start "PathFinder AI - Backend" cmd /k "cd /d ""%BACKEND_DIR%"" && call venv\Scripts\activate.bat && uvicorn main:app --reload"

echo Starting frontend...
start "PathFinder AI - Frontend" cmd /k "cd /d ""%FRONTEND_DIR%"" && npm run dev"

echo.
echo ==========================================
echo Both services are starting.
echo Backend:  http://127.0.0.1:8000
echo Frontend: http://localhost:5173
echo ==========================================
echo.
echo Keep both terminal windows open while using PathFinder AI.
echo You can close them to stop the application.
echo.
pause
