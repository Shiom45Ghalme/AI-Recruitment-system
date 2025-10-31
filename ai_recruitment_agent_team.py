from typing import Literal, Tuple, Dict, Optional
import time
import smtplib
import requests
import PyPDF2
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
import streamlit as st
import json
import os
import pytz
import pandas as pd
import matplotlib.pyplot as plt
from phi.tools.zoom import ZoomTool
from phi.utils.log import logger
from streamlit_pdf_viewer import pdf_viewer
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
FILE_PATH = "roles.json"
MCQS_FILE_PATH = "mcqs.json"
ANALYTICS_FILE_PATH = "analytics.json"
PREDEFINED_TIMES_PATH = "predefined_times.json"
PASSING_SCORE = 0.7

# Default roles
ROLE_REQUIREMENTS = {
    "ai_ml_engineer": """
        Required Skills:
        - Python, PyTorch/TensorFlow
        - Machine Learning algorithms and frameworks
        - Deep Learning and Neural Networks
        - Data preprocessing and analysis
        - MLOps and model deployment
        - RAG, LLM, Finetuning and Prompt Engineering
    """,
    "frontend_engineer": """
        Required Skills:
        - React/Vue.js/Angular
        - HTML5, CSS3, JavaScript/TypeScript
        - Responsive design
        - State management
        - Frontend testing
    """,
    "backend_engineer": """
        Required Skills:
        - Python/Java/Node.js
        - REST APIs
        - Database design and management
        - System architecture
        - Cloud services (AWS/GCP/Azure)
        - Kubernetes, Docker, CI/CD
    """
}

# ==================== UTILITY FUNCTIONS ====================

def validate_email(email: str) -> bool:
    """Validate email format."""
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None

