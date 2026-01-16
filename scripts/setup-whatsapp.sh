#!/bin/bash

echo "🚀 Setting up WhatsApp Deadline Monitor..."
echo ""

# Navigate to whatsapp-service directory
cd "$(dirname "$0")/../backend/whatsapp-service" || exit 1

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo "📥 Please install Node.js from https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js found: $(node --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "✅ Dependencies installed successfully!"
echo ""

# Check if backend is running
echo "🔍 Checking if backend is running..."
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

if curl -s "$BACKEND_URL/tasks" > /dev/null 2>&1; then
    echo "✅ Backend is running at $BACKEND_URL"
else
    echo "⚠️  Backend doesn't seem to be running at $BACKEND_URL"
    echo "💡 Make sure to start your backend before running the WhatsApp monitor"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📱 Next steps:"
echo "   1. Make sure your backend is running"
echo "   2. Run: npm start"
echo "   3. Scan the QR code with WhatsApp"
echo "   4. Start receiving automatic deadline detection!"
echo ""
