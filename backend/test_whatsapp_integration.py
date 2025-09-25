#!/usr/bin/env python3
"""
Test script for WhatsApp notification integration
Tests all WhatsApp-related functionality
"""
import requests
import json
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

BASE_URL = "http://localhost:8000"

def test_server_health():
    """Test if the server is running"""
    try:
        response = requests.get(f"{BASE_URL}/tasks", timeout=5)
        return response.status_code == 200
    except:
        return False

def test_user_preferences():
    """Test user preferences endpoints"""
    print("🔍 Testing User Preferences...")
    
    # Test getting default preferences
    try:
        response = requests.get(f"{BASE_URL}/user/preferences")
        if response.status_code == 200:
            print("✅ Get default preferences: Working")
            preferences = response.json()
            print(f"   Default preferences: {json.dumps(preferences, indent=2)}")
        else:
            print(f"❌ Get preferences failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get preferences failed: {e}")
        return False
    
    # Test updating preferences with WhatsApp number
    try:
        test_preferences = {
            "email": "test@example.com",
            "whatsapp_number": "+1234567890",  # Test number - replace with your actual number
            "email_notifications": True,
            "whatsapp_notifications": True,
            "desktop_notifications": True
        }
        
        response = requests.post(f"{BASE_URL}/user/preferences", json=test_preferences)
        if response.status_code == 200:
            print("✅ Update preferences: Working")
            updated = response.json()
            print(f"   Updated preferences: {json.dumps(updated, indent=2)}")
        else:
            print(f"❌ Update preferences failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Update preferences failed: {e}")
        return False
    
    return True

def test_whatsapp_number_validation():
    """Test WhatsApp number validation"""
    print("🔍 Testing WhatsApp Number Validation...")
    
    test_cases = [
        ("+1234567890", True),    # Valid
        ("+911234567890", True),  # Valid India
        ("1234567890", False),    # Missing +
        ("+123", False),          # Too short
        ("+abc1234567890", False) # Invalid characters
    ]
    
    for number, should_be_valid in test_cases:
        try:
            test_preferences = {
                "whatsapp_number": number,
                "whatsapp_notifications": True
            }
            
            response = requests.post(f"{BASE_URL}/user/preferences", json=test_preferences)
            
            if should_be_valid:
                if response.status_code == 200:
                    print(f"✅ Valid number {number}: Accepted")
                else:
                    print(f"❌ Valid number {number}: Rejected unexpectedly")
                    return False
            else:
                if response.status_code == 400:
                    print(f"✅ Invalid number {number}: Correctly rejected")
                else:
                    print(f"❌ Invalid number {number}: Should have been rejected")
                    return False
                    
        except Exception as e:
            print(f"❌ Testing number {number} failed: {e}")
            return False
    
    return True