def load_json_file(filepath: str, default_value: dict = None) -> dict:
    """Generic function to load JSON files with error handling."""
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data if data else (default_value or {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"File issue with {filepath}: {e}")
        return default_value or {}

def save_json_file(filepath: str, data: dict) -> bool:
    """Generic function to save JSON files with error handling."""
    try:
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving to {filepath}: {e}")
        return False

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting PDF text: {str(e)}")
        return ""

# ==================== SESSION STATE MANAGEMENT ====================

def init_session_state() -> None:
    """Initialize only necessary session state variables."""
    # Load from config_local if available
    try:
        from config_local import (EMAIL_SENDER, EMAIL_PASSWORD, RECRUITER_EMAIL, 
                                 ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET, 
                                 OPENAI_API_KEY, COMPANY_NAME)
    except ImportError:
        EMAIL_SENDER = EMAIL_PASSWORD = RECRUITER_EMAIL = ""
        ZOOM_ACCOUNT_ID = ZOOM_CLIENT_ID = ZOOM_CLIENT_SECRET = ""
        OPENAI_API_KEY = COMPANY_NAME = ""
    
    defaults = {
        'candidate_email': "", 'openai_api_key': OPENAI_API_KEY, 'recruiter_email': RECRUITER_EMAIL, 
        'resume_text': "", 'analysis_complete': False, 'is_selected': False, 
        'zoom_account_id': ZOOM_ACCOUNT_ID, 'zoom_client_id': ZOOM_CLIENT_ID,
        'zoom_client_secret': ZOOM_CLIENT_SECRET, 'email_sender': EMAIL_SENDER,
        'email_passkey': EMAIL_PASSWORD, 'company_name': COMPANY_NAME, 'current_pdf': None,
        'time_change_requested': False, 'scheduled_datetime': None, 'proceed_app': False, 
        'test_conducted': False, 'check_it': False, 'no_button': False, 'time_and_date': False,
        'check_again': False, 'fragment': False, 'go_ahead': False, 'session_to_proceed': False,
        'show_analytics': False, 'custom_roles': {}
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def reset_application_state(role: str = None):
    """Reset application-specific session state."""
    reset_flags = ['fragment', 'check_it', 'analysis_complete', 'is_selected', 'proceed_app',
                   'test_conducted', 'time_change_requested', 'go_ahead', 'session_to_proceed',
                   'check_again', 'no_button', 'time_and_date']
    for flag in reset_flags:
        st.session_state[flag] = False
    for key in ['resume_text', 'candidate_email', 'current_pdf']:
        st.session_state[key] = None if key == 'current_pdf' else ""
    if role:
        test_state_key = f"{role}_test_state"
        if test_state_key in st.session_state:
            st.session_state[test_state_key] = {"progress": 0, "answers": [], "completed": False}

# ==================== ANALYTICS FUNCTIONS ====================

def update_analytics(role: str, test_result: bool):
    """Update analytics.json with test results."""
    try:
        data = load_json_file(ANALYTICS_FILE_PATH, {"roles": {}, "interviews": []})
        if role not in data["roles"]:
            data["roles"][role] = {"total_applicants": 0, "selected_for_test": 0, "passed": 0, "failed": 0}
        data["roles"][role]["selected_for_test"] += 1
        data["roles"][role]["passed" if test_result else "failed"] += 1
        save_json_file(ANALYTICS_FILE_PATH, data)
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")

def increment_total_applicants(role: str):
    """Increment total applicants count for a role."""
    try:
        data = load_json_file(ANALYTICS_FILE_PATH, {"roles": {}, "interviews": []})
        if role not in data["roles"]:
            data["roles"][role] = {"total_applicants": 0, "selected_for_test": 0, "passed": 0, "failed": 0}
        data["roles"][role]["total_applicants"] += 1
        save_json_file(ANALYTICS_FILE_PATH, data)
    except Exception as e:
        logger.error(f"Error incrementing applicants: {e}")

def display_analytics():
    """Display analytics dashboard."""
    analytics_data = load_json_file(ANALYTICS_FILE_PATH)
    if not analytics_data or not analytics_data.get("roles"):
        st.warning("No analytics data available.")
        return
    
    role_df = pd.DataFrame(analytics_data["roles"]).T.reset_index().rename(columns={"index": "Role"})
    
    st.subheader("Role-Based Analytics")
    st.table(role_df)
    
    # Bar graph
    fig, ax = plt.subplots(figsize=(10, 6))
    role_df.set_index("Role")[["total_applicants", "selected_for_test", "passed", "failed"]].plot(
        kind="bar", ax=ax, color=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
    plt.title("Applicants Breakdown by Role")
    plt.xlabel("Roles")
    plt.ylabel("Number of Applicants")
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Pie chart
    if role_df["total_applicants"].sum() > 0:
        fig, ax = plt.subplots(figsize=(8, 8))
        role_df.set_index("Role")["total_applicants"].plot.pie(ax=ax, autopct='%1.1f%%')
        plt.title("Total Applicants by Role")
        st.pyplot(fig)

# ==================== ROLE MANAGEMENT ====================

def load_roles() -> dict:
    return load_json_file(FILE_PATH, {})

def save_roles(roles: dict) -> bool:
    return save_json_file(FILE_PATH, roles)

def load_mcqs(role_choice: str = ""):
    mcqs_data = load_json_file(MCQS_FILE_PATH, {})
    return mcqs_data.get(role_choice, []) if role_choice else mcqs_data

def save_mcqs(role_choice: str, role_mcqs: list) -> bool:
    mcqs_data = load_json_file(MCQS_FILE_PATH, {})
    mcqs_data[role_choice] = role_mcqs
    return save_json_file(MCQS_FILE_PATH, mcqs_data)

def manage_roles():
    """Manage roles with add, edit, delete functionality."""
    roles = load_roles()
    if not roles:
        roles = ROLE_REQUIREMENTS.copy()
        save_roles(roles)
    
    if "custom_roles" not in st.session_state or not st.session_state["custom_roles"]:
        st.session_state["custom_roles"] = roles
    
    st.sidebar.subheader("Modify or Add Role Criteria")

    role_choice = st.selectbox(
        "Select a role to modify or add:",
        list(st.session_state["custom_roles"].keys()) + ["Add New Role"]
    )

    if role_choice == "Add New Role":
        existing_roles_in_mcqs = list(load_mcqs().keys())
        existing_roles_in_json = list(st.session_state["custom_roles"].keys())
        suggested_roles = [role for role in existing_roles_in_mcqs if role not in existing_roles_in_json]

        new_role = st.text_input("Enter the name of the new role:")

        if suggested_roles:
            st.write("Following Roles Already have MCQs (type similar spelling to access those):")
            st.write(", ".join(suggested_roles))

        st.write("If your role is not listed, you can type a new role name.")

        if new_role:
            if new_role in existing_roles_in_json:
                st.warning(f"Role '{new_role}' already exists in the roles file.")
                new_criteria = st.text_area("Enter the criteria for the new role:")
                if st.button("Add Role"):
                    st.session_state["custom_roles"][new_role] = new_criteria
                    save_roles(st.session_state["custom_roles"])
                    st.success(f"New role '{new_role}' added successfully.")
                    st.rerun()
            elif new_role in existing_roles_in_mcqs:
                st.warning(f"Role '{new_role}' already exists in the MCQs file.")
                new_criteria = st.text_area("Enter the criteria for the new role:", 
                                          value="Enter Criteria for role", height=150)
                if st.button("Add Role"):
                    st.session_state["custom_roles"][new_role] = new_criteria
                    save_roles(st.session_state["custom_roles"])
                    st.success(f"New role '{new_role}' added successfully with existing MCQs.")
            else:
                new_criteria = st.text_area("Enter the criteria for the new role:")
                if st.button("Add Role"):
                    if not new_role.strip():
                        st.error("Role name cannot be empty.")
                    elif not new_criteria.strip():
                        st.error("Please provide criteria for the new role.")
                    else:
                        st.session_state["custom_roles"][new_role] = new_criteria
                        save_roles(st.session_state["custom_roles"])
                        st.success(f"New role '{new_role}' added successfully.")
                        st.rerun()
    else:
        st.markdown(f"### Current Criteria for {role_choice}:")
        st.text_area("", value=st.session_state["custom_roles"][role_choice], 
                    height=150, disabled=True)

        new_criteria = st.text_area(
            f"Modify the criteria for {role_choice}:",
            value=st.session_state["custom_roles"][role_choice]
        )
        
        if st.button("Save Changes"):
            if not new_criteria.strip():
                st.error("Criteria cannot be empty.")
            else:
                st.session_state["custom_roles"][role_choice] = new_criteria
                save_roles(st.session_state["custom_roles"])
                st.success(f"Criteria for '{role_choice}' updated successfully.")
                st.rerun()

        if st.button("Delete Role"):
            del st.session_state["custom_roles"][role_choice]
            save_roles(st.session_state["custom_roles"])
            st.success(f"Role '{role_choice}' deleted successfully.")
            st.warning(f"Role '{role_choice}' MCQs are kept in the system.")
            st.rerun()

        if role_choice != "Add New Role":
            edit_mcq_questions(role_choice)
            add_mcq_question(role_choice)

    if not st.session_state["custom_roles"]:
        st.session_state["custom_roles"] = ROLE_REQUIREMENTS.copy()
        save_roles(st.session_state["custom_roles"])

    return st.session_state["custom_roles"]

def edit_mcq_questions(role_choice: str):
    """Edit MCQs for the selected role."""
    role_mcqs = load_mcqs(role_choice)
    
    st.subheader(f"Existing MCQs for {role_choice}")
    
    if not role_mcqs:
        st.write("No questions found for this role.")
        return
    
    for idx, question in enumerate(role_mcqs):
        st.markdown(f"### Question {idx + 1}")
        st.write(f"**Q:** {question['question']}")
        st.write(f"**Options:** {', '.join(question['options'])}")
        
        answer = question.get('answer', 'No answer set')
        st.write(f"**Answer:** {answer}")
        
        with st.expander(f"Edit Question {idx + 1}"):
            new_question = st.text_input(f"Edit Question {idx + 1}: ", 
                                        value=question['question'], key=f"question_{idx}")
            new_options = [st.text_input(f"Option {i + 1}: ", value=opt, 
                                        key=f"option_{idx}_{i}") 
                          for i, opt in enumerate(question['options'])]
            new_answer = st.selectbox(f"Select Correct Answer for Question {idx + 1}", 
                                     new_options, key=f"answer_{idx}")
            
            if st.button(f"Save Changes to Question {idx + 1}", key=f"save_{idx}"):
                if not new_question.strip() or not new_options or not new_answer.strip():
                    st.error("Please fill in all fields correctly.")
                else:
                    role_mcqs[idx] = {
                        "question": new_question,
                        "options": new_options,
                        "answer": new_answer
                    }
                    save_mcqs(role_choice, role_mcqs)
                    st.success(f"Question {idx + 1} updated successfully.")
                    st.rerun()
        
            if st.button(f"Delete Question {idx + 1}", key=f"delete_{idx}"):
                role_mcqs.pop(idx)
                save_mcqs(role_choice, role_mcqs)
                st.success(f"Question {idx + 1} deleted successfully.")
                st.rerun()

def add_mcq_question(role_choice: str):
    """Add a new MCQ question for the selected role."""
    st.sidebar.subheader(f"Add New MCQ for {role_choice}")
    
    new_question = st.text_input("Enter the new question:", key=f"new_question_{role_choice}")
    
    option_1 = st.text_input("Option 1:", key=f"option_1_{role_choice}")
    option_2 = st.text_input("Option 2:", key=f"option_2_{role_choice}")
    option_3 = st.text_input("Option 3:", key=f"option_3_{role_choice}")
    option_4 = st.text_input("Option 4:", key=f"option_4_{role_choice}")

    correct_option = st.selectbox(
        "Select the correct option:",
        ["Option 1", "Option 2", "Option 3", "Option 4"],
        key=f"correct_option_{role_choice}"
    )

    if st.button("Add MCQ"):
        if not all([new_question, option_1, option_2, option_3, option_4]):
            st.error("Please fill in all fields before adding the MCQ.")
        else:
            mcq_question = {
                "question": new_question,
                "options": [option_1, option_2, option_3, option_4],
                "answer": correct_option
            }

            role_mcqs = load_mcqs(role_choice)
            role_mcqs.append(mcq_question)
            save_mcqs(role_choice, role_mcqs)
            st.success(f"MCQ added for role '{role_choice}' successfully!")
            st.rerun()

# ==================== SCHEDULING FUNCTIONS ====================

def schedule_meeting():
    """Allow user to input date and time for scheduling."""
    st.sidebar.subheader("Schedule Meeting")

    meeting_date = st.date_input("Select Meeting Date:")
    meeting_time = st.time_input("Select Meeting Time:")

    if meeting_date and meeting_time:
        scheduled_datetime = datetime.combine(meeting_date, meeting_time)
        st.session_state["scheduled_datetime"] = scheduled_datetime
        st.success(f"Meeting scheduled for: {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')}")

    if "scheduled_datetime" in st.session_state:
        st.sidebar.info(
            f"Scheduled Meeting:\n{st.session_state['scheduled_datetime'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

def update_meeting_schedule():
    """Update meeting schedule from predefined times."""
    st.sidebar.subheader("Update Meeting Schedule")

    predefined_data = load_json_file(PREDEFINED_TIMES_PATH, {"available_times": []})
    available_times = predefined_data.get("available_times", [])
    
    if not available_times:
        st.warning("No predefined times available.")
        return
    
    available_times_formatted = [datetime.strptime(t, "%Y-%m-%d %H:%M:%S") 
                                for t in available_times]

    selected_time = st.selectbox(
        "Select a new meeting date and time:",
        options=available_times_formatted,
        format_func=lambda x: x.strftime("%Y-%m-%d %H:%M:%S"),
    )

    if selected_time:
        if ("scheduled_datetime" not in st.session_state or 
            st.session_state["scheduled_datetime"] != selected_time):
            st.session_state["scheduled_datetime"] = selected_time
            st.success(f"Meeting updated to: {selected_time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            st.info("No changes made to the meeting schedule.")

    if "scheduled_datetime" in st.session_state:
        st.sidebar.info(
            f"Updated Meeting:\n"
            f"{st.session_state['scheduled_datetime'].strftime('%Y-%m-%d %H:%M:%S')}"
        )

def ask_for_time_change() -> bool:
    """Ask candidate if they want to change interview time."""
    if "time_change_requested" not in st.session_state:
        st.session_state.time_change_requested = False

    current_time = st.session_state.get("scheduled_datetime")
    if not current_time:
        st.warning("No interview time assigned by the recruiter yet.")
        return False

    st.write(f"Current interview time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")

    change_time = st.radio("Would you like to change the interview time?", 
                          ["No", "Yes"], index=0, key="change_time_radio")
    
    if change_time == "Yes":
        st.session_state.time_change_requested = True
    elif change_time == "No":
        st.session_state.time_change_requested = False
        st.write("You have opted to keep the original scheduled time.")

    return st.session_state.time_change_requested

def manage_interview_slots():
    """Manage available interview slots."""
    st.sidebar.subheader("Manage Interview Slots")
    st.subheader("Available Slots for Self-Scheduling Interviews")

    if "available_times" not in st.session_state:
        predefined_data = load_json_file(PREDEFINED_TIMES_PATH, {"available_times": []})
        st.session_state.available_times = predefined_data.get("available_times", [])

    st.write("Current Available Slots:")
    for i, slot in enumerate(st.session_state.available_times):
        st.write(f"{i + 1}. {slot}")

    with st.form("add_slot_form"):
        st.write("Add a New Slot")
        new_date = st.date_input("New Slot Date:", key="add_date")
        new_time = st.time_input("New Slot Time:", key="add_time")
        add_slot = st.form_submit_button("Add Slot")

        if add_slot and new_date and new_time:
            new_slot = f"{new_date} {new_time}"
            if new_slot not in st.session_state.available_times:
                st.session_state.available_times.append(new_slot)
                save_json_file(PREDEFINED_TIMES_PATH, 
                             {"available_times": st.session_state.available_times})
                st.success(f"Slot {new_slot} added successfully!")
                st.rerun()
            else:
                st.warning("This slot already exists.")
    
    if st.session_state.available_times:
        st.write("Remove an Existing Slot")
        with st.form("remove_slot_form"):
            slot_to_remove = st.selectbox("Select Slot to Remove:", 
                                         options=st.session_state.available_times, 
                                         key="remove_slot")
            remove_slot = st.form_submit_button("Remove Slot")

            if remove_slot and slot_to_remove:
                st.session_state.available_times.remove(slot_to_remove)
                save_json_file(PREDEFINED_TIMES_PATH, 
                             {"available_times": st.session_state.available_times})
                st.success(f"Slot {slot_to_remove} removed successfully!")
                st.rerun()
    else:
        st.info("Add time slots for self-scheduling.")

    st.write("Changes saved successfully!")

# ==================== EMAIL FUNCTIONS ====================

def send_selection_email(sender_email, sender_password, receiver_email, role, company) -> None:
    subject = f"Congratulations! You have been selected for the {role} role"
    body = f"""
    Dear Candidate,
    
    Congratulations! We are pleased to inform you that you have been selected for the role of {role} at {company}.
    
    We believe you will be a great addition to the team, and we look forward to seeing the skills and expertise you will bring to this position.
    
    Please prepare yourself by reviewing relevant skills for the {role} role. You will be contacted shortly with further instructions regarding your start date and other preparations.
    
    Additionally, we will schedule a Zoom meeting soon to discuss the next steps and answer any questions you may have.
    
    Best regards,
    {company}
    """
    msg = MIMEText(body, 'plain', 'utf-8')
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

def send_rejection_email(sender_email, sender_password, receiver_email, role, company) -> None:
    subject = f"Regarding your application for the {role} role"
    body = f"""
    Dear Candidate,
    
    Thank you for your interest in the {role} role at {company}. Unfortunately, we regret to inform you that we will not be proceeding with your application at this time.
    
    We encourage you to continue preparing and working hard to improve your skills.
    
    Best regards,
    {company}
    """
    msg = MIMEText(body, 'plain', 'utf-8')
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())

# ==================== ZOOM INTEGRATION ====================

class CustomZoomTool(ZoomTool):
    """Custom Zoom tool with OAuth token management."""
    def __init__(self, *, account_id: Optional[str] = None, client_id: Optional[str] = None, 
                 client_secret: Optional[str] = None, name: str = "zoom_tool"):
        super().__init__(account_id=account_id, client_id=client_id, client_secret=client_secret, name=name)
        self.token_url = "https://zoom.us/oauth/token"
        self.access_token = None
        self.token_expires_at = 0

    def get_access_token(self) -> str:
        if self.access_token and time.time() < self.token_expires_at:
            return str(self.access_token)
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {"grant_type": "account_credentials", "account_id": self.account_id}

        try:
            response = requests.post(self.token_url, headers=headers, data=data, 
                                   auth=(self.client_id, self.client_secret))
            response.raise_for_status()

            token_info = response.json()
            self.access_token = token_info["access_token"]
            expires_in = token_info["expires_in"]
            self.token_expires_at = time.time() + expires_in - 60

            self._set_parent_token(str(self.access_token))
            return str(self.access_token)

        except requests.RequestException as e:
            logger.error(f"Error fetching access token: {e}")
            return ""

    def _set_parent_token(self, token: str) -> None:
        """Set token in parent ZoomTool class."""
        if token:
            self._ZoomTool__access_token = token

def schedule_interview(zoom_acc_id: str, zoom_client_id: str, zoom_secret: str, sender_email: str,
                      sender_password: str, receiver_email: str, recruiter_email: str, role: str,
                      company: str, local_timezone: str) -> bool:
    """Schedule Zoom interview and send emails."""
    try:
        if "scheduled_datetime" not in st.session_state:
            st.error("Please schedule a date and time for the interview first!")
            return False
        
        scheduled_datetime = st.session_state['scheduled_datetime']
        st.write(f"Your interview is scheduled for {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')} ({local_timezone})")
        
        # Convert to UTC
        local_tz = pytz.timezone(local_timezone)
        local_dt = local_tz.localize(scheduled_datetime, is_dst=None)
        utc_dt = local_dt.astimezone(pytz.utc)
        meeting_time_iso = utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        # Get Zoom token
        zoom_token_url = "https://zoom.us/oauth/token"
        token_response = requests.post(zoom_token_url, 
                                      data={'grant_type': 'account_credentials', 'account_id': zoom_acc_id},
                                      auth=(zoom_client_id, zoom_secret))
        token_response.raise_for_status()
        access_token = token_response.json().get('access_token')
        
        if not access_token:
            raise ValueError("Failed to fetch Zoom access token.")
        
        # Create Zoom meeting
        meeting_details = {
            "topic": f"Interview for {role}",
            "type": 2,
            "start_time": meeting_time_iso,
            "duration": 60,
            "timezone": "UTC",
            "settings": {"join_before_host": True, "waiting_room": False}
        }
        meeting_response = requests.post("https://api.zoom.us/v2/users/me/meetings",
                                        json=meeting_details,
                                        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"})
        meeting_response.raise_for_status()
        meeting_link = meeting_response.json().get('join_url')
        
        if not meeting_link:
            raise ValueError("Failed to schedule Zoom meeting.")
        
        # Send email
        subject = f"Interview Scheduled for {role} at {company}"
        body = f"""Dear Candidate,

Your interview for {role} at {company} has been scheduled.

Meeting Details:
- Link: {meeting_link}
- Date: {scheduled_datetime.strftime('%Y-%m-%d')}
- Time: {scheduled_datetime.strftime('%H:%M:%S')} ({local_timezone})

Best regards,
{company} Hiring Team"""
        
        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = ", ".join([receiver_email, recruiter_email])
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(message)
        
        # Update analytics
        analytics_data = load_json_file(ANALYTICS_FILE_PATH, {"roles": {}, "interviews": []})
        analytics_data["interviews"].append({
            "email": receiver_email,
            "role": role,
            "time": scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S'),
            "link": meeting_link
        })
        save_json_file(ANALYTICS_FILE_PATH, analytics_data)
        
        st.success("Interview scheduled successfully!")
        logger.info(f"Interview scheduled for {receiver_email} - {role}")
        return True
    except Exception as e:
        logger.error(f"Error scheduling interview: {e}")
        st.error("Unable to schedule interview. Please try again.")
        return False

# ==================== ASSESSMENT FUNCTIONS ====================

def analyze_resume(resume_text: str, role) -> Tuple[bool, str]:
    try:
        # Manual response - your working version
        response = {
            "selected": True,
            "feedback": "The candidate meets over 70% of the required skills for the role...",
            "matching_skills": ["Python", "Machine Learning", "Deep Learning", "Flask Framework", "DBMS", "C++"],
            "missing_skills": ["TensorFlow", "PyTorch", "Natural Language Processing", "Cloud Computing", "DevOps"],
            "experience_level": "junior"
        }
        return response["selected"], response["feedback"]
    except Exception as e:
        return False, f"Error analyzing resume: {str(e)}"

def conduct_test_and_evaluate(role_choice: str) -> Optional[bool]:
    """Conduct assessment test and return pass/fail result."""
    role_mcqs = load_mcqs(role_choice)
    if not role_mcqs:
        st.error("No MCQs available for this role.")
        return True
    
    test_state_key = f"{role_choice}_test_state"
    if test_state_key not in st.session_state:
        st.session_state[test_state_key] = {"progress": 0, "answers": [], "completed": False}
    
    test_state = st.session_state[test_state_key]
    progress = test_state["progress"]
    
    if not test_state["completed"]:
        current_question = role_mcqs[progress]
        st.write(f"Question {progress + 1}: {current_question['question']}")
        selected_option = st.radio("Choose your answer:", current_question['options'],
                                   key=f"{role_choice}_test_question_{progress}")
        
        if st.button("Submit Answer", key=f"{role_choice}_submit_button_{progress}"):
            if not selected_option:
                st.warning("Please select an answer before proceeding.")
            else:
                test_state["answers"].append(selected_option)
                if progress + 1 < len(role_mcqs):
                    test_state["progress"] += 1
                else:
                    test_state["completed"] = True
                st.rerun()
        return None
    
    if test_state["completed"]:
        correct_answers = sum(1 for i, mcq in enumerate(role_mcqs) if mcq["answer"] == test_state["answers"][i])
        score_percentage = (correct_answers / len(role_mcqs)) * 100
        
        st.write(f"Test completed! You answered {correct_answers} out of {len(role_mcqs)} correctly.")
        st.write(f"Your score: {score_percentage:.2f}%")
        st.session_state.test_conducted = True
        
        if score_percentage >= (PASSING_SCORE * 100):
            st.success("You have passed the test!")
            return True
        else:
            st.error("You did not pass the test.")
            return False

# ==================== MAIN APPLICATION ====================

def main() -> None:
    st.title("AI Recruitment System")
    init_session_state()
    
    with st.sidebar:
        st.header("Configuration")
        
        # Toggle Analytics Button
        if st.sidebar.button("Show Analytics" if not st.session_state["show_analytics"] else "Back to Recruitment"):
            st.session_state["show_analytics"] = not st.session_state["show_analytics"]
            st.rerun()
        
        st.subheader("OpenAI Settings")
        api_key = st.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key, help="Get your API key from platform.openai.com")
        if api_key: 
            st.session_state.openai_api_key = api_key

        st.subheader("Zoom Settings")
        zoom_account_id = st.text_input("Zoom Account ID", type="password", value=st.session_state.zoom_account_id)
        zoom_client_id = st.text_input("Zoom Client ID", type="password", value=st.session_state.zoom_client_id)
        zoom_client_secret = st.text_input("Zoom Client Secret", type="password", value=st.session_state.zoom_client_secret)
        
        st.subheader("Email Settings")
        email_sender = st.text_input("Sender Email", value=st.session_state.email_sender, help="Email address to send from")
        recruiter_email = st.text_input("Recruiter Email", value=st.session_state.recruiter_email, help="Email address to send to as a recruiter")
        email_passkey = st.text_input("Email App Password", type="password", value=st.session_state.email_passkey, help="App-specific password for email")
        company_name = st.text_input("Company Name", value=st.session_state.company_name, help="Name to use in email communications")

        # Update session state (REMOVED HARDCODED DEFAULTS)
        if zoom_account_id:
            st.session_state.zoom_account_id = zoom_account_id
        if zoom_client_id:
            st.session_state.zoom_client_id = zoom_client_id
        if zoom_client_secret:
            st.session_state.zoom_client_secret = zoom_client_secret
        if email_sender:
            st.session_state.email_sender = email_sender
        if email_passkey:
            st.session_state.email_passkey = email_passkey
        if company_name:
            st.session_state.company_name = company_name
        if recruiter_email:
            st.session_state.recruiter_email = recruiter_email

        # Role Management
        final_roles = manage_roles()
        
        # Scheduling
        schedule_meeting()
        manage_interview_slots()
        
        # Required configurations check
        required_configs = {
            'OpenAI API Key': st.session_state.openai_api_key,
            'Zoom Account ID': st.session_state.zoom_account_id,
            'Zoom Client ID': st.session_state.zoom_client_id,
            'Zoom Client Secret': st.session_state.zoom_client_secret,
            'Email Sender': st.session_state.email_sender,
            'Email Password': st.session_state.email_passkey,
            'Company Name': st.session_state.company_name
        }

    # Show Analytics if toggled
    if st.session_state["show_analytics"]:
        display_analytics()
        return

    # Check required configurations
    missing_configs = [k for k, v in required_configs.items() if not v]
    if missing_configs:
        st.warning(f"Please configure the following in the sidebar: {', '.join(missing_configs)}")
        return

    if not st.session_state.openai_api_key:
        st.warning("Please enter your OpenAI API key in the sidebar to continue.")
        return
    
    # Role selection
    role = st.selectbox("Select the role you're applying for:", list(final_roles.keys()))
    with st.expander("View Required Skills", expanded=True):
        st.markdown(final_roles[role])

    # New Application button
    if st.button("📝 New Application"):
        reset_application_state(role)
        st.rerun()

    # Resume upload
    resume_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"], key="resume_uploader")
    
    if resume_file is not None and resume_file != st.session_state.get('current_pdf'):
        st.session_state.current_pdf = resume_file
        st.session_state.resume_text = ""
        st.session_state.analysis_complete = False
        st.session_state.is_selected = False
        st.rerun()

    # Display uploaded resume
    if resume_file:
        st.subheader("Uploaded Resume")
        col1, col2 = st.columns([4, 1])
        
        with col1:
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(resume_file.read())
                tmp_file_path = tmp_file.name
            resume_file.seek(0)
            try:
                pdf_viewer(tmp_file_path)
            finally:
                os.unlink(tmp_file_path)
        
        with col2:
            st.download_button(label="📥 Download", data=resume_file, file_name=resume_file.name, mime="application/pdf")
        
        # Process resume text
        if not st.session_state.resume_text:
            with st.spinner("Processing your resume..."):
                resume_text = extract_text_from_pdf(resume_file)
                if resume_text:
                    st.session_state.resume_text = resume_text
                    st.success("Resume processed successfully!")
                else:
                    st.error("Could not process the PDF. Please try again.")

    # Email input
    email_can = st.text_input("Candidate's email address", value=st.session_state.candidate_email, key="email_input")
    
    if email_can:
        if validate_email(email_can):
            st.session_state.candidate_email = email_can
        else:
            st.error("Please enter a valid email address.")
            st.session_state.candidate_email = ""
    else:
        st.session_state.candidate_email = ""

    # Analyze Resume
    if (st.session_state.resume_text and st.session_state.candidate_email and 
        not st.session_state.analysis_complete):
        if st.button("Analyze Resume"):
            with st.spinner("Analyzing your resume..."):
                is_selected, feedback = analyze_resume(st.session_state.resume_text, role)
                
                # Update total applicants
                increment_total_applicants(role)

                if is_selected:
                    st.success("Congratulations! Your skills match our requirements.")
                    st.session_state.analysis_complete = True
                    st.session_state.is_selected = True
                    st.rerun()
                else:
                    st.warning("Unfortunately, your skills don't match our requirements.")
                    st.write(f"Feedback: {feedback}")
                    
                    # Send rejection email
                    with st.spinner("Sending feedback email..."):
                        try:
                            send_rejection_email(
                                st.session_state.get('email_sender'),
                                st.session_state.get('email_passkey'), 
                                st.session_state.get('candidate_email'),
                                role, 
                                st.session_state.get('company_name'))
                            st.info("We've sent you an email with detailed feedback.")
                        except Exception as e:
                            logger.error(f"Error sending rejection email: {e}")
                            st.error("Could not send feedback email. Please try again.")

    # Conduct test if selected
    if (st.session_state.get('analysis_complete') and st.session_state.get('is_selected', False) and 
        not st.session_state.get('proceed_app')):
        test_result = conduct_test_and_evaluate(role)
        if test_result is not None:
            st.session_state.go_ahead = test_result

    # Handle test failure
    if (st.session_state.get('test_conducted') and not st.session_state.get('go_ahead') and 
        st.session_state.get('is_selected', False)):
        st.error("You need to pass the test to proceed with the application.")
        st.info("Unfortunately we are unable to proceed.")
        with st.spinner("Sending feedback email..."):
            try:
                send_rejection_email(
                    st.session_state.get('email_sender'),
                    st.session_state.get('email_passkey'), 
                    st.session_state.get('candidate_email'),
                    role, 
                    st.session_state.get('company_name'))
                test_state_key = f"{role}_test_state"
                if test_state_key in st.session_state:
                    st.session_state[test_state_key] = {"progress": 0, "answers": [], "completed": False}
                st.info("We've sent you an email with detailed feedback.")
                update_analytics(role, st.session_state.get('go_ahead'))
            except Exception as e:
                logger.error(f"Error sending rejection email: {e}")
                st.error("Could not send feedback email. Please try again.")

    # Proceed with application if test passed
    if (st.session_state.get('test_conducted') and st.session_state.get('analysis_complete') and 
        st.session_state.get('is_selected', False) and st.session_state.go_ahead and 
        not st.session_state.get('session_to_proceed')):
        st.success("Congratulations! You have passed the test")
        st.info("Click 'Proceed with Application' to continue with the interview process.")
        
        if st.button("Proceed with Application", key="proceed_button"):
            with st.spinner("🔄 Processing your application..."):
                try:
                    # Send selection email
                    with st.status("📧 Sending confirmation email...", expanded=True) as status:
                        send_selection_email(
                            st.session_state.get('email_sender'),
                            st.session_state.get('email_passkey'),
                            st.session_state.get('candidate_email'), 
                            role, 
                            st.session_state.get('company_name'))
                        status.update(label="✅ Confirmation email sent!")

                    st.session_state.session_to_proceed = True
                    st.session_state.proceed_app = True
                    
                    # Schedule interview
                    with st.status("📅 Scheduling interview...", expanded=True):
                        pass

                    st.rerun()

                except Exception as e:
                    logger.error(f"Error in application processing: {e}")
                    st.error(f"An error occurred: {str(e)}")
                    st.error("Please try again or contact support.")

    # Ask for time change
    if not st.session_state.get('no_button') and st.session_state.get('proceed_app'):
        st.success("Confirmation email sent successfully!")
        st.info("Schedule interview time out of given time!")
        st.session_state.time_change_requested = ask_for_time_change()
        st.session_state.check_again = True

    # Update meeting schedule if requested
    if st.session_state.get('time_change_requested') and not st.session_state.get('time_and_date'):
        st.session_state.check_it = True
        update_meeting_schedule() 
    else:
        st.session_state.check_it = True

    # Proceed with schedule
    if (st.session_state.get('check_it') and st.session_state.get('check_again') and 
        not st.session_state.get('fragment')):
        if st.button("Proceed with Schedule", key="schedule_button"):
            st.session_state.no_button = True
            st.session_state.time_and_date = True
            schedule_interview(
                st.session_state.get('zoom_account_id'),
                st.session_state.get('zoom_client_id'),
                st.session_state.get('zoom_client_secret'),
                st.session_state.get('email_sender'),
                st.session_state.get('email_passkey'),
                st.session_state.get('candidate_email'),
                st.session_state.get('recruiter_email'),
                role,
                st.session_state.get('company_name'),
                "UTC"
            )
            st.session_state.fragment = True
            st.rerun()

    # Final success message
    if st.session_state.get('fragment'):
        update_analytics(role, st.session_state.get('go_ahead'))
        test_state_key = f"{role}_test_state"
        if test_state_key in st.session_state:
            st.session_state[test_state_key] = {"progress": 0, "answers": [], "completed": False}
        st.success("Interview scheduled successfully! Check your email for details.")
        st.info("Interview scheduled and email sent successfully.")
        st.success("""
            🎉 Application Successfully Processed!
            
            Please check your email for:
            1. Selection confirmation ✅
            2. Interview details with Zoom link 🔗
            
            Next steps:
            1. Review the role requirements
            2. Prepare for your technical interview
            3. Join the interview 5 minutes early
        """)

    # Reset Application button
    if st.sidebar.button("Reset Application"):
        for key in list(st.session_state.keys()):
            if key != 'openai_api_key':
                del st.session_state[key]
        
        # Reset analytics
        roles_data = load_roles()
        initial_data = {"roles": {}, "interviews": []}
        
        for role_key in roles_data:
            formatted_role = role_key.replace('_', ' ').title()
            initial_data["roles"][formatted_role] = {
                "total_applicants": 0,
                "selected_for_test": 0,
                "passed": 0,
                "failed": 0
            }
        
        save_json_file(ANALYTICS_FILE_PATH, initial_data)
        st.rerun()

if __name__ == "__main__":
    main()