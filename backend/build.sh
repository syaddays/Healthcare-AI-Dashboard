#!/usr/bin/env bash
# Render build script for Smart Hospital Backend

set -o errexit  # Exit on error

echo "🔧 Starting build process..."

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies without cache to avoid Rust issues
echo "📦 Installing dependencies..."
pip install --no-cache-dir --no-binary :all: --only-binary psycopg2-binary,httpx,fastapi,uvicorn,sqlalchemy,aiosqlite,pydantic,python-dotenv,python-multipart -r requirements.txt

echo "✅ Build complete!"
