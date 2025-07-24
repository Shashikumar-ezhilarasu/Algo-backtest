#!/bin/bash

# Advanced Stock Market Backtesting Platform Startup Script

echo "🚀 Starting Advanced Stock Market Backtesting Platform..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

# Install requirements
echo "📦 Installing Python packages..."
pip3 install -r backend/requirements.txt

# Function to check if port is available
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use. Please free the port or use a different one."
        return 1
    fi
    return 0
}

# Check required ports
if ! check_port 8000; then
    echo "❌ Backend port 8000 is not available."
    exit 1
fi

if ! check_port 8501; then
    echo "❌ Frontend port 8501 is not available."
    exit 1
fi

# Start PostgreSQL (if not running)
echo "🗄️  Checking PostgreSQL..."
if ! pgrep -x "postgres" > /dev/null; then
    echo "⚠️  PostgreSQL is not running. Please start PostgreSQL first."
    echo "   For macOS: brew services start postgresql"
    echo "   For Linux: sudo systemctl start postgresql"
fi

# Start FastAPI backend in background
echo "🔧 Starting FastAPI backend on port 8000..."
cd backend
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8000/docs > /dev/null; then
    echo "❌ Failed to start backend. Check the logs above for errors."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend started successfully!"
echo "📚 API Documentation: http://localhost:8000/docs"

# Start Streamlit frontend
echo "🖥️  Starting Streamlit frontend on port 8501..."
python3 -m streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

echo ""
echo "🎉 Advanced Stock Market Backtesting Platform is now running!"
echo ""
echo "📊 Frontend (Streamlit): http://localhost:8501"
echo "🔧 Backend (FastAPI):   http://localhost:8000"
echo "📚 API Docs:            http://localhost:8000/docs"
echo ""
echo "⚠️  To stop the platform, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down platform..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Platform stopped successfully!"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
