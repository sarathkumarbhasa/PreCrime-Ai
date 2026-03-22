@echo off
echo ===========================================
echo       Starting PRECRIME AI SERVERS
echo ===========================================

echo [1/2] Starting Python Backend Server...
start "PRECRIME AI Backend" cmd /k "cd backend && python main.py"

echo [2/2] Starting React Frontend Server...
start "PRECRIME AI Frontend" cmd /k "npm run dev"

echo.
echo Both servers have been launched in new terminal windows!
echo Please check those new windows for the server logs.
echo The Frontend will be available at: http://localhost:3000
echo The Backend will be available at:  http://localhost:8000
echo.
pause
