@echo off
echo ========================================================
echo Scaler AI Persona - Setup Environment (Windows)
echo ========================================================

echo 1. Creating Virtual Environment...
python -m venv venv

echo 2. Activating Virtual Environment and Installing Dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt

echo 3. Setting up Frontend...
cd frontend
call npm install
cd ..

echo ========================================================
echo Setup Complete! 
echo.
echo To start the backend:
echo   call venv\Scripts\activate.bat
echo   python -m uvicorn backend.main:app --reload
echo.
echo To start the frontend:
echo   cd frontend
echo   npm run dev
echo ========================================================
pause
