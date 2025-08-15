# 📧 Multi-Email Account Configuration

This guide explains how to configure multiple Gmail accounts for comprehensive deadline detection across different aspects of your life.

## 🎯 Supported Account Types

### 1. **👤 Personal Accounts** (Medium Priority)
- Personal communications
- Social events, birthdays
- Shopping, bills, subscriptions
- Appointments

### 2. **💼 Placement Account** (High Priority)
- Job applications
- Interview schedules
- Internship deadlines
- Recruiter communications
- Company announcements

### 3. **🎓 Education Account** (High Priority)
- Assignment deadlines
- Project submissions
- Exam schedules
- Course announcements
- Professor communications

## 🔧 Setup Instructions

### Step 1: Copy Template Configuration

```bash
cd backend
cp email_accounts.template.json email_accounts.json
```

### Step 2: Configure Your Email Accounts

Edit `email_accounts.json` with your actual credentials:

```json
[
  {
    "email": "your-personal@gmail.com",
    "password": "your-app-password",
    "name": "Personal Account",
    "category": "personal",
    "priority": "medium",
    "keywords": ["birthday", "event", "family", "friends", "social"]
  },
  {
    "email": "your-placement@gmail.com", 
    "password": "your-app-password",
    "name": "Placement Account",
    "category": "placement",
    "priority": "high",
    "keywords": ["interview", "application", "job", "internship", "recruiter"]
  },
  {
    "email": "your-education@gmail.com",
    "password": "your-app-password", 
    "name": "Education Account",
    "category": "education",
    "priority": "high",
    "keywords": ["assignment", "project", "exam", "course", "professor"]
  }
]
```

### Step 3: Generate Gmail App Passwords

For **each** Gmail account:

1. Go to [Google Account Settings](https://myaccount.google.com/security)
2. Enable 2-Step Verification (if not already enabled)
3. Click "App passwords"
4. Select "Mail" as the app
5. Copy the 16-character password
6. Use this password in your configuration

### Step 4: Validate Configuration

```bash
python validate_email_config.py
```

### Step 5: Test Multi-Email System

```bash
python multi_gmail_ingest.py
```

## 🎯 Smart Categorization

The system automatically categorizes emails based on:

- **Account Type**: Which email account received it
- **Keywords**: Content-based detection
- **Priority Level**: High priority for placement/education, medium for personal

## 🔔 Notification Priorities

- 🔴 **High Priority**: Placement & Education deadlines get urgent notifications
- 🟡 **Medium Priority**: Personal deadlines get standard notifications

## 🔒 Security Best Practices

- ✅ Never commit `email_accounts.json` to version control
- ✅ Use Gmail App Passwords, not your main password
- ✅ Keep credentials in `.gitignore`
- ✅ Regular backup of working configuration

## 📊 Expected Output

```
📧 Fetching from Personal Account (personal@gmail.com)...
   Found 8 emails
💼 Fetching from Placement Account (placement@gmail.com)...  
   Found 12 emails
🎓 Fetching from Education Account (education@gmail.com)...
   Found 6 emails

📊 Total emails fetched: 26

📈 Breakdown by Category:
  💼 Placement: 12 emails (🔴 high priority)
  🎓 Education: 6 emails (🔴 high priority)
  👤 Personal: 8 emails (🟡 medium priority)
```

## 🛠️ Troubleshooting

### Common Issues:

1. **"Authentication failed"**
   - Ensure 2-Step Verification is enabled
   - Use App Password, not account password
   - Check email/password spelling

2. **"No emails found"**
   - Check date range (default: last 3 days)
   - Verify inbox has recent emails
   - Check email account access

3. **"JSON format error"**
   - Validate JSON syntax
   - Use `python validate_email_config.py`

## 🚀 Integration with Main System

The multi-email system integrates seamlessly with the main Deadline Reminder API:

```python
# Import from all accounts
response = requests.post("http://localhost:8000/ingest/multi-gmail")

# View all deadlines with account information
tasks = requests.get("http://localhost:8000/tasks")
```

Each task will include:
- `account`: Source email address
- `category`: personal/placement/education  
- `priority`: high/medium/low
- `account_name`: Friendly account name
