"""
Email Sender Utility Module
Handles all email communications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_selection_email(sender_email: str, sender_password: str, receiver_email: str, 
                        role: str, company: str) -> None:
    """Send selection email to candidate after passing resume screening."""
    subject = f"Congratulations! You have been selected for the {role} role"
    body = f"""
Dear Candidate,

Congratulations! We are pleased to inform you that you have been selected for the role of {role} at {company}.

We believe you will be a great addition to the team, and we look forward to seeing the skills and expertise you will bring to this position.

Please prepare yourself by reviewing relevant skills for the {role} role. You will be contacted shortly with further instructions regarding your MCQ test.

Best regards,
{company} Recruitment Team
"""
    _send_email(sender_email, sender_password, receiver_email, subject, body)

def send_rejection_email(sender_email: str, sender_password: str, receiver_email: str, 
                        role: str, company: str) -> None:
    """Send rejection email to candidate."""
    subject = f"Regarding your application for the {role} role"
    body = f"""
Dear Candidate,

Thank you for your interest in the {role} role at {company}. 

Unfortunately, we regret to inform you that we will not be proceeding with your application at this time. Your resume or test score did not meet the minimum requirements for this position.

We encourage you to continue preparing and working hard to improve your skills. Feel free to apply again in the future.

Best regards,
{company} Recruitment Team
"""
    _send_email(sender_email, sender_password, receiver_email, subject, body)

def send_interview_email(sender_email: str, sender_password: str, candidate_email: str, 
                        recruiter_email: str, candidate_name: str, role: str, 
                        interview_slot: str, meeting_url: str, company: str) -> None:
    """Send interview confirmation email with Zoom link."""
    subject = f"Interview Scheduled - {role} at {company}"
    body = f"""
Dear {candidate_name},

Congratulations on passing the assessment! We are excited to invite you for an interview for the {role} position at {company}.

Interview Details:
- Role: {role}
- Date & Time: {interview_slot}
- Meeting Link: {meeting_url}

Please:
1. Join the meeting 5 minutes early
2. Ensure you have a stable internet connection
3. Keep your resume and portfolio ready
4. Prepare to discuss your experience and skills

If you have any questions or need to reschedule, please contact us at {recruiter_email}.

Best regards,
{company} Recruitment Team
"""
    _send_email(sender_email, sender_password, candidate_email, subject, body)
    
    # Also send copy to recruiter
    recruiter_subject = f"Interview Scheduled: {candidate_name} for {role}"
    recruiter_body = f"""
Interview Scheduled:

Candidate: {candidate_name}
Email: {candidate_email}
Role: {role}
Date & Time: {interview_slot}
Meeting Link: {meeting_url}

Best regards,
Recruitment System
"""
    _send_email(sender_email, sender_password, recruiter_email, recruiter_subject, recruiter_body)

def _send_email(sender_email: str, sender_password: str, receiver_email: str, 
                subject: str, body: str) -> None:
    """Internal function to send email via SMTP."""
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        
        logger.info(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        logger.error(f"Error sending email to {receiver_email}: {str(e)}")
        raise
