import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from dotenv import load_dotenv
import json

def clean_subject(subject):
    if subject is None:
        return "No Subject"
    try:
        decoded, encoding = decode_header(subject)[0]
        if isinstance(decoded, bytes):
            return decoded.decode(encoding or "utf-8", errors="ignore")
        return decoded
    except Exception:
        return subject or "No Subject"

def fetch_emails_from_account(email_address: str, password: str, account_name: str = "", account_category: str = "general", account_priority: str = "medium", days: int = 3) -> List[Dict]:
    """Fetch emails from a specific Gmail account"""
    tasks = []
    IMAP_SERVER = "imap.gmail.com"
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(email_address, password)
        mail.select("inbox")
        date_filter = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{date_filter}")')
        
        if status != "OK" or not messages or not messages[0]:
            return []
            
        email_ids = messages[0].split()
        
        for num in email_ids[-10:]:  # Get last 10 emails
            try:
                res, msg_data = mail.fetch(num, "(RFC822)")
                if res != "OK" or not msg_data or not isinstance(msg_data[0], tuple):
                    continue
                    
                _, raw_bytes = msg_data[0]
                if not isinstance(raw_bytes, bytes):
                    continue
                    
                msg = email.message_from_bytes(raw_bytes)
                subject = clean_subject(msg.get("Subject"))
                from_ = msg.get("From", "")
                
                # Extract body
                body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            payload = part.get_payload(decode=True)
                            if isinstance(payload, bytes):
                                body = payload.decode(errors="ignore")
                                break
                else:
                    payload = msg.get_payload(decode=True)
                    if isinstance(payload, bytes):
                        body = payload.decode(errors="ignore")
                
                tasks.append({
                    "from": from_,
                    "subject": subject,
                    "body": body[:1000],
                    "account": email_address,  # Track which account this came from
                    "account_name": account_name,
                    "category": account_category,
                    "priority": account_priority
                })
                
            except Exception as e:
                print(f"Error processing email {num}: {e}")
                continue
                
        mail.logout()
        
    except Exception as e:
        print(f"Failed to connect to {email_address}: {e}")
        return []
    
    return tasks

def fetch_from_multiple_accounts(accounts_config: List[Dict]) -> List[Dict]:
    """
    Fetch emails from multiple Gmail accounts
    
    accounts_config format:
    [
        {"email": "email1@gmail.com", "password": "app-password-1"},
        {"email": "email2@gmail.com", "password": "app-password-2"},
    ]
    """
    all_tasks = []
    
    for account in accounts_config:
        email_addr = account.get("email")
        password = account.get("password")
        
        if not email_addr or not password:
            print(f"Skipping account with missing credentials: {email_addr}")
            continue
            
        account_name = account.get("name", email_addr)
        account_category = account.get("category", "general")
        account_priority = account.get("priority", "medium")
        
        print(f"📧 Fetching from {account_name} ({email_addr})...")
        account_tasks = fetch_emails_from_account(
            email_addr, password, account_name, account_category, account_priority
        )
        all_tasks.extend(account_tasks)
        print(f"   Found {len(account_tasks)} emails")
    
    return all_tasks

def load_accounts_from_file(config_file: str = "email_accounts.json") -> List[Dict]:
    """Load email accounts configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Configuration file {config_file} not found. Creating example...")
        
        # Create example configuration
        example_config = [
            {
                "email": "your-work-email@gmail.com",
                "password": "your-work-app-password",
                "name": "Work Account"
            },
            {
                "email": "your-personal-email@gmail.com", 
                "password": "your-personal-app-password",
                "name": "Personal Account"
            }
        ]
        
        with open(config_file, 'w') as f:
            json.dump(example_config, f, indent=2)
            
        print(f"Example configuration created at {config_file}")
        print("Please edit this file with your actual email credentials.")
        return []

if __name__ == "__main__":
    # Example usage
    accounts = load_accounts_from_file()
    
    if accounts:
        all_emails = fetch_from_multiple_accounts(accounts)
        print(f"\n📊 Total emails fetched: {len(all_emails)}")
        
        # Group by category and account
        by_category = {}
        by_account = {}
        
        for email_data in all_emails:
            # Group by account
            account_name = email_data.get("account_name", "Unknown")
            if account_name not in by_account:
                by_account[account_name] = []
            by_account[account_name].append(email_data)
            
            # Group by category
            category = email_data.get("category", "general")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(email_data)
        
        print("\n📈 Breakdown by Account:")
        for account, emails in by_account.items():
            category = emails[0].get("category", "general") if emails else "general"
            priority = emails[0].get("priority", "medium") if emails else "medium"
            priority_emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            print(f"  {priority_emoji} {account} ({category}): {len(emails)} emails")
        
        print("\n🏷️ Breakdown by Category:")
        for category, emails in by_category.items():
            priority_counts = {}
            for email_data in emails:
                priority = email_data.get("priority", "medium")
                priority_counts[priority] = priority_counts.get(priority, 0) + 1
            
            category_emoji = {
                "placement": "💼",
                "education": "🎓", 
                "personal": "👤",
                "general": "📧"
            }.get(category, "📧")
            
            print(f"  {category_emoji} {category.title()}: {len(emails)} emails")
            for priority, count in priority_counts.items():
                priority_emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                print(f"    {priority_emoji} {priority}: {count}")
    else:
        print("No accounts configured.")
