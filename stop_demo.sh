#!/bin/bash
# ===============================================
# AI Social Media Content Agent - Demo Stopper
# ===============================================

echo "🛑 Stopping AI Social Media Content Agent Demo..."

# Kill processes if PID files exist
if [ -f ".backend_pid" ]; then
    BACKEND_PID=$(cat .backend_pid)
    kill $BACKEND_PID 2>/dev/null
    echo "✅ Backend stopped (PID: $BACKEND_PID)"
    rm -f .backend_pid
fi

if [ -f ".frontend_pid" ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    rm -f .frontend_pid
fi

# Kill any remaining processes on the ports
echo "🧹 Cleaning up any remaining processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:5173 | xargs kill -9 2>/dev/null || true

echo "✅ Demo stopped successfully!"