#!/bin/bash
# start.sh
# Wait for DB to be ready and run migrations before starting the app.

echo "--- Runnings Backend Startup Script ---"

# Run alembic migrations
echo "Running database migrations..."
alembic upgrade head

# Start uvicorn
echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
