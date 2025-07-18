#!/usr/bin/env python3
"""
Test script to verify Gmail connection
"""
import os
from dotenv import load_dotenv
from gmail_ingest import fetch_recent_emails

# Load environment variables
load_dotenv()

def test_gmail_connection():
    print("Testing Gmail connection...")
    print(f"Gmail Email: {os.getenv('GMAIL_EMAIL')}")
    print(f"Gmail Password: {'*' * len(os.getenv('GMAIL_PASSWORD', ''))}")
    
    try:
        emails = fetch_recent_emails(days=7)
        print(f"✅ Successfully connected to Gmail!")
        print(f"Found {len(emails)} emails in the last 7 days")
        
        if emails:
            print("\nFirst few emails:")
            for i, email in enumerate(emails[:3]):
                print(f"{i+1}. From: {email['from']}")
                print(f"   Subject: {email['subject']}")
                print(f"   Body preview: {email['body'][:100]}...")
                print()
        
        return True
        
    except Exception as e:
        print(f"❌ Gmail connection failed: {e}")
        return False

if __name__ == "__main__":
    test_gmail_connection()
