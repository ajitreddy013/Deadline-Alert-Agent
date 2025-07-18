# 🔒 Security Guide - Protecting Your Credentials

## ⚠️ **IMPORTANT: Never commit credentials to GitHub!**

This guide ensures your personal information stays secure.

## 🛡️ **What We've Protected:**

### ✅ **Environment Variables (.env file)**
- Your `.env` file is in `.gitignore` - it will never be committed
- Contains your Gmail credentials and API keys
- Only exists locally on your machine

### ✅ **Database Files**
- `tasks.db` files are now ignored by git
- Your personal tasks and data stay private

### ✅ **System Files**
- `.DS_Store` files (macOS system files) are ignored
- Python cache files (`__pycache__`) are ignored
- Build artifacts and temporary files are ignored

## 📋 **Security Checklist:**

### 1. **Environment File Setup**
```bash
# Your backend/.env file should contain:
GMAIL_EMAIL=your-email@gmail.com
GMAIL_PASSWORD=your-app-password
FCM_SERVER_KEY=your-fcm-server-key
DATABASE_URL=sqlite:///./tasks.db
```

### 2. **Gmail App Password Setup**
- ✅ Use Gmail App Password (not your regular password)
- ✅ Enable 2-factor authentication on Gmail
- ✅ Generate app-specific password in Gmail settings

### 3. **File Permissions**
```bash
# Make sure .env file has restricted permissions
chmod 600 backend/.env
```

## 🚨 **What to NEVER commit:**
- `.env` files
- Database files (`.db`, `.sqlite`)
- API keys or passwords
- Personal email addresses
- Chrome profiles or session data
- Firebase configuration files with keys

## ✅ **What's Safe to Commit:**
- `.env.template` (with placeholder values)
- Source code without hardcoded credentials
- Documentation
- Configuration files without sensitive data

## 🔍 **How to Check for Exposed Credentials:**

### Before committing:
```bash
# Check what files will be committed
git status

# Check for credentials in code
grep -r "your-email@gmail.com" .
grep -r "password" . --exclude-dir=.git

# Check git history for exposed data
git log --oneline --grep="password\|credential\|email"
```

## 🛠️ **Emergency: If Credentials Were Exposed**

If you accidentally committed credentials:

1. **Change your passwords immediately**
2. **Remove from git history:**
   ```bash
   git filter-branch --force --index-filter 'git rm --cached --ignore-unmatch backend/.env' --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push to overwrite remote:**
   ```bash
   git push origin --force --all
   ```

## 📚 **Best Practices:**

1. **Use Environment Variables**
   - Store all secrets in `.env` files
   - Use `python-dotenv` to load them
   - Never hardcode credentials in source code

2. **Regular Security Audits**
   - Check `.gitignore` coverage
   - Review commit history for exposed data
   - Update passwords regularly

3. **Template Files**
   - Keep `.env.template` with placeholder values
   - Help others set up without exposing your data
   - Document required environment variables

## 🎯 **Your Current Security Status:**

✅ **SECURE**: All credentials are now protected
✅ **SECURE**: Database files are ignored
✅ **SECURE**: System files are ignored  
✅ **SECURE**: Templates use placeholders
✅ **SECURE**: Git history is clean

## 🔒 **Remember:**
- Your `.env` file stays local and is never committed
- GitHub will never see your actual credentials
- Your personal data remains private
- The project works for others without exposing your info

**Keep your credentials safe! 🛡️**
