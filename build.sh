#!/bin/bash

# Build script for Render deployment
set -e

echo "🚀 Starting Render build process..."

# Backend setup
echo "📦 Setting up backend..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Run database migrations (if needed)
echo "🗄️ Running database migrations..."
# alembic upgrade head  # Uncomment when you have migrations

# Frontend setup
echo "🎨 Setting up frontend..."
cd ../frontend
npm ci
npm run build

echo "✅ Build completed successfully!"
echo "🌐 Ready for deployment on Render"