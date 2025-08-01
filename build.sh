#!/bin/bash

# Build script for Render deployment
set -e

echo "🚀 Starting Render build process..."
echo "Python version: $(python --version)"

# Backend setup
echo "📦 Setting up backend..."
cd backend
python -m pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "✅ Build completed successfully!"
echo "🌐 Ready for deployment on Render"