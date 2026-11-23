"""
Google Calendar API Integration with OAuth 2.0
Handles interview scheduling, token refresh, and Google Meet link generation.
"""

import os
import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# Google API Scopes required for Calendar Events
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_PATH = os.path.join(BASE_DIR, 'token.json')
CREDENTIALS_PATH = os.path.join(BASE_DIR, 'credentials.json')


def is_google_calendar_configured() -> bool:
    """Check if token.json or credentials.json exists."""
    return os.path.exists(TOKEN_PATH) or os.path.exists(CREDENTIALS_PATH)


def get_calendar_service():
    """
    Authenticate with OAuth 2.0 and return the Google Calendar service.
    Handles token refresh automatically when expired.
    """
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as e:
        logger.error(f"Google API libraries not installed: {e}")
        return None

    creds = None

    # Load existing token if present
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            logger.warning(f"Error loading token.json: {e}")
            creds = None

    # If expired, refresh token automatically using OAuth 2.0 refresh_token
    if creds and creds.expired and creds.refresh_token:
        try:
            logger.info("Google OAuth 2.0 token expired. Refreshing token...")
            creds.refresh(Request())
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
            logger.info("Google OAuth 2.0 token refreshed and saved successfully.")
        except Exception as e:
            logger.error(f"Failed to refresh OAuth token: {e}")
            creds = None

    # If no valid credentials, attempt local server flow if credentials.json is present
    if not creds or not creds.valid:
        if os.path.exists(CREDENTIALS_PATH):
            try:
                logger.info("Initiating OAuth 2.0 authorization flow...")
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(TOKEN_PATH, 'w') as token_file:
                    token_file.write(creds.to_json())
                logger.info("OAuth 2.0 token created and saved successfully.")
            except Exception as e:
                logger.error(f"OAuth 2.0 flow error: {e}")
                return None
        else:
            logger.warning("Neither token.json nor credentials.json found for Google Calendar API.")
            return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        logger.error(f"Failed to build Google Calendar service: {e}")
        return None


def schedule_google_calendar_interview(
    candidate_name: str,
    candidate_email: str,
    recruiter_email: str,
    role: str,
    slot_str: str,
    company_name: str = "Company",
    duration_minutes: int = 45,
    timezone: str = "UTC"
) -> Dict[str, Any]:
    """
    Create a Google Calendar event with a real Google Meet link.
    
    Returns:
        dict: {
            'success': bool,
            'meeting_url': str,
            'event_id': str or None,
            'event_link': str or None,
            'error': str or None
        }
    """
    service = get_calendar_service()
    if not service:
        logger.warning("Google Calendar service not available. Falling back to placeholder.")
        return {
            'success': False,
            'meeting_url': None,
            'event_id': None,
            'event_link': None,
            'error': "Google Calendar service not authorized. Place credentials.json or token.json in project."
        }

    # Parse slot datetime
    start_time = None
    for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M'):
        try:
            start_time = datetime.strptime(slot_str.strip(), fmt)
            break
        except ValueError:
            continue

    if not start_time:
        start_time = datetime.now() + timedelta(days=1)

    end_time = start_time + timedelta(minutes=duration_minutes)

    event_body = {
        'summary': f"Interview: {candidate_name} - {role} ({company_name})",
        'description': (
            f"Automated Recruitment Interview\n\n"
            f"Candidate: {candidate_name} ({candidate_email})\n"
            f"Position: {role}\n"
            f"Company: {company_name}\n"
            f"Duration: {duration_minutes} minutes\n"
        ),
        'start': {
            'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': timezone,
        },
        'attendees': [
            {'email': candidate_email, 'displayName': candidate_name},
        ],
        'conferenceData': {
            'createRequest': {
                'requestId': f"interview-{uuid.uuid4().hex[:12]}",
                'conferenceSolutionKey': {'type': 'hangoutsMeet'}
            }
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
                {'method': 'email', 'minutes': 24 * 60},
                {'method': 'popup', 'minutes': 15},
            ],
        },
    }

    if recruiter_email:
        event_body['attendees'].append({'email': recruiter_email, 'displayName': f"{company_name} Recruiter"})

    try:
        from googleapiclient.errors import HttpError
        logger.info(f"Creating Google Calendar event for {candidate_name} at {start_time}...")
        
        created_event = service.events().insert(
            calendarId='primary',
            body=event_body,
            conferenceDataVersion=1,
            sendUpdates='all'
        ).execute()

        # Extract Google Meet link
        meet_url = created_event.get('hangoutLink')
        if not meet_url and 'conferenceData' in created_event:
            for entry_point in created_event['conferenceData'].get('entryPoints', []):
                if entry_point.get('entryPointType') == 'video':
                    meet_url = entry_point.get('uri')
                    break

        event_id = created_event.get('id')
        event_link = created_event.get('htmlLink')
        logger.info(f"Google Calendar event created successfully! Meet URL: {meet_url}")

        return {
            'success': True,
            'meeting_url': meet_url,
            'event_id': event_id,
            'event_link': event_link,
            'error': None
        }

    except Exception as e:
        logger.error(f"API error creating Google Calendar event: {e}")
        return {
            'success': False,
            'meeting_url': None,
            'event_id': None,
            'event_link': None,
            'error': str(e)
        }
