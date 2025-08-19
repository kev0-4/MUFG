@echo off
setlocal EnableDelayedExpansion

:: FinGuard Servers Initialization Script for Windows
:: Activates existing virtual environments and runs Financial Server (port 8001), NLP Server (port 8000), and AI Analytics Server (port 8002)
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

:: Stop any running servers first
echo Stopping any running servers...
taskkill /IM python.exe /F >nul 2>&1
taskkill /IM uvicorn.exe /F >nul 2>&1

:: Wait a moment for processes to terminate
timeout /t 2 /nobreak >nul

:: Verify virtual environments exist
if not exist "%FINANCIAL_VENV%" (
    echo Error: Virtual environment %FINANCIAL_VENV% not found.
    exit /b 1
)
if not exist "%NLP_VENV%" (
    echo Error: Virtual environment %NLP_VENV% not found.
    exit /b 1
)
if not exist "%ANALYTICS_VENV%" (
    echo Error: Virtual environment %ANALYTICS_VENV% not found.
    exit /b 1
)

:: Verify server files exist
if not exist "%FINANCIAL_DIR%\run_dev.py" (
    echo Error: %FINANCIAL_DIR%\run_dev.py not found.
    exit /b 1
)
if not exist "%NLP_DIR%\main.py" (
    echo Error: %NLP_DIR%\main.py not found.
    exit /b 1
)
if not exist "%ANALYTICS_DIR%\main.py" (
    echo Error: %ANALYTICS_DIR%\main.py not found.
    exit /b 1
)

:: Start Financial Server
echo Starting Financial Server on port %FINANCIAL_PORT%...
start "Financial Server" cmd /k "call %FINANCIAL_VENV%\Scripts\activate.bat && cd %FINANCIAL_DIR% && uvicorn run_dev:app --reload --host 0.0.0.0 --port %FINANCIAL_PORT% && pause"

:: Start NLP Server
timeout /t 3 /nobreak >nul
echo Starting NLP Server on port %NLP_PORT%...
start "NLP Server" cmd /k "call %NLP_VENV%\Scripts\activate.bat && cd %NLP_DIR% && uvicorn main:app --reload --host 0.0.0.0 --port %NLP_PORT% && pause"

:: Start AI Analytics Server
timeout /t 3 /nobreak >nul
echo Starting AI Analytics Server on port %ANALYTICS_PORT%...
start "AI Analytics Server" cmd /k "call %ANALYTICS_VENV%\Scripts\activate.bat && cd %ANALYTICS_DIR% && uvicorn main:app --reload --host 0.0.0.0 --port %ANALYTICS_PORT% && pause"

:: Stop all servers
:stop_servers
echo Stopping all servers...
taskkill /IM python.exe /F >nul 2>&1
taskkill /IM uvicorn.exe /F >nul 2>&1
echo Servers stopped.
goto :eof

:: Main execution
if "%1"=="start" (
    echo Starting all FinGuard servers...
    call :start_servers
    timeout /t 5 /nobreak >nul
    echo.
    echo All servers started successfully!
    echo.
    echo Swagger UIs:
    echo   Financial Server: http://localhost:%FINANCIAL_PORT%/docs
    echo   NLP Server: http://localhost:%NLP_PORT%/docs
    echo   AI Analytics Server: http://localhost:%ANALYTICS_PORT%/docs
    echo.
    echo Run '%0 stop' to stop all servers.
    goto :eof
) else if "%1"=="stop" (
    call :stop_servers
    goto :eof
) else (
    echo Usage: %0 [start^|stop]
    echo.
    echo   start - Stop any running servers and start all three servers
    echo   stop  - Stop all running servers
    exit /b 1
)

:start_servers
echo Starting Financial Server on port %FINANCIAL_PORT%...
start "Financial Server" cmd /k "call %FINANCIAL_VENV%\Scripts\activate.bat && cd %FINANCIAL_DIR% && uvicorn run_dev:app --reload --host 0.0.0.0 --port %FINANCIAL_PORT% && pause"

timeout /t 3 /nobreak >nul
echo Starting NLP Server on port %NLP_PORT%...
start "NLP Server" cmd /k "call %NLP_VENV%\Scripts\activate.bat && cd %NLP_DIR% && uvicorn main:app --reload --host 0.0.0.0 --port %NLP_PORT% && pause"

timeout /t 3 /nobreak >nul
echo Starting AI Analytics Server on port %ANALYTICS_PORT%...
start "AI Analytics Server" cmd /k "call %ANALYTICS_VENV%\Scripts\activate.bat && cd %ANALYTICS_DIR% && uvicorn main:app --reload --host 0.0.0.0 --port %ANALYTICS_PORT% && pause"
goto :eof