@echo off
REM start.bat - Start LegacyX Backend and Frontend on Windows

echo.
echo 🚀 Starting LegacyX...
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

REM Check Node
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)

echo 📦 Backend Setup
cd backend

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Install dependencies
pip install -r requirements.txt -q

echo ✓ Backend dependencies installed
echo.

REM Start backend in a new window
echo 🔧 Starting Backend (FastAPI)
start "LegacyX Backend" python main.py
timeout /t 2 /nobreak

echo.

REM Setup frontend
cd ..\frontend
echo 📦 Frontend Setup

if not exist "node_modules" (
    echo Installing Node dependencies...
    call npm install -q
)

echo ✓ Frontend dependencies ready
echo.

REM Start frontend in a new window
echo 🎨 Starting Frontend (React + Vite)
start "LegacyX Frontend" cmd /k npm run dev

echo.
echo ========================================
echo ✨ LegacyX is starting!
echo ========================================
echo.
echo 📊 Backend:  http://localhost:8000
echo 🎨 Frontend: http://localhost:3000
echo.
echo 📋 Next steps:
echo   1. Open http://localhost:3000 in your browser
echo   2. Generate sample data: python generate_sample_data.py
echo   3. Upload the generated XLSX file
echo   4. Explore the Command Center
echo.
pause
