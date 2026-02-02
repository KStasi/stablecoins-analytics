#!/bin/bash

echo "🚀 Starting Stablecoins Analytics"
echo ""

echo "1️⃣ Starting PostgreSQL database..."
docker-compose up -d

echo "⏳ Waiting for database to be ready..."
sleep 5

echo ""
echo "2️⃣ Running initial data collection..."
uv run python collector.py

echo ""
echo "3️⃣ Starting background scheduler..."
uv run python scheduler.py &
SCHEDULER_PID=$!

echo ""
echo "4️⃣ Starting Streamlit app..."
echo "   App will be available at http://localhost:8501"
echo ""
echo "📝 Scheduler running in background (PID: $SCHEDULER_PID)"
echo "   To stop scheduler: kill $SCHEDULER_PID"
echo ""

uv run streamlit run app.py
