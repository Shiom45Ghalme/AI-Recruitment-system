# 🤖 AI Recruitment System (Flask Version)

An intelligent, automated recruitment platform built with Flask that streamlines the entire hiring process from resume screening to interview scheduling. **Now with separate UIs for candidates and recruiters!**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

### For Candidates
- **📝 Easy Registration** - Register and select your desired role
- **📄 Automated Resume Screening** - AI-powered analysis with 50% match threshold
- **📝 MCQ Assessment** - Role-specific technical tests with 75% passing score
- **📅 Self-Scheduling** - Choose convenient interview slots
- **📧 Auto Notifications** - Receive emails at every stage

### For Recruiters
- **👥 Role Management** - Add, edit, and delete job roles
- **❓ MCQ Creator** - Create and manage assessment questions
- **📊 Analytics Dashboard** - Track applicant statistics
- **🕒 Slot Management** - Manage available interview times
- **🔐 Secure Access** - Password-protected recruiter portal

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account (for email notifications)
- Zoom account (for interview scheduling)
- OpenAI API key (for resume analysis)

### Installation

1. **Navigate to project directory**
   ```bash
   cd "C:\Users\shiom\OneDrive\Desktop\AI Recruitment System\Automate_recruitment"
   ```

2. **Install Flask dependencies**
   ```bash
   pip install -r requirements_flask.txt
   ```

3. **Configure credentials**
   - Ensure `config_local.py` exists with your credentials:
   ```python
   EMAIL_SENDER = "your-email@gmail.com"
   EMAIL_PASSWORD = "your-app-password"
   RECRUITER_EMAIL = "recruiter@company.com"
   
   ZOOM_ACCOUNT_ID = "your-zoom-account-id"
   ZOOM_CLIENT_ID = "your-zoom-client-id"
   ZOOM_CLIENT_SECRET = "your-zoom-client-secret"
   
   OPENAI_API_KEY = "your-openai-api-key"
   COMPANY_NAME = "Your Company Name"
   ```

4. **Run the Flask application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser to: `http://localhost:5000`
   - Recruiter login: `http://localhost:5000/recruiter/login`
     - Default credentials: `admin` / `admin123`

## 🏗️ Project Structure

```
Automate_recruitment/
│
├── app.py                          # Main Flask application
├── config.py                       # Configuration template
├── config_local.py                 # Your local credentials (gitignored)
├── requirements_flask.txt          # Flask dependencies
│
├── templates/                      # HTML templates
│   ├── base.html                   # Base template
│   ├── index.html                  # Landing page
│   ├── recruiter/                  # Recruiter templates
│   │   ├── login.html
│   │   ├── dashboard.html
│   │   ├── manage_roles.html
│   │   ├── manage_mcqs.html
│   │   ├── manage_slots.html
│   │   └── analytics.html
│   └── candidate/                  # Candidate templates
│       ├── register.html
│       ├── apply.html
│       ├── test.html
│       ├── schedule.html
│       └── result.html
│
├── static/                         # Static files
│   └── css/
│       └── style.css               # Custom styles
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── data_handler.py             # JSON file operations
│   ├── resume_analyzer.py          # Resume analysis
│   ├── email_sender.py             # Email automation
│   └── zoom_integration.py         # Zoom API integration
│
├── uploads/                        # Resume uploads (auto-created)
│
├── roles.json                      # Role definitions
├── mcqs.json                       # Assessment questions
├── analytics.json                  # Analytics data
└── predefined_times.json          # Interview slots
```

## 📋 Configuration

### Email Setup (Gmail)

