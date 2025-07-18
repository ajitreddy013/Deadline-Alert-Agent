from src.gmail_reader import read_emails

tasks = read_emails()

for task in tasks:
    print(f"\nFrom: {task['from']}")
    print(f"Subject: {task['subject']}")
    print(f"Deadlines found: {task['deadline_phrases']}")
