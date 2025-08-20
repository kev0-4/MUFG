@echo off
setlocal EnableDelayedExpansion

:: FinGuard Servers Initialization Script for Windows
:: Runs Financial Server (8001), NLP Server (8000), AI Analytics Server (8002), and API Gateway Server (8003)
:: Usage: start_finguard_servers.bat [start|stop]

:: Configuration
set FINANCIAL_DIR=financial-server
set NLP_DIR=server_4_nlp
set ANALYTICS_DIR=server_5_analytics
set APIGW_DIR=api_gateway

set FINANCIAL_VENV=%FINANCIAL_DIR%\finance_venv
set NLP_VENV=%NLP_DIR%\nlp_venv
set ANALYTICS_VENV=%ANALYTICS_DIR%\analytics_venv
set APIGW_VENV=%APIGW_DIR%\apigw_venv

set FINANCIAL_PORT=8001
set NLP_PORT=8000
set ANALYTICS_PORT=8002
set APIGW_PORT=8003

:: Stop any running servers first
echo Stopping any running servers...
taskkill /IM python.exe /F >nul 2>&1
taskkill /IM uvicorn.exe /F >nul 2>&1

:: Wait a moment for processes to terminate
timeout /t 2 /nobreak >nul

:: Start Financial Server
:start_financial_server
echo Starting Financial Server on port %FINANCIAL_PORT%...
call "%FINANCIAL_VENV%\Scripts\activate.bat"
cd "%FINANCIAL_DIR%" || (
    echo Error: Failed to change to %FINANCIAL_DIR%.
    call deactivate
    exit /b 1
)
start /b uvicorn run_dev:app --reload --host 0.0.0.0 --port %FINANCIAL_PORT%
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
start /b uvicorn main:app --reload --host 0.0.0.0 --port %NLP_PORT%
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
start /b uvicorn main:app --reload --host 0.0.0.0 --port %ANALYTICS_PORT%
cd ..
call deactivate

:: Start API Gateway Server
:start_apigw_server
echo Starting API Gateway Server on port %APIGW_PORT%...
if not exist "%APIGW_VENV%" (
    echo Creating virtual environment for API Gateway...
    python -m venv "%APIGW_VENV%"
)
call "%APIGW_VENV%\Scripts\activate.bat"
cd "%APIGW_DIR%" || (
    echo Error: Failed to change to %APIGW_DIR%.
    call deactivate
    exit /b 1
)
echo Installing dependencies from requirements/dev.txt...
pip install -r requirements/dev.txt
start /b uvicorn main:app --reload --host 0.0.0.0 --port %APIGW_PORT%
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
    ping 127.0.0.1 -n 3 >nul
    call :start_apigw_server
    echo All servers started.
    echo Swagger UIs:
    echo   Financial Server: http://localhost:%FINANCIAL_PORT%/docs
    echo   NLP Server: http://localhost:%NLP_PORT%/docs
    echo   AI Analytics Server: http://localhost:%ANALYTICS_PORT%/docs
    echo   API Gateway Server: http://localhost:%APIGW_PORT%/docs
    echo Run 'start_finguard_servers.bat stop' to stop the servers.
    goto :eof
) else if "%1"=="stop" (
    call :stop_servers
    goto :eof
) else (
    echo Usage: %0 [start^|stop]
    exit /b 1
)
