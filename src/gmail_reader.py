import imaplib
import email
from email.header import decode_header
from email.message import Message
from datetime import datetime, timedelta
import re

EMAIL = "ajitreddy013@gmail.com"
PASSWORD = "bmpo eyak yuyf milx"
IMAP_SERVER = "imap.gmail.com"

def clean_subject(subject):
    decoded, encoding = decode_header(subject)[0]
    if isinstance(decoded, bytes):
        return decoded.decode(encoding or "utf-8", errors="ignore")
    return decoded

def extract_deadlines(text):
    patterns = [
        r"due\s+(?:on\s+)?\d{1,2}\s+\w+",
        r"\d{1,2}:\d{2}\s*(?:AM|PM)",
        r"by\s+\d{1,2}[:.]?\d{0,2}\s*(?:AM|PM)?"
    ]
    found = []
    for pattern in patterns:
        found += re.findall(pattern, text, re.IGNORECASE)
    return found

def read_emails():
    tasks = []
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select("inbox")

        since_date = (datetime.now() - timedelta(days=3)).strftime("%d-%b-%Y")
        status, messages = mail.search(None, f'(SINCE "{since_date}")')

        if status != "OK" or not messages or not messages[0]:
            return []

        email_ids = messages[0].split()

        for num in email_ids[-10:]:
            res, msg_data = mail.fetch(num, "(RFC822)")
            if res != "OK" or not msg_data or not isinstance(msg_data[0], tuple):
                continue

            _, raw_bytes = msg_data[0]
            if not isinstance(raw_bytes, bytes):
                continue

            try:
                msg: Message = email.message_from_bytes(raw_bytes)
            except Exception:
                continue

            subject = clean_subject(msg.get("Subject", "No Subject"))
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

            deadlines = extract_deadlines(body)
            if deadlines:
                tasks.append({
                    "from": from_,
                    "subject": subject,
                    "body": body[:500],
                    "deadline_phrases": deadlines
                })

        mail.logout()
    except Exception as e:
        print(f"Error reading emails: {e}")

    return tasks