1. Enable 2-Factor Authentication on your Gmail account
2. Generate App Password: [Google Account Settings](https://myaccount.google.com/apppasswords)
3. Add to `config_local.py`:
   ```python
   EMAIL_SENDER = "your-email@gmail.com"
   EMAIL_PASSWORD = "your-16-digit-app-password"
   RECRUITER_EMAIL = "recruiter@company.com"
   ```

### Zoom Setup

1. Create a Zoom Server-to-Server OAuth app
2. Get credentials from [Zoom Marketplace](https://marketplace.zoom.us/)
3. Add to `config_local.py`:
   ```python
   ZOOM_ACCOUNT_ID = "your-account-id"
   ZOOM_CLIENT_ID = "your-client-id"
   ZOOM_CLIENT_SECRET = "your-client-secret"
   ```

### OpenAI Setup

1. Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
2. Add to `config_local.py`:
   ```python
   OPENAI_API_KEY = "sk-your-api-key"
   ```

## 🎯 How to Use

### For Recruiters

1. **Login** at `/recruiter/login` (admin/admin123)
2. **Add Roles** - Define job positions and requirements
3. **Create MCQs** - Add assessment questions for each role
4. **Add Slots** - Set available interview time slots
5. **Monitor** - View analytics dashboard for applicant stats

### For Candidates

1. **Register** - Visit homepage and click "Apply Now"
2. **Upload Resume** - Submit your PDF resume
   - AI analyzes your resume (50% match required)
3. **Take Test** - Complete MCQ assessment
   - 75% score required to pass
4. **Schedule Interview** - Select from available time slots
5. **Check Email** - Receive confirmation with Zoom link

## 🔧 Key Technologies

- **Flask** - Web framework
- **Bootstrap 5** - Frontend UI
- **PyPDF2** - PDF processing
- **OpenAI GPT** - Resume analysis
- **Zoom API** - Video conferencing
- **SMTP** - Email automation

## 📊 Candidate Flow

```
Register → Upload Resume → AI Analysis (50%) → MCQ Test (75%) → Schedule Interview → Email Confirmation
   ↓              ↓                ↓                  ↓                 ↓
 Email       PDF Parse      Pass/Fail         Pass/Fail         Zoom Link
```

## 🛡️ Security Features

- ✅ Password-protected recruiter portal
- ✅ Separate candidate and recruiter interfaces
- ✅ Credentials stored in `config_local.py` (gitignored)
- ✅ Secure file uploads with validation
- ✅ OAuth 2.0 for Zoom integration
- ✅ Session-based authentication

## 🔄 Differences from Streamlit Version

| Feature | Streamlit | Flask |
|---------|-----------|-------|
| **UI Separation** | Single page | Separate candidate/recruiter portals |
| **Authentication** | None | Password-protected recruiter login |
| **Routing** | Auto | Manual routes |
| **Customization** | Limited | Full HTML/CSS control |
| **Production** | Demo only | Production-ready |
| **Security** | Basic | Role-based access |

## 🐛 Troubleshooting

**Issue: Flask not found**
```bash
pip install Flask==3.0.0
```

**Issue: OpenAI errors**
- Check your API key is valid
- Ensure you have credits in your OpenAI account
- Fallback keyword matching is used if OpenAI fails

**Issue: Zoom meeting creation fails**
- Verify Zoom credentials are correct
- Check account has meeting creation permissions
- System falls back to generic Zoom link

**Issue: Email not sending**
- Verify Gmail app password (not regular password)
- Check 2FA is enabled on Gmail
- Ensure SMTP access is allowed

## 📝 Default Login Credentials

**Recruiter Portal:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change these credentials in production!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Shiom Ghalme**
- GitHub: [@shiomghalme](https://github.com/shiomghalme)
- Email: shiom.ghalme45@gmail.com

## 📞 Support

For support, email shiom.ghalme45@gmail.com or open an issue on GitHub.

---

⭐ **Star this repo** if you find it helpful!

## 🔄 Migrating from Streamlit

If you're coming from the Streamlit version:

1. Install Flask dependencies: `pip install -r requirements_flask.txt`
2. Your existing data files (roles.json, mcqs.json, etc.) work as-is
3. Run with `python app.py` instead of `streamlit run`
4. Access at `http://localhost:5000` instead of port 8501
