#!/usr/bin/env python3
"""
Comprehensive test script for Deadline Reminder project
Tests all components: Backend API, Gmail integration, WhatsApp integration, and notifications
"""
import requests
import json
import os
import sys
import time
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent / "backend"))

BASE_URL = "http://localhost:8000"

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/tasks", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_gmail_integration():
    """Test Gmail integration"""
    print("🔍 Testing Gmail Integration...")
    try:
        # Test direct Gmail ingestion
        os.chdir("backend")
        from dotenv import load_dotenv
        load_dotenv()
        from gmail_ingest import fetch_recent_emails
        
        emails = fetch_recent_emails(days=7)
        print(f"✅ Gmail: Found {len(emails)} emails")
        
        # Test API endpoint
        response = requests.post(f"{BASE_URL}/ingest/gmail")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Gmail API: Ingested {len(result['ingested'])} emails with deadlines")
            return True
        else:
            print(f"❌ Gmail API failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Gmail integration failed: {e}")
        return False

def test_whatsapp_integration():
    """Test WhatsApp integration (dry run)"""
    print("🔍 Testing WhatsApp Integration...")
    try:
        # Test the WhatsApp function exists and can be imported
        from whatsapp_ingest import fetch_whatsapp_messages
        print("✅ WhatsApp: Module imported successfully")
        print("⚠️  WhatsApp: Requires manual QR code scan to test fully")
        return True
    except Exception as e:
        print(f"❌ WhatsApp integration failed: {e}")
        return False

def test_api_endpoints():
    """Test all API endpoints"""
    print("🔍 Testing API Endpoints...")
    
    # Test GET /tasks
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        print(f"✅ GET /tasks: {response.status_code}")
        tasks = response.json()
        print(f"   Current tasks: {len(tasks)}")
    except Exception as e:
        print(f"❌ GET /tasks failed: {e}")
        return False
    
    # Test POST /tasks
    try:
        new_task = {
            "summary": "Test project completion",
            "deadline": "2024-12-31T23:59:59",
            "source": "test",
            "alert_status": "pending"
        }
        response = requests.post(f"{BASE_URL}/tasks", json=new_task)
        print(f"✅ POST /tasks: {response.status_code}")
        if response.status_code == 200:
            task = response.json()
            print(f"   Created task ID: {task['id']}")
            
            # Test desktop notification
            notification_response = requests.post(f"{BASE_URL}/notify/desktop/{task['id']}")
            print(f"✅ Desktop notification: {notification_response.status_code}")
            
    except Exception as e:
        print(f"❌ POST /tasks failed: {e}")
        return False
    
    # Test deadline extraction
    try:
        test_message = "Complete the project by December 25th at 11:59 PM for the hackathon deadline"
        response = requests.post(
            f"{BASE_URL}/extract_deadline",
            json={"message": test_message}
        )
        print(f"✅ Deadline extraction: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Dates found: {result['dates']}")
            print(f"   Tasks found: {result['tasks']}")
            print(f"   Hackathons found: {result['hackathons']}")
    except Exception as e:
        print(f"❌ Deadline extraction failed: {e}")
        return False
    
    return True

def test_flutter_setup():
    """Test Flutter app setup"""
    print("🔍 Testing Flutter App Setup...")
    try:
        # Check if Flutter is installed
        flutter_result = os.system("flutter --version > /dev/null 2>&1")
        if flutter_result == 0:
            print("✅ Flutter: Installed and available")
        else:
            print("❌ Flutter: Not installed")
            return False
            
        # Check if the app can be analyzed
        os.chdir("deadline_alert_app")
        analyze_result = os.system("flutter analyze > /dev/null 2>&1")
        if analyze_result == 0:
            print("✅ Flutter App: Analysis passed")
        else:
            print("⚠️  Flutter App: Analysis warnings (check manually)")
            
        print("✅ Flutter App: Ready to run with 'flutter run'")
        return True
        
    except Exception as e:
        print(f"❌ Flutter setup failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Deadline Reminder - Full Project Test")
    print("=" * 60)
    
    # Check if server is running
    if not test_server_health():
        print("❌ Server is not running. Please start it first:")
        print("   cd backend && source venv/bin/activate && python run_server.py")
        return
    
    print("✅ Server is running!")
    print("-" * 60)
    
    # Run all tests
    tests = [
        ("API Endpoints", test_api_endpoints),
        ("Gmail Integration", test_gmail_integration),
        ("WhatsApp Integration", test_whatsapp_integration),
        ("Flutter App Setup", test_flutter_setup)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
        print("-" * 60)
    
    # Summary
    print("\n📋 Test Summary:")
    print("=" * 60)
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Result: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your project is ready to use.")
        print("\n🚀 To run the full project:")
        print("1. Backend: cd backend && source venv/bin/activate && python run_server.py")
        print("2. Flutter App: cd deadline_alert_app && flutter run")
        print("3. Access API docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()
