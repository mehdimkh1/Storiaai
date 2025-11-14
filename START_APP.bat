@echo off
echo Starting StoriaAI Backend...
cd backend
call ..\.venv\Scripts\activate.bat
start "StoriaAI Backend" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

timeout /t 3

echo Opening Frontend...
cd ..
start "" "frontend\index.html"

echo.
echo ===================================
echo   StoriaAI is running!
echo   Backend: http://localhost:8000
echo   Frontend: Opening in browser
echo ===================================
echo.
echo Press any key to stop...
pause > nul
