#!/usr/bin/env python3
"""
Test script to initiate WhatsApp QR code scanning
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_whatsapp_qr():
    """Test WhatsApp integration - will open browser for QR scan"""
    print("🔍 Testing WhatsApp Integration...")
    print("=" * 50)
    
    # You can replace this with any chat name you want to scan
    chat_name = input("Enter WhatsApp chat name (or press Enter for 'Family'): ").strip()
    if not chat_name:
        chat_name = "Family"
    
    print(f"📱 Attempting to scan WhatsApp chat: '{chat_name}'")
    print("⚠️  This will open a Chrome browser window")
    print("⚠️  You'll need to scan the QR code with your phone if not already logged in")
    print("⚠️  Make sure you have the chat name exactly as it appears in WhatsApp")
    
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Cancelled")
        return
    
    try:
        # Call the WhatsApp ingestion endpoint
        print("🚀 Starting WhatsApp ingestion...")
        response = requests.post(
            f"{BASE_URL}/ingest/whatsapp",
            params={"chat_name": chat_name},
            timeout=120  # 2 minutes timeout for QR scan
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ WhatsApp ingestion successful!")
            print(f"📊 Found {len(result['ingested'])} messages with deadlines")
            
            for msg in result['ingested'][:3]:  # Show first 3
                print(f"   - {msg['message'][:50]}...")
                
        else:
            print(f"❌ WhatsApp ingestion failed: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⏰ Request timed out. This might happen if QR code wasn't scanned in time.")
    except Exception as e:
        print(f"❌ Error during WhatsApp ingestion: {e}")

if __name__ == "__main__":
    print("🔧 WhatsApp QR Code Scanner")
    print("=" * 50)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/tasks", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running")
            test_whatsapp_qr()
        else:
            print("❌ Backend server not responding properly")
    except:
        print("❌ Backend server is not running!")
        print("Please start it first with:")
        print("   source venv/bin/activate && python run_server.py")
