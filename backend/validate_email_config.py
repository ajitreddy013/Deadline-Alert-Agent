import json
import re

def validate_email_config(config_file="email_accounts.json"):
    """Validate email configuration without exposing sensitive data"""
    
    try:
        with open(config_file, 'r') as f:
            accounts = json.load(f)
    except FileNotFoundError:
        print("❌ Configuration file not found!")
        return False
    except json.JSONDecodeError:
        print("❌ Invalid JSON format in configuration file!")
        return False
    
    print("🔍 Validating Email Configuration...\n")
    
    valid_accounts = 0
    total_accounts = len(accounts)
    
    for i, account in enumerate(accounts, 1):
        name = account.get("name", f"Account {i}")
        email = account.get("email", "")
        password = account.get("password", "")
        category = account.get("category", "")
        priority = account.get("priority", "")
        
        print(f"📧 {name}:")
        
        # Validate email format
        email_valid = bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
        if email_valid and not email.startswith("your-"):
            print(f"   ✅ Email: {email}")
        else:
            print(f"   ❌ Email: Invalid or still template")
            
        # Validate password (check if it's not template and has reasonable length)
        password_valid = len(password) >= 16 and not password.startswith("your-") and not "password" in password.lower()
        if password_valid:
            print(f"   ✅ Password: Configured (length: {len(password)})")
        else:
            print(f"   ❌ Password: Not configured or still template")
            
        # Validate category
        valid_categories = ["personal", "placement", "education", "general"]
        if category in valid_categories:
            print(f"   ✅ Category: {category}")
        else:
            print(f"   ⚠️  Category: {category} (should be one of: {valid_categories})")
            
        # Validate priority
        valid_priorities = ["high", "medium", "low"]
        if priority in valid_priorities:
            priority_emoji = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
            print(f"   ✅ Priority: {priority_emoji} {priority}")
        else:
            print(f"   ⚠️  Priority: {priority} (should be one of: {valid_priorities})")
        
        # Count valid accounts
        if email_valid and password_valid and not email.startswith("your-"):
            valid_accounts += 1
            print(f"   ✅ Status: Ready to use")
        else:
            print(f"   ❌ Status: Needs configuration")
            
        print()
    
    print(f"📊 Summary: {valid_accounts}/{total_accounts} accounts properly configured")
    
    if valid_accounts == total_accounts:
        print("🎉 All accounts are ready! You can now run the multi-email system.")
        return True
    else:
        print("⚠️  Some accounts need attention. Please update the configuration.")
        return False

def show_next_steps():
    """Show next steps for the user"""
    print("\n📋 Next Steps:")
    print("1. Edit email_accounts.json with your real email addresses")
    print("2. Generate app passwords for each Gmail account:")
    print("   - Go to https://myaccount.google.com/security")
    print("   - Enable 2-Step Verification")
    print("   - Generate App Password for 'Mail'")
    print("   - Copy the 16-character password")
    print("3. Run this script again to validate: python validate_email_config.py")
    print("4. Test the system: python multi_gmail_ingest.py")

if __name__ == "__main__":
    is_valid = validate_email_config()
    
    if not is_valid:
        show_next_steps()
