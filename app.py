from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from functools import wraps
import os
import logging
from datetime import datetime, timedelta
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import utility modules
from utils.resume_analyzer import analyze_resume_text, extract_text_from_pdf
from utils.email_sender import send_selection_email, send_rejection_email, send_interview_email
from utils.zoom_integration import schedule_zoom_meeting
from utils.data_handler import (
    load_json_file, save_json_file, 
    load_roles, save_roles, 
    load_mcqs, save_mcqs,
    load_analytics, update_analytics, increment_total_applicants
)

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Load configuration
try:
    from config_local import (
        EMAIL_SENDER, EMAIL_PASSWORD, RECRUITER_EMAIL,
        ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET,
        OPENAI_API_KEY, COMPANY_NAME
    )
except ImportError:
    EMAIL_SENDER = EMAIL_PASSWORD = RECRUITER_EMAIL = ""
    ZOOM_ACCOUNT_ID = ZOOM_CLIENT_ID = ZOOM_CLIENT_SECRET = ""
    OPENAI_API_KEY = COMPANY_NAME = ""

# Constants
PASSING_SCORE = 0.75  # 75%
RESUME_MATCH_THRESHOLD = 0.50  # 50%

# ==================== HELPER FUNCTIONS ====================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def login_required(f):
    """Decorator to require login for recruiter routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'recruiter_logged_in' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('recruiter_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Landing page with options for candidate and recruiter."""
    return render_template('index.html')

# ==================== RECRUITER ROUTES ====================

@app.route('/recruiter/login', methods=['GET', 'POST'])
def recruiter_login():
    """Recruiter login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (in production, use proper user database)
        if username == 'admin' and password == 'admin123':
            session['recruiter_logged_in'] = True
            session['recruiter_username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('recruiter_dashboard'))
        else:
            flash('Invalid credentials. Try again.', 'danger')
    
    return render_template('recruiter/login.html')

@app.route('/recruiter/logout')
def recruiter_logout():
    """Logout recruiter."""
    session.pop('recruiter_logged_in', None)
    session.pop('recruiter_username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/recruiter/dashboard')
@login_required
def recruiter_dashboard():
    """Recruiter dashboard."""
    roles = load_roles()
    analytics = load_analytics()
    return render_template('recruiter/dashboard.html', roles=roles, analytics=analytics)

@app.route('/recruiter/roles', methods=['GET', 'POST'])
@login_required
def manage_roles():
    """Manage job roles."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            role_name = request.form.get('role_name')
            role_criteria = request.form.get('role_criteria')
            
            roles = load_roles()
            roles[role_name] = role_criteria
            save_roles(roles)
            
            flash(f'Role "{role_name}" added successfully!', 'success')
        
        elif action == 'edit':
            old_role_name = request.form.get('old_role_name')
            new_role_name = request.form.get('role_name')
            role_criteria = request.form.get('role_criteria')
            
            roles = load_roles()
            if old_role_name in roles:
                del roles[old_role_name]
            roles[new_role_name] = role_criteria
            save_roles(roles)
            
            flash(f'Role "{new_role_name}" updated successfully!', 'success')
        
        elif action == 'delete':
            role_name = request.form.get('role_name')
            roles = load_roles()
            if role_name in roles:
                del roles[role_name]
                save_roles(roles)
                flash(f'Role "{role_name}" deleted successfully!', 'success')
        
        return redirect(url_for('manage_roles'))
    
    roles = load_roles()
    return render_template('recruiter/manage_roles.html', roles=roles)

