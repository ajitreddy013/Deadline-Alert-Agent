#!/bin/bash
# Startup script for Deadline Reminder project

echo "🚀 Starting Deadline Reminder Project"
echo "======================================"

# Change to project directory
cd "$(dirname "$0")"

# Start backend server
echo "📡 Starting backend server..."
cd backend
source venv/bin/activate
python run_server.py &
BACKEND_PID=$!

echo "Backend server started with PID: $BACKEND_PID"
echo "Backend available at: http://localhost:8000"
echo "API docs at: http://localhost:8000/docs"

# Wait a moment for server to start
sleep 3

# Run tests
echo ""
echo "🧪 Running project tests..."
cd ..
python test_full_project.py

echo ""
echo "✅ Project is running!"
echo "To stop the backend server, run: kill $BACKEND_PID"
echo "To start the Flutter app, run: cd deadline_alert_app && flutter run"
