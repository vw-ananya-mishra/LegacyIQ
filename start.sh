#!/bin/bash
# start.sh - Start LegacyX Backend and Frontend

echo "🚀 Starting LegacyX..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "${RED}❌ Python 3 not found. Please install Python 3.9+${NC}"
    exit 1
fi

# Check Node
if ! command -v node &> /dev/null; then
    echo "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

echo "${BLUE}📦 Backend Setup${NC}"
cd backend

# Install backend dependencies
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt -q

echo "${GREEN}✓ Backend dependencies installed${NC}"
echo ""

# Start backend in background
echo "${BLUE}🔧 Starting Backend (FastAPI)${NC}"
echo "Logs: backend.log"
python main.py > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
sleep 2

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "${GREEN}✓ Backend health check passed${NC}"
else
    echo "${RED}❌ Backend health check failed${NC}"
    echo "Check backend.log for errors"
fi

echo ""

# Setup frontend
cd ../frontend
echo "${BLUE}📦 Frontend Setup${NC}"

if [ ! -d "node_modules" ]; then
    echo "Installing Node dependencies..."
    npm install -q
fi

echo "${GREEN}✓ Frontend dependencies ready${NC}"
echo ""

# Start frontend
echo "${BLUE}🎨 Starting Frontend (React + Vite)${NC}"
echo "Logs: ../frontend.log"
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
sleep 3

echo ""
echo "${GREEN}========================================${NC}"
echo "✨ LegacyX is running!"
echo "${GREEN}========================================${NC}"
echo ""
echo "📊 Backend:  http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "📋 Next steps:"
echo "  1. Open http://localhost:3000 in your browser"
echo "  2. Generate sample data: python generate_sample_data.py"
echo "  3. Upload the generated XLSX file"
echo "  4. Explore the Command Center"
echo ""
echo "🛑 To stop:"
echo "  kill $BACKEND_PID  # Stop backend"
echo "  kill $FRONTEND_PID # Stop frontend"
echo ""

# Keep script running
wait
