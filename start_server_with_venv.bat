@echo off
setlocal EnableDelayedExpansion

:: FinGuard Servers Initialization Script for Windows
:: Creates virtual environments, installs dependencies, and runs Financial Server (port 8001), NLP Server (port 8000), and AI Analytics Server (port 8002)
:: Usage: start_finguard_servers.bat [start|stop]

:: Configuration
set FINANCIAL_DIR=financial-server
set NLP_DIR=server_4_nlp
set ANALYTICS_DIR=server_5_analytics
set FINANCIAL_VENV=%FINANCIAL_DIR%\finance_venv
set NLP_VENV=%NLP_DIR%\nlp_venv
set ANALYTICS_VENV=%ANALYTICS_DIR%\analytics_venv
set FINANCIAL_PORT=8001
set NLP_PORT=8000
set ANALYTICS_PORT=8002
set LOG_DIR=logs


:: Stop any running servers first
echo Stopping any running servers...
taskkill /IM python.exe /F >nul 2>&1
taskkill /IM uvicorn.exe /F >nul 2>&1

:: Wait a moment for processes to terminate
timeout /t 2 /nobreak >nul


:: Create logs directory
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
type nul > "%LOG_DIR%\financial_server.log"
type nul > "%LOG_DIR%\nlp_server.log"
type nul > "%LOG_DIR%\analytics_server.log"

:: Set up Financial Server virtual environment and dependencies
if not exist "%FINANCIAL_DIR%" (
    echo Error: Directory %FINANCIAL_DIR% not found.
    exit /b 1
)
if not exist "%FINANCIAL_DIR%\run_dev.py" (
    echo Error: %FINANCIAL_DIR%\run_dev.py not found.
    exit /b 1
)
if not exist "%FINANCIAL_VENV%" (
    echo Creating virtual environment for Financial Server...
    python -m venv "%FINANCIAL_VENV%"
)
call "%FINANCIAL_VENV%\Scripts\activate.bat"
if exist "%FINANCIAL_DIR%\requirements.txt" (
    echo Installing dependencies for Financial Server...
    pip install --upgrade pip
    pip install -r "%FINANCIAL_DIR%\requirements.txt"
) else (
    echo Error: %FINANCIAL_DIR%\requirements.txt not found.
    call deactivate
    exit /b 1
)
call deactivate

:: Set up NLP Server virtual environment and dependencies
if not exist "%NLP_DIR%" (
    echo Error: Directory %NLP_DIR% not found.
    exit /b 1
)
if not exist "%NLP_DIR%\main.py" (
    echo Error: %NLP_DIR%\main.py not found.
    exit /b 1
)
if not exist "%NLP_VENV%" (
    echo Creating virtual environment for NLP Server...
    python -m venv "%NLP_VENV%"
)
call "%NLP_VENV%\Scripts\activate.bat"
if exist "%NLP_DIR%\requirements\dev.txt" (
    echo Installing dependencies for NLP Server...
    pip install --upgrade pip
    pip install -r "%NLP_DIR%\requirements\dev.txt" --no-cache-dir
) else (
    echo Error: %NLP_DIR%\requirements\dev.txt not found.
    call deactivate
    exit /b 1
)
call deactivate

:: Set up AI Analytics Server virtual environment and dependencies
if not exist "%ANALYTICS_DIR%" (
    echo Error: Directory %ANALYTICS_DIR% not found.
    exit /b 1
)
if not exist "%ANALYTICS_DIR%\main.py" (
    echo Error: %ANALYTICS_DIR%\main.py not found.
    exit /b 1
)
if not exist "%ANALYTICS_VENV%" (
    echo Creating virtual environment for AI Analytics Server...
    python -m venv "%ANALYTICS_VENV%"
)
call "%ANALYTICS_VENV%\Scripts\activate.bat"
if exist "%ANALYTICS_DIR%\requirements\dev.txt" (
    echo Installing dependencies for AI Analytics Server...
    pip install --upgrade pip
    pip install -r "%ANALYTICS_DIR%\requirements\dev.txt"
) else (
    echo Error: %ANALYTICS_DIR%\requirements\dev.txt not found.
    call deactivate
    exit /b 1
)
call deactivate

:: Start Financial Server
:start_financial_server
echo Starting Financial Server on port %FINANCIAL_PORT%...
call "%FINANCIAL_VENV%\Scripts\activate.bat"
cd "%FINANCIAL_DIR%" || (
    echo Error: Failed to change to %FINANCIAL_DIR%.
    call deactivate
    exit /b 1
)
start /b uvicorn run_dev:app --reload --host 0.0.0.0 --port %FINANCIAL_PORT% > "..\%LOG_DIR%\financial_server.log" 2>&1
cd ..
call deactivate

:: Start NLP Server
:start_nlp_server
echo Starting NLP Server on port %NLP_PORT%...
call "%NLP_VENV%\Scripts\activate.bat"
cd "%NLP_DIR%" || (
    echo Error: Failed to change to %NLP_DIR%.
    call deactivate
    exit /b 1
)
start /b uvicorn main:app --reload --host 0.0.0.0 --port %NLP_PORT% > "..\%LOG_DIR%\nlp_server.log" 2>&1
cd ..
call deactivate

:: Start AI Analytics Server
:start_analytics_server
echo Starting AI Analytics Server on port %ANALYTICS_PORT%...
call "%ANALYTICS_VENV%\Scripts\activate.bat"
cd "%ANALYTICS_DIR%" || (
    echo Error: Failed to change to %ANALYTICS_DIR%.
    call deactivate
    exit /b 1
)
start /b uvicorn main:app --reload --host 0.0.0.0 --port %ANALYTICS_PORT% > "..\%LOG_DIR%\analytics_server.log" 2>&1
cd ..
call deactivate

:: Stop all servers
:stop_servers
echo Stopping all servers...
taskkill /IM python.exe /F
echo Warning: All Python processes stopped. Ensure no other Python applications are running.
goto :eof

:: Main execution
if "%1"=="start" (
    call :start_financial_server
    ping 127.0.0.1 -n 3 >nul
    call :start_nlp_server
    ping 127.0.0.1 -n 3 >nul
    call :start_analytics_server
    echo All servers started. Logs are in %LOG_DIR%.
    echo Swagger UIs:
    echo   Financial Server: http://localhost:%FINANCIAL_PORT%/docs
    echo   NLP Server: http://localhost:%NLP_PORT%/docs
    echo   AI Analytics Server: http://localhost:%ANALYTICS_PORT%/docs
    echo Run 'start_finguard_servers.bat stop' to stop the servers.
    goto :eof
) else if "%1"=="stop" (
    call :stop_servers
    goto :eof
) else (
    echo Usage: %0 [start^|stop]
    exit /b 1
)