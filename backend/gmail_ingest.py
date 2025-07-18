import os
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL = os.environ.get("GMAIL_EMAIL")
PASSWORD = os.environ.get("GMAIL_PASSWORD")
IMAP_SERVER = "imap.gmail.com"

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

def fetch_recent_emails(days: int = 3) -> List[Dict]:
    tasks = []
    if not EMAIL or not PASSWORD:
        raise ValueError("Gmail credentials not configured. Please set GMAIL_EMAIL and GMAIL_PASSWORD environment variables.")
    
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")
        date_filter = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{date_filter}")')
        if status != "OK" or not messages or not messages[0]:
            return []
        email_ids = messages[0].split()
        for num in email_ids[-10:]:
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
                })
            except Exception as e:
                print(f"Error processing email {num}: {e}")
                continue
        mail.logout()
    except Exception as e:
        raise Exception(f"Failed to connect to Gmail: {e}")
    
    return tasks
