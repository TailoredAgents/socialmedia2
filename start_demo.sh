#!/bin/bash
# ===============================================
# AI Social Media Content Agent - Demo Launcher
# ===============================================

echo "🚀 Starting AI Social Media Content Agent Demo..."
echo "=================================================="

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Python virtual environment not found!"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if Node modules are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "❌ Frontend dependencies not found!"
    echo "Installing frontend dependencies..."
    cd frontend && npm install && cd ..
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Check if ports are available
if check_port 8000; then
    echo "⚠️  Port 8000 is already in use. Please stop the existing backend service."
    exit 1
fi

if check_port 5173; then
    echo "⚠️  Port 5173 is already in use. Please stop the existing frontend service."
    exit 1
fi

echo "✅ Environment configuration ready"
echo "✅ Ports 8000 and 5173 are available"
echo ""

# Initialize database if it doesn't exist
if [ ! -f "socialmedia.db" ]; then
    echo "🗄️  Initializing SQLite database..."
    source venv/bin/activate
    python -c "
from backend.db.database import engine
from backend.db.models import Base
Base.metadata.create_all(bind=engine)
print('✅ Database initialized successfully')
"
fi

echo "🔧 Starting Backend API Server..."
echo "   - URL: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo ""

# Start backend in background
source venv/bin/activate
cd backend
nohup uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start within 30 seconds"
        echo "Check backend.log for errors"
        kill $BACKEND_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

echo ""
echo "🎨 Starting Frontend Dashboard..."
echo "   - URL: http://localhost:5173"
echo ""

# Start frontend
cd frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
cd ..

echo ""
echo "=================================================="
echo "🎉 DEMO IS READY!"
echo "=================================================="
echo ""
echo "📱 Dashboard: http://localhost:5173"
echo "🔧 API Docs:  http://localhost:8000/docs"
echo "📊 Health:    http://localhost:8000/api/health"
echo ""
echo "🛑 To stop the demo, press Ctrl+C or run:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "💡 Features available in demo mode:"
echo "   ✅ Professional dashboard interface"
echo "   ✅ Mock social media data"
echo "   ✅ Interactive analytics charts"
echo "   ✅ Goal tracking system"
echo "   ✅ Memory explorer"
echo "   ✅ Content management"
echo ""
echo "🔒 Authentication: Simplified for demo (no Auth0 required)"
echo ""

# Save PIDs for cleanup
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

# Wait for user to stop
trap "echo ''; echo '🛑 Stopping demo...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend_pid .frontend_pid; echo '✅ Demo stopped'; exit 0" INT

echo "Press Ctrl+C to stop the demo..."
wait