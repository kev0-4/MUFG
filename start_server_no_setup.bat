@echo off
echo Starting FinGuard Project...

:: Start all services with Docker Compose
start cmd /k "cd C:\Users\lemon\Desktop\Projects\MUFG\monitoring && docker-compose up"

echo All services (servers, Promtail) started.
pause