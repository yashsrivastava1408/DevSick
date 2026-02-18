#!/bin/bash

# Devsick Alpha - One-Click Server Deployment Script
# This script prepares the server and starts the Devsick stack.

set -e

echo "🚀 Starting Devsick Server Installation..."

# 1. Check for Docker
if ! [ -x "$(command -v docker)" ]; then
  echo "❌ Error: docker is not installed. Please install Docker first." >&2
  exit 1
fi

# 2. Check for Docker Compose
if ! [ -x "$(command -v docker compose)" ]; then
  echo "❌ Error: docker compose is not installed. Please install Docker Compose v2 first." >&2
  exit 1
fi

# 3. Check for .env file
if [ ! -f .env ]; then
  echo "⚠️  No .env file found. Creating one..."
  echo "GROQ_API_KEY=" > .env
  echo "✅ Empty .env created. PLEASE EDIT IT with your GROQ_API_KEY to enable AI."
else
  echo "✅ .env file found."
fi

# 4. Pull/Build and Start
echo "📦 Pulling and Building Devsick containers..."
docker compose build --no-cache

echo "⚡ Starting services in detached mode..."
docker compose up -d

echo "------------------------------------------------"
echo "✅ DEVSICK IS LIVE"
echo "------------------------------------------------"
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "API Docs:  http://localhost:8000/docs"
echo "------------------------------------------------"
echo "To see logs, run: docker compose logs -f"
