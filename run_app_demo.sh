#!/bin/bash
# Quick demo to run the Flutter app

echo "🚀 Deadline Reminder - Flutter App Demo"
echo "======================================="

cd "$(dirname "$0")"

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/tasks > /dev/null 2>&1; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend is not running!"
    echo "Please start the backend first:"
    echo "   cd backend && source venv/bin/activate && python run_server.py"
    exit 1
fi

# Navigate to Flutter app
cd deadline_alert_app

echo ""
echo "📱 Available platforms:"
echo "  - Chrome (web) - Recommended for testing"
echo "  - macOS (desktop) - If you prefer desktop app"

echo ""
read -p "Run on web (Chrome)? (y/n): " choice

if [[ $choice == "y" || $choice == "Y" ]]; then
    echo "🌐 Starting Flutter app in Chrome..."
    echo "This will open a new Chrome window with your app"
    flutter run -d chrome
else
    echo "📋 Available devices:"
    flutter devices
    echo ""
    echo "To run manually:"
    echo "  flutter run -d chrome    # Web version"
    echo "  flutter run -d macos     # Desktop version"
    echo "  flutter run              # Choose interactively"
fi
