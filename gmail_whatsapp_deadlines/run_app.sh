#!/bin/bash
# Gmail & WhatsApp Deadlines Manager - Launch Script

echo "📧💬 Gmail & WhatsApp Deadlines Manager"
echo "======================================"

cd "$(dirname "$0")"

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/tasks > /dev/null 2>&1; then
    echo "✅ Backend is running!"
else
    echo "❌ Backend is not running!"
    echo "Please start the backend first:"
    echo "   cd ../backend && source venv/bin/activate && python run_server.py"
    echo ""
    read -p "Do you want me to try starting the backend? (y/n): " start_backend
    if [[ $start_backend == "y" || $start_backend == "Y" ]]; then
        echo "🚀 Attempting to start backend..."
        cd ../backend
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            python run_server.py &
            backend_pid=$!
            echo "Backend started with PID: $backend_pid"
            sleep 3
            cd ../gmail_whatsapp_deadlines
        else
            echo "❌ Backend virtual environment not found!"
            exit 1
        fi
    else
        exit 1
    fi
fi

# Install dependencies if needed
if [ ! -d "build" ]; then
    echo "📦 Installing Flutter dependencies..."
    flutter pub get
fi

echo ""
echo "📱 Available platforms:"
echo "  - Chrome (web) - Recommended for testing"
echo "  - Android - If you have Android device connected"
echo "  - iOS - If you have iOS simulator (macOS only)"
echo "  - Desktop - Native desktop app"

echo ""
read -p "Run on web (Chrome)? (y/n): " choice

if [[ $choice == "y" || $choice == "Y" ]]; then
    echo "🌐 Starting Gmail & WhatsApp Deadlines Manager in Chrome..."
    echo "This will open a new Chrome window with your app"
    flutter run -d chrome
else
    echo "📋 Available devices:"
    flutter devices
    echo ""
    echo "To run manually:"
    echo "  flutter run -d chrome    # Web version"
    echo "  flutter run -d android   # Android version"
    echo "  flutter run -d ios       # iOS version"  
    echo "  flutter run              # Choose interactively"
    echo ""
    read -p "Enter device ID or press Enter to choose interactively: " device_id
    if [ -z "$device_id" ]; then
        flutter run
    else
        flutter run -d "$device_id"
    fi
fi
