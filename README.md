# 🤖 AI Recruitment System

An intelligent, automated recruitment platform that streamlines the entire hiring process from resume screening to interview scheduling.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## ✨ Features

- **📄 Automated Resume Screening** - AI-powered resume analysis
- **📝 MCQ Assessment** - Role-specific technical tests
- **📧 Email Automation** - Automatic selection/rejection notifications
- **🎥 Zoom Integration** - Automated interview scheduling
- **📊 Analytics Dashboard** - Track applicant statistics by role
- **👥 Multi-Role Support** - Manage multiple job positions
- **⏰ Smart Scheduling** - Flexible interview time management

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Gmail account (for email notifications)
- Zoom account (for interview scheduling)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-recruitment-system.git
   cd ai-recruitment-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   - Copy `config.py` to `config_local.py`
   - Add your credentials to `config_local.py`

5. **Run the application**
   ```bash
   streamlit run ai_recruitment_agent_team.py
   ```

## 📋 Configuration

### Email Setup (Gmail)

1. Enable 2-Factor Authentication
2. Generate App Password: [Google Account Settings](https://myaccount.google.com/apppasswords)
3. Add to `config_local.py`:
   ```python
   EMAIL_SENDER = "your-email@gmail.com"
   EMAIL_PASSWORD = "your-app-password"
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

## 🏗️ Project Structure

```
ai-recruitment-system/
│
├── ai_recruitment_agent_team.py    # Main application
├── config.py                        # Configuration template
├── requirements.txt                 # Python dependencies
├── README.md                        # Documentation
│
├── roles.json                       # Role definitions
├── mcqs.json                        # Assessment questions
├── analytics.json                   # Analytics data
└── predefined_times.json           # Interview slots
```

## 🎯 Usage

### For Recruiters

1. **Configure Settings** - Add email and Zoom credentials in sidebar
2. **Manage Roles** - Add/edit/delete job roles and requirements
3. **Create MCQs** - Add assessment questions for each role
4. **Schedule Slots** - Set available interview time slots
5. **Monitor Analytics** - Track applicant statistics

### For Candidates

1. **Select Role** - Choose the position you're applying for
2. **Upload Resume** - Submit your PDF resume
3. **Take Assessment** - Complete the MCQ test
4. **Schedule Interview** - Choose from available time slots
5. **Receive Confirmation** - Get email with interview details

## 🔧 Key Technologies

- **Streamlit** - Web application framework
- **PyPDF2** - PDF processing
- **Pandas** - Data manipulation
- **Matplotlib** - Data visualization
- **Zoom API** - Video conferencing integration
- **SMTP** - Email automation

## 📊 Analytics Features

- Total applicants per role
- Test pass/fail rates
- Interview scheduling statistics
- Visual charts and graphs

## 🛡️ Security

- Credentials stored in `config_local.py` (gitignored)
- Email validation
- Secure SMTP connection
- OAuth 2.0 for Zoom integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Shiom Ghalme**
- GitHub: [@shiomghalme](https://github.com/shiomghalme)
- Email: shiom.ghalme45@gmail.com

## 🙏 Acknowledgments

- Streamlit team for the amazing framework
- Zoom for API access
- All contributors and testers

## 📞 Support

For support, email shiom.ghalme45@gmail.com or open an issue on GitHub.

---

⭐ **Star this repo** if you find it helpful!