@app.route('/recruiter/mcqs/<role>', methods=['GET', 'POST'])
@login_required
def manage_mcqs(role):
    """Manage MCQs for a specific role."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            question = request.form.get('question')
            options = [
                request.form.get('option1'),
                request.form.get('option2'),
                request.form.get('option3'),
                request.form.get('option4')
            ]
            answer = request.form.get('answer')
            
            mcqs = load_mcqs(role)
            mcqs.append({
                'question': question,
                'options': options,
                'answer': answer
            })
            save_mcqs(role, mcqs)
            
            flash('MCQ added successfully!', 'success')
        
        elif action == 'delete':
            index = int(request.form.get('index'))
            mcqs = load_mcqs(role)
            if 0 <= index < len(mcqs):
                mcqs.pop(index)
                save_mcqs(role, mcqs)
                flash('MCQ deleted successfully!', 'success')
        
        return redirect(url_for('manage_mcqs', role=role))
    
    mcqs = load_mcqs(role)
    return render_template('recruiter/manage_mcqs.html', role=role, mcqs=mcqs)

@app.route('/recruiter/slots', methods=['GET', 'POST'])
@login_required
def manage_slots():
    """Manage interview time slots."""
    slots_file = 'predefined_times.json'
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            date = request.form.get('date')
            time = request.form.get('time')
            slot = f"{date} {time}"
            
            data = load_json_file(slots_file, {"available_times": []})
            if slot not in data['available_times']:
                data['available_times'].append(slot)
                save_json_file(slots_file, data)
                flash('Time slot added successfully!', 'success')
        
        elif action == 'delete':
            slot = request.form.get('slot')
            data = load_json_file(slots_file, {"available_times": []})
            if slot in data['available_times']:
                data['available_times'].remove(slot)
                save_json_file(slots_file, data)
                flash('Time slot deleted successfully!', 'success')
        
        return redirect(url_for('manage_slots'))
    
    slots_data = load_json_file(slots_file, {"available_times": []})
    return render_template('recruiter/manage_slots.html', slots=slots_data['available_times'])

@app.route('/recruiter/analytics')
@login_required
def analytics():
    """View analytics dashboard."""
    analytics_data = load_analytics()
    return render_template('recruiter/analytics.html', analytics=analytics_data)

# ==================== CANDIDATE ROUTES ====================

@app.route('/candidate/register', methods=['GET', 'POST'])
def candidate_register():
    """Candidate registration and role selection."""
    if request.method == 'POST':
        # Store candidate info in session
        session['candidate_name'] = request.form.get('name')
        session['candidate_email'] = request.form.get('email')
        session['candidate_role'] = request.form.get('role')
        
        flash('Registration successful! Please upload your resume.', 'success')
        return redirect(url_for('candidate_apply'))
    
    roles = load_roles()
    return render_template('candidate/register.html', roles=roles)

@app.route('/candidate/apply', methods=['GET', 'POST'])
def candidate_apply():
    """Candidate resume upload and analysis."""
    if 'candidate_email' not in session:
        flash('Please register first.', 'warning')
        return redirect(url_for('candidate_register'))
    
    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No resume file uploaded.', 'danger')
            return redirect(request.url)
        
        file = request.files['resume']
        
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Extract text from resume
            with open(filepath, 'rb') as f:
                resume_text = extract_text_from_pdf(f)
            
            # Analyze resume
            role = session['candidate_role']
            roles = load_roles()
            role_criteria = roles.get(role, "")
            
            is_selected, match_score, feedback = analyze_resume_text(resume_text, role_criteria, OPENAI_API_KEY)
            
            # Increment total applicants
            increment_total_applicants(role)
            
            if match_score >= RESUME_MATCH_THRESHOLD:
                session['resume_text'] = resume_text
                session['resume_match_score'] = match_score
                flash(f'Your resume matched {int(match_score * 100)}%! You can now take the MCQ test.', 'success')
                return redirect(url_for('candidate_test'))
            else:
                # Send rejection email (with error handling)
                try:
                    if EMAIL_SENDER and EMAIL_PASSWORD:
                        send_rejection_email(
                            EMAIL_SENDER, EMAIL_PASSWORD,
                            session['candidate_email'],
                            role, COMPANY_NAME
                        )
                        flash(f'Unfortunately, your resume matched only {int(match_score * 100)}%. We\'ve sent feedback to your email.', 'warning')
                    else:
                        flash(f'Unfortunately, your resume matched only {int(match_score * 100)}%.', 'warning')
                except Exception as e:
                    logger.error(f"Email sending failed: {str(e)}")
                    flash(f'Unfortunately, your resume matched only {int(match_score * 100)}%.', 'warning')
                
                return redirect(url_for('candidate_result', passed=False))
        else:
            flash('Only PDF files are allowed.', 'danger')
    
    role = session.get('candidate_role', 'Unknown')
    return render_template('candidate/apply.html', role=role)

@app.route('/candidate/test', methods=['GET', 'POST'])
def candidate_test():
    """Candidate MCQ test."""
    if 'candidate_email' not in session or 'resume_text' not in session:
        flash('Please complete the resume screening first.', 'warning')
        return redirect(url_for('candidate_register'))
    
    role = session['candidate_role']
    mcqs = load_mcqs(role)
    
    if not mcqs:
        flash('No test available for this role yet.', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        # Calculate score
        correct_answers = 0
        total_questions = len(mcqs)
        
        for idx, mcq in enumerate(mcqs):
            user_answer = request.form.get(f'question_{idx}')
            if user_answer == mcq['answer']:
                correct_answers += 1
        
        score = correct_answers / total_questions if total_questions > 0 else 0
        session['test_score'] = score
        
        # Update analytics
        passed = score >= PASSING_SCORE
        update_analytics(role, passed)
        
        if passed:
            # Send selection email (with error handling)
            try:
                if EMAIL_SENDER and EMAIL_PASSWORD:
                    send_selection_email(
                        EMAIL_SENDER, EMAIL_PASSWORD,
                        session['candidate_email'],
                        role, COMPANY_NAME
                    )
                    flash(f'Congratulations! You scored {int(score * 100)}% and passed the test! Check your email.', 'success')
                else:
                    flash(f'Congratulations! You scored {int(score * 100)}% and passed the test!', 'success')
            except Exception as e:
                logger.error(f"Email sending failed: {str(e)}")
                flash(f'Congratulations! You scored {int(score * 100)}% and passed the test! (Note: Email notification failed)', 'success')
            
            return redirect(url_for('candidate_schedule'))
        else:
            # Send rejection email (with error handling)
            try:
                if EMAIL_SENDER and EMAIL_PASSWORD:
                    send_rejection_email(
                        EMAIL_SENDER, EMAIL_PASSWORD,
                        session['candidate_email'],
                        role, COMPANY_NAME
                    )
            except Exception as e:
                logger.error(f"Email sending failed: {str(e)}")
            
            flash(f'You scored {int(score * 100)}%. Unfortunately, you need 75% to pass.', 'warning')
            return redirect(url_for('candidate_result', passed=False))
    
    return render_template('candidate/test.html', mcqs=mcqs, role=role)

@app.route('/candidate/schedule', methods=['GET', 'POST'])
def candidate_schedule():
    """Candidate interview scheduling."""
    if 'candidate_email' not in session or 'test_score' not in session:
        flash('Please complete the test first.', 'warning')
        return redirect(url_for('candidate_register'))
    
    if session['test_score'] < PASSING_SCORE:
        flash('You need to pass the test to schedule an interview.', 'warning')
        return redirect(url_for('index'))
    
    slots_data = load_json_file('predefined_times.json', {"available_times": []})
    available_slots = slots_data['available_times']
    
    if request.method == 'POST':
        selected_slot = request.form.get('slot')
        
        if selected_slot:
            # Schedule Zoom meeting
            try:
                meeting_url = schedule_zoom_meeting(
                    ZOOM_ACCOUNT_ID, ZOOM_CLIENT_ID, ZOOM_CLIENT_SECRET,
                    session['candidate_name'], session['candidate_email'],
                    selected_slot, session['candidate_role']
                )
            except Exception as e:
                logger.error(f"Zoom meeting creation failed: {str(e)}")
                meeting_url = "https://zoom.us"  # Fallback
            
            # Send interview confirmation email (with error handling)
            try:
                if EMAIL_SENDER and EMAIL_PASSWORD:
                    send_interview_email(
                        EMAIL_SENDER, EMAIL_PASSWORD,
                        session['candidate_email'], RECRUITER_EMAIL,
                        session['candidate_name'], session['candidate_role'],
                        selected_slot, meeting_url, COMPANY_NAME
                    )
                    flash('Interview scheduled successfully! Check your email for details.', 'success')
                else:
                    flash('Interview scheduled successfully!', 'success')
            except Exception as e:
                logger.error(f"Email sending failed: {str(e)}")
                flash('Interview scheduled successfully! (Note: Email notification failed)', 'warning')
            
            return redirect(url_for('candidate_result', passed=True))
        else:
            flash('Please select a time slot.', 'warning')
    
    return render_template('candidate/schedule.html', slots=available_slots)

@app.route('/candidate/result/<passed>')
def candidate_result(passed):
    """Show final result to candidate."""
    passed = passed.lower() == 'true'
    return render_template('candidate/result.html', 
                         passed=passed,
                         name=session.get('candidate_name'),
                         role=session.get('candidate_role'),
                         interview_slot=session.get('interview_slot'),
                         meeting_url=session.get('meeting_url'))

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