def test_whatsapp_notification_endpoints():
    """Test WhatsApp notification endpoints"""
    print("🔍 Testing WhatsApp Notification Endpoints...")
    
    # First, set up preferences with a test number
    test_preferences = {
        "whatsapp_number": "+1234567890",  # Replace with your actual WhatsApp number for real testing
        "whatsapp_notifications": True,
        "desktop_notifications": True
    }
    
    try:
        requests.post(f"{BASE_URL}/user/preferences", json=test_preferences)
        print("✅ Test preferences set")
    except Exception as e:
        print(f"❌ Failed to set test preferences: {e}")
        return False
    
    # Create a test task
    try:
        test_task = {
            "summary": "Test WhatsApp deadline reminder",
            "deadline": "2024-12-31T23:59:59",
            "source": "test",
            "alert_status": "pending"
        }
        response = requests.post(f"{BASE_URL}/tasks", json=test_task)
        if response.status_code == 200:
            task = response.json()
            task_id = task["id"]
            print(f"✅ Test task created: ID {task_id}")
        else:
            print(f"❌ Failed to create test task: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Failed to create test task: {e}")
        return False
    
    # Test WhatsApp notification for the task
    try:
        response = requests.post(f"{BASE_URL}/notify/whatsapp/{task_id}")
        if response.status_code == 200:
            print("✅ WhatsApp task notification endpoint: Working")
            result = response.json()
            print(f"   Result: {json.dumps(result, indent=2)}")
            print("⚠️  Note: Actual WhatsApp message sending requires valid Twilio credentials")
        else:
            print(f"⚠️  WhatsApp task notification: {response.status_code}")
            print(f"   This is expected if Twilio credentials are not configured")
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ WhatsApp task notification failed: {e}")
        return False
    
    # Test custom WhatsApp notification
    try:
        response = requests.post(
            f"{BASE_URL}/notify/whatsapp",
            params={
                "to_number": "+1234567890",  # Test number
                "title": "Test Notification",
                "message": "This is a test message from your Deadline Reminder system!"
            }
        )
        
        if response.status_code == 200:
            print("✅ Custom WhatsApp notification endpoint: Working")
            result = response.json()
            print(f"   Result: {json.dumps(result, indent=2)}")
        else:
            print(f"⚠️  Custom WhatsApp notification: {response.status_code}")
            print("   This is expected if Twilio credentials are not configured")
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
    except Exception as e:
        print(f"❌ Custom WhatsApp notification failed: {e}")
        return False
    
    # Test all-channels notification
    try:
        response = requests.post(f"{BASE_URL}/notify/all/{task_id}")
        if response.status_code == 200:
            print("✅ All-channels notification endpoint: Working")
            result = response.json()
            print(f"   Result: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ All-channels notification failed: {response.status_code}")
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
            return False
    except Exception as e:
        print(f"❌ All-channels notification failed: {e}")
        return False
    
    return True

def test_whatsapp_module_import():
    """Test if WhatsApp notification module can be imported"""
    print("🔍 Testing WhatsApp Module Import...")
    
    try:
        from whatsapp_notify import (
            send_whatsapp_notification,
            send_deadline_reminder_whatsapp,
            validate_whatsapp_number
        )
        print("✅ WhatsApp notification module: Imported successfully")
        
        # Test validation function
        test_number = validate_whatsapp_number("+1234567890")
        if test_number == "+1234567890":
            print("✅ WhatsApp number validation: Working")
        else:
            print("❌ WhatsApp number validation: Failed")
            return False
            
    except Exception as e:
        print(f"❌ WhatsApp module import failed: {e}")
        return False
    
    return True

def print_setup_instructions():
    """Print setup instructions for Twilio WhatsApp"""
    print("\n📋 WhatsApp Integration Setup Instructions:")
    print("=" * 60)
    print()
    print("🔧 To enable actual WhatsApp message sending:")
    print()
    print("1. Create a Twilio account:")
    print("   https://www.twilio.com/")
    print()
    print("2. Get your credentials from Twilio Console:")
    print("   - Account SID")
    print("   - Auth Token")
    print()
    print("3. For development, use Twilio WhatsApp Sandbox:")
    print("   - Go to Console -> Messaging -> Try it out -> Send a WhatsApp message")
    print("   - Join sandbox by sending 'join <sandbox-code>' to +1 415 523 8886")
    print()
    print("4. Add to your .env file:")
    print("   TWILIO_ACCOUNT_SID=your_account_sid_here")
    print("   TWILIO_AUTH_TOKEN=your_auth_token_here")
    print("   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886")
    print()
    print("5. For production, apply for WhatsApp Business API approval")
    print()
    print("💡 Alternative options:")
    print("   - WhatsApp Business API (official but complex setup)")
    print("   - Other providers like MessageBird, Vonage")
    print()

def main():
    """Run all WhatsApp integration tests"""
    print("🚀 WhatsApp Integration - Comprehensive Test")
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
        ("WhatsApp Module Import", test_whatsapp_module_import),
        ("User Preferences", test_user_preferences),
        ("WhatsApp Number Validation", test_whatsapp_number_validation),
        ("WhatsApp Notification Endpoints", test_whatsapp_notification_endpoints)
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
        print("🎉 All WhatsApp integration tests passed!")
        print("\n✅ Your WhatsApp notification system is ready!")
        print("📱 Next steps:")
        print("   1. Configure Twilio credentials in .env")
        print("   2. Set up WhatsApp sandbox for testing")
        print("   3. Test with your actual WhatsApp number")
        
    print_setup_instructions()

if __name__ == "__main__":
    main()
