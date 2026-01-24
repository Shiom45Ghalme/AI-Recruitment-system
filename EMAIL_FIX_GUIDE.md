# 📧 Email Configuration Fix Guide

## Issue: SMTP Authentication Error

If you're seeing this error:
```
SMTPAuthenticationError: (535, b'5.7.8 Username and Password not accepted')
```

## ✅ Solution

### Step 1: Check Your Gmail App Password

1. **Go to Google Account Settings**: https://myaccount.google.com/apppasswords
2. **Enable 2-Factor Authentication** (required for app passwords)
3. **Generate a new App Password**:
   - Select "Mail" as the app
   - Select "Other" as the device
   - Name it "AI Recruitment System"
   - Copy the 16-character password

### Step 2: Update config_local.py

Open `config_local.py` and verify:

```python
# CORRECT FORMAT:
EMAIL_SENDER = "youremail@gmail.com"  # Your full Gmail address
EMAIL_PASSWORD = "abcd efgh ijkl mnop"  # 16-character app password (with or without spaces)
RECRUITER_EMAIL = "recruiter@company.com"  # Can be same as EMAIL_SENDER

# WRONG - Don't use these:
EMAIL_PASSWORD = "your-regular-gmail-password"  # ❌ Won't work!
EMAIL_PASSWORD = ""  # ❌ Empty won't work!
```

### Step 3: Test Your Configuration

Create a test file `test_email.py`:

```python
import smtplib
from email.mime.text import MIMEText

# Replace with your credentials
EMAIL_SENDER = "youremail@gmail.com"
EMAIL_PASSWORD = "your-16-char-app-password"

try:
    msg = MIMEText("Test email from recruitment system", 'plain', 'utf-8')
    msg["Subject"] = "Test Email"
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_SENDER  # Send to yourself

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, EMAIL_SENDER, msg.as_string())
    
    print("✅ Email test successful!")
except Exception as e:
    print(f"❌ Email test failed: {str(e)}")
```

Run it:
```bash
python test_email.py
```

### Step 4: Restart Your Flask App

After updating `config_local.py`, restart the app:

```bash
# Stop the app (Ctrl+C)
# Then restart:
python app.py
```

## 🆘 Still Having Issues?

### Common Mistakes:

1. **Using regular password instead of app password**
   - ❌ Wrong: Your normal Gmail login password
   - ✅ Right: 16-character app password from Google

2. **2FA not enabled**
   - App passwords require 2-Factor Authentication
   - Enable it at: https://myaccount.google.com/security

3. **Wrong email format**
   - ❌ Wrong: `"youremail"` or `'youremail@gmail'`
   - ✅ Right: `"youremail@gmail.com"`

4. **Spaces in app password**
   - Both work: `"abcd efgh ijkl mnop"` or `"abcdefghijklmnop"`

### Alternative: Use Without Emails

If you want to test without email, leave credentials empty in `config_local.py`:

```python
EMAIL_SENDER = ""
EMAIL_PASSWORD = ""
RECRUITER_EMAIL = ""
```

The app will now work WITHOUT sending emails! You'll see notifications but no emails will be sent.

## 🎉 Fixed!

After following these steps:
1. ✅ Update `config_local.py` with correct app password
2. ✅ Restart Flask app
3. ✅ Test the candidate flow again

The app will now either:
- ✅ Send emails successfully, OR
- ✅ Continue working without emails (with a note in the flash message)

No more crashes! 🚀
