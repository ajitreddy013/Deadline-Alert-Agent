#!/usr/bin/env python3
"""
Test script to demonstrate API functionality
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_basic_endpoints():
    """Test basic API endpoints"""
    print("🚀 Testing Deadline Reminder API")
    print("=" * 50)
    
    # Test health endpoint
    try:
        response = requests.get(f"{BASE_URL}/tasks")
        print(f"✅ GET /tasks: {response.status_code}")
        tasks = response.json()
        print(f"   Current tasks: {len(tasks)}")
    except Exception as e:
        print(f"❌ GET /tasks failed: {e}")
    
    # Test creating a task
    try:
        new_task = {
            "summary": "Test deadline reminder",
            "deadline": "2024-12-31T23:59:59",
            "source": "manual",
            "alert_status": "pending"
        }
        response = requests.post(f"{BASE_URL}/tasks", json=new_task)
        print(f"✅ POST /tasks: {response.status_code}")
        if response.status_code == 200:
            created_task = response.json()
            print(f"   Created task ID: {created_task['id']}")
    except Exception as e:
        print(f"❌ POST /tasks failed: {e}")
    
    # Test deadline extraction
    try:
        test_message = "Please submit your assignment by December 25th at 11:59 PM"
        response = requests.post(
            f"{BASE_URL}/extract_deadline",
            json={"message": test_message}
        )
        print(f"✅ POST /extract_deadline: {response.status_code}")
        if response.status_code == 200:
            extraction = response.json()
            print(f"   Found dates: {extraction['dates']}")
            print(f"   Found tasks: {extraction['tasks']}")
    except Exception as e:
        print(f"❌ POST /extract_deadline failed: {e}")
    
    # Test Gmail ingestion
    try:
        response = requests.post(f"{BASE_URL}/ingest/gmail")
        print(f"✅ POST /ingest/gmail: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Ingested emails: {len(result['ingested'])}")
            for email in result['ingested'][:3]:  # Show first 3
                print(f"   - {email['subject'][:50]}...")
    except Exception as e:
        print(f"❌ POST /ingest/gmail failed: {e}")

def test_server_running():
    """Check if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/tasks", timeout=5)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("Checking if server is running...")
    if test_server_running():
        print("✅ Server is running!")
        test_basic_endpoints()
    else:
        print("❌ Server is not running. Please start it first with:")
        print("   source venv/bin/activate && python run_server.py")
