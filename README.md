# 🤖 AI Recruitment & Interview Automation Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-black.svg)](https://flask.palletsprojects.com/)
[![Google Calendar](https://img.shields.io/badge/Google_Calendar-OAuth_2.0-4285F4.svg)](https://developers.google.com/calendar)
[![Google Meet](https://img.shields.io/badge/Google_Meet-Integrated-00897B.svg)](https://meet.google.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent, end-to-end recruitment platform that automates the entire hiring workflow: from **AI-powered PDF resume screening** and **technical MCQ testing** to **conflict-free interview scheduling** and **automated Google Meet creation via OAuth 2.0 Google Calendar API**.

---

## ✨ Key Features

- **📄 Automated AI Resume Screening** — Parses unstructured PDF resumes and calculates qualification match against role requirements using OpenAI GPT.
- **📝 Role-Specific Technical Assessments** — Dynamic MCQ testing engine with automated randomized questions and instant 75% benchmark grading.
- **📅 Conflict-Free Interview Scheduling** — Concurrency-safe slot booking engine that guarantees zero overlapping or double-booked interview slots.
- **🎥 OAuth 2.0 Google Calendar & Google Meet Integration** — Automatically schedules interview events on Google Calendar with automatic token refresh and provisions live **Google Meet** video conference links.
- **📧 Automated Email Notifications** — Dispatches candidate selection, rejection, and interview confirmation emails with calendar invitations and preparation steps.
- **👥 Dual Portal Architecture** — Completely segregated experiences for candidates (application & testing) and recruiters (management dashboard).
- **📊 Real-time Recruitment Analytics** — Live tracking of applicant funnels, role popularities, test pass/fail rates, and scheduled interviews.

---

## 🏗️ Architecture & Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Web Framework** | Flask, Jinja2, HTML5/CSS3 | Modular multi-page application with responsive UI |
| **Alternative UI** | Streamlit | Rapid interactive prototyping and standalone dashboard |
| **AI / NLP** | OpenAI GPT, PyPDF2 | PDF resume text extraction and semantic skill evaluation |
| **Calendar Automation** | Google Calendar API (v3), OAuth 2.0 | Event scheduling, automatic token refresh, and Google Meet link generation |
| **Communications** | Python `smtplib`, `email` | Secure Gmail SMTP automated email notifications |
| **Data Store** | JSON flat-file storage | Lightweight persistence for roles, MCQs, slots, and analytics |

---

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone https://github.com/Shiom45Ghalme/AI-Recruitment-system.git
cd AI-Recruitment-system/Automate_recruitment
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# Install requirements
pip install -r requirements_flask.txt
```

### 3. Configure Credentials (`config_local.py`)
Create or edit `config_local.py` in the `Automate_recruitment` directory:
```python
# Email Configuration
EMAIL_SENDER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-16-char-gmail-app-password"
RECRUITER_EMAIL = "recruiter@company.com"

# Recruiter Portal Login
RECRUITER_USERNAME = "admin"
RECRUITER_PASSWORD = "your-secure-password"

# Optional: OpenAI API Key for AI Resume Parsing
OPENAI_API_KEY = "sk-..."

# Company Name
COMPANY_NAME = "Your Company Name"
```

### 4. Run the Application
```bash
python app.py
```

Access the portals:
* **Candidate Application Portal:** [http://localhost:5000/](http://localhost:5000/)
* **Recruiter Command Center:** [http://localhost:5000/recruiter/login](http://localhost:5000/recruiter/login)
  * Default Username: `admin`
  * Default Password: `admin123` *(changeable in `config_local.py`)*

---

## 📅 Google Calendar OAuth 2.0 Integration Setup

This project features a production-grade Google Calendar API integration:
- Uses **OAuth 2.0 Desktop Application** authorization.
- Automatically creates calendar events with **Google Meet** conference links for candidates and recruiters.
- **Silent Token Refresh:** Automatically detects expired access tokens and refreshes them using the stored `refresh_token`.

### One-Time Setup:
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) and enable the **Google Calendar API**.
2. Configure the **OAuth Consent Screen** (User type: *External*, add your email under *Test users*).
3. Under **Credentials**, click **Create Credentials** > **OAuth client ID** > Select **Desktop app**.
4. Download the JSON file, rename it to **`credentials.json`**, and place it in the `Automate_recruitment/` folder.
5. In the app, navigate to `http://localhost:5000/recruiter/google-calendar` and click **Authorize Google Calendar Now**.
6. Sign in with your Google account to generate `token.json`. All future scheduling will run 100% automatically!

---

## 🔄 Candidate Application Flow

```
[Candidate Landing Page]
         │
         ▼
[Registration & Role Selection]
         │
         ▼
[Resume Upload (PDF)] ──(AI Score < 50%)──► [Rejection Email & Feedback]
         │
         ├─(AI Score ≥ 50%)
         ▼
[Technical MCQ Assessment] ──(Score < 75%)──► [Rejection Email & Summary]
         │
         ├─(Score ≥ 75%)
         ▼
[Conflict-Free Slot Selection]
         │
         ▼
[Google Calendar Event Created + Google Meet Generated]
         │
         ▼
[Confirmation Email Dispatched + Result Confirmation Page]
```

---

## 📁 Project Structure

```
Automate_recruitment/
├── app.py                         # Main Flask application & routes
├── ai_recruitment_agent_team.py   # Streamlit application
├── config.py                      # Configuration template
├── config_local.py                # Local secret configuration (gitignored)
├── credentials.json               # Google OAuth 2.0 Client credentials (gitignored)
├── token.json                     # Google OAuth 2.0 user tokens (gitignored)
├── requirements_flask.txt         # Flask dependencies
├── requirements.txt               # Full project dependencies
├── roles.json                     # Job roles and criteria
├── mcqs.json                      # MCQ assessment question bank
├── predefined_times.json          # Available & booked interview slots
├── analytics.json                 # Candidate metrics and funnel analytics
├── templates/                     # Jinja2 HTML templates
│   ├── base.html                  # Base layout & navigation
│   ├── index.html                 # Candidate landing page
│   ├── candidate/                 # Candidate flow templates
│   │   ├── register.html
│   │   ├── apply.html
│   │   ├── test.html
│   │   ├── schedule.html
│   │   └── result.html
│   └── recruiter/                 # Recruiter management templates
│       ├── login.html
│       ├── dashboard.html
│       ├── manage_roles.html
│       ├── manage_mcqs.html
│       ├── manage_slots.html
│       ├── analytics.html
│       └── google_calendar.html   # Google OAuth 2.0 management
├── static/                        # CSS styles & static assets
└── utils/                         # Core utility packages
    ├── data_handler.py            # JSON persistence & slot locking
    ├── resume_analyzer.py         # AI & PDF parsing logic
    ├── email_sender.py            # SMTP dispatch routines
    └── google_calendar.py         # OAuth 2.0 Google Calendar & Meet engine
```

---

## 🛡️ Security Best Practices

- **Zero Credential Leaks:** `config_local.py`, `credentials.json`, `token.json`, and `.env` files are strictly excluded via `.gitignore`.
- **Protected Recruiter Routes:** All administrative views require active session authentication (`@login_required`).
- **Input Sanitization:** Resumes validated via file extension whitelists and safe filename handling (`secure_filename`).
- **Race Condition Guard:** Concurrency locking on interview slots prevents multiple candidates from reserving the same meeting time.

---

## 👨‍💻 Author

**Shiom Ghalme**
- GitHub: [@Shiom45Ghalme](https://github.com/Shiom45Ghalme)
- Email: [shiom.ghalme45@gmail.com](mailto:shiom.ghalme45@gmail.com)

---

## 📝 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
