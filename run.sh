#!/bin/bash

echo "Starting Stablecoins Analytics"
echo ""

echo "1. Starting PostgreSQL database..."
docker-compose up -d

echo "Waiting for database to be ready..."
sleep 5

echo ""
echo "2. Running initial data collection..."
uv run python scripts/collector.py

echo ""
echo "3. Starting background scheduler..."
uv run python scripts/scheduler.py &
SCHEDULER_PID=$!

echo ""
echo "4. Starting Streamlit app..."
echo "   App will be available at http://localhost:8501"
echo ""
echo "Scheduler running in background (PID: $SCHEDULER_PID)"
echo "   To stop scheduler: kill $SCHEDULER_PID"
echo ""

uv run streamlit run app.py
