"""
Gmail ingestion using OAuth refresh tokens
This module fetches emails from Gmail using OAuth tokens stored in the database
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timedelta
from typing import List, Dict
import base64
import re

def extract_deadlines_simple(text: str) -> List[str]:
    """Simple deadline extraction without spaCy"""
    deadlines = []
    
    # Common date patterns
    date_patterns = [
        r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # 12/31/2024 or 12-31-2024
        r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # 2024-12-31
        r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',  # January 15, 2024
        r'\d{1,2} (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{4}',    # 15 January 2024
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        deadlines.extend(matches)
    
    return list(set(deadlines))  # Remove duplicates

def fetch_gmail_messages(refresh_token: str, client_id: str, client_secret: str, max_results: int = 50) -> List[Dict]:
    """Fetch messages from Gmail using OAuth"""
    
    # Create credentials from refresh token
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=["https://www.googleapis.com/auth/gmail.readonly"]
    )
    
    # Build Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    
    # Calculate date for filtering (last 30 days)
    after_date = (datetime.now() - timedelta(days=30)).strftime('%Y/%m/%d')
    
    # Search for messages with deadline-related keywords
    query = f'after:{after_date} (deadline OR due OR submit OR registration OR apply OR expires)'
    
    try:
        # Get message list
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        email_data = []
        for msg in messages[:20]:  # Process first 20
            try:
                # Get full message
                message = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()
                
                # Extract headers
                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                from_email = next((h['value'] for h in headers if h['name'] == 'From'), '')
                date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Extract body
                body = ""
                if 'parts' in message['payload']:
                    for part in message['payload']['parts']:
                        if part['mimeType'] == 'text/plain':
                            if 'data' in part['body']:
                                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                                break
                else:
                    if 'data' in message['payload']['body']:
                        body = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8', errors='ignore')
                
                # LLM-based deadline extraction
                try:
                    from llm_deadline_extractor import extract_deadlines_with_llm
                    combined_text = f"{subject}\n{body[:500]}"
                    deadlines_data = extract_deadlines_with_llm(combined_text)
                    deadlines = [d.get('date', '') for d in deadlines_data if d.get('date')]
                except Exception as e:
                    print(f"LLM extraction failed, using regex fallback: {e}")
                    # Simple regex fallback
                    combined_text = f"{subject} {body[:500]}"
                    from llm_deadline_extractor import extract_deadlines_regex_fallback
                    deadlines_data = extract_deadlines_regex_fallback(combined_text)
                    deadlines = [d.get('date', '') for d in deadlines_data if d.get('date')]
                
                email_data.append({
                    'subject': subject,
                    'from': from_email,
                    'date': date,
                    'body_preview': body[:200],
                    'deadlines_found': deadlines,
                    'message_id': msg['id']
                })
                
            except Exception as e:
                print(f"Error processing message {msg['id']}: {e}")
                continue
        
        return email_data
        
    except Exception as e:
        print(f"Error fetching Gmail messages: {e}")
        raise

def ingest_gmail_for_account(email_account, client_id: str, client_secret: str, db_session) -> List[Dict]:
    """Ingest emails for a specific account and save tasks to database"""
    from models import Task
    
    print(f"📧 Ingesting emails for {email_account.email}...")
    
    try:
        # Fetch emails
        emails = fetch_gmail_messages(
            refresh_token=email_account.refresh_token,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Create tasks from emails with deadlines
        tasks_created = []
        for email_data in emails:
            if email_data['deadlines_found']:
                for deadline in email_data['deadlines_found']:
                    # Create task
                    task = Task(
                        summary=email_data['subject'],
                        deadline=deadline,
                        source=f"gmail:{email_account.email}",
                        alert_status='pending'
                    )
                    db_session.add(task)
                    tasks_created.append({
                        'subject': email_data['subject'],
                        'deadline': deadline,
                        'from': email_data['from']
                    })
        
        db_session.commit()
        
        # Update last sync time
        email_account.last_sync = datetime.now()
        db_session.commit()
        
        print(f"✅ Created {len(tasks_created)} tasks from {len(emails)} emails")
        return tasks_created
        
    except Exception as e:
        print(f"❌ Error ingesting emails: {e}")
        raise
