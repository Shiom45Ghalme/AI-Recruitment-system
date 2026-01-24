# 🚀 Flask Recruitment System - Quick Start Guide

## Step 1: Install Dependencies

```bash
cd "C:\Users\shiom\OneDrive\Desktop\AI Recruitment System\Automate_recruitment"
pip install -r requirements_flask.txt
```

## Step 2: Verify Configuration

Make sure `config_local.py` exists with your credentials:

```python
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-gmail-app-password"
RECRUITER_EMAIL = "recruiter@company.com"

ZOOM_ACCOUNT_ID = "your-zoom-account-id"
ZOOM_CLIENT_ID = "your-zoom-client-id"
ZOOM_CLIENT_SECRET = "your-zoom-client-secret"

OPENAI_API_KEY = "sk-your-openai-api-key"
COMPANY_NAME = "Your Company Name"
```

## Step 3: Run the Application

```bash
python app.py
```

## Step 4: Access the Application

### Landing Page
```
http://localhost:5000
```

### Recruiter Login
```
http://localhost:5000/recruiter/login
Username: admin
Password: admin123
```

### Candidate Registration
```
http://localhost:5000/candidate/register
```

## Application Flow

### Recruiter Workflow:
1. Login at `/recruiter/login`
2. Go to Dashboard
3. Add roles in "Manage Roles"
4. Add MCQs for each role
5. Add interview time slots
6. Monitor analytics

### Candidate Workflow:
1. Visit homepage
2. Click "Apply Now"
3. Register with name, email, and select role
4. Upload PDF resume (AI analyzes - 50% match needed)
5. Take MCQ test (75% score needed)
6. Schedule interview from available slots
7. Receive confirmation email with Zoom link

## Features

✅ Separate UIs for candidates and recruiters
✅ AI-powered resume screening (50% threshold)
✅ MCQ testing (75% passing score)
✅ Automated email notifications
✅ Zoom meeting creation
✅ Analytics dashboard
✅ Role and question management

## Key Routes

| Route | Purpose |
|-------|---------|
| `/` | Landing page |
| `/recruiter/login` | Recruiter login |
| `/recruiter/dashboard` | Recruiter dashboard |
| `/recruiter/roles` | Manage job roles |
| `/recruiter/mcqs/<role>` | Manage MCQs |
| `/recruiter/slots` | Manage time slots |
| `/recruiter/analytics` | View analytics |
| `/candidate/register` | Candidate registration |
| `/candidate/apply` | Upload resume |
| `/candidate/test` | Take MCQ test |
| `/candidate/schedule` | Schedule interview |
| `/candidate/result/<passed>` | View result |

## Data Files

- `roles.json` - Job roles and requirements
- `mcqs.json` - Assessment questions
- `analytics.json` - Applicant statistics
- `predefined_times.json` - Interview slots
- `uploads/` - Candidate resumes

## Troubleshooting

### Port Already in Use
```bash
# Change port in app.py:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### OpenAI API Errors
- The system automatically falls back to keyword matching
- Verify your API key and account credits

### Email Not Sending
- Use Gmail app password, not regular password
- Enable 2FA on Gmail account

### Zoom Meeting Creation Fails
- System provides fallback Zoom link
- Verify OAuth credentials

## Security Notes

⚠️ **Change default admin password in production!**

To add proper authentication:
1. Use Flask-Login extension
2. Store hashed passwords in database
3. Implement user registration for recruiters

## Next Steps

1. ✅ Install dependencies
2. ✅ Configure credentials
3. ✅ Run the application
4. ✅ Login as recruiter
5. ✅ Add roles and MCQs
6. ✅ Test candidate flow

Need help? Contact: shiom.ghalme45@gmail.com
