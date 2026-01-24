"""
Zoom Integration Utility Module
Handles Zoom meeting creation via API
"""
import requests
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def schedule_zoom_meeting(account_id: str, client_id: str, client_secret: str,
                         candidate_name: str, candidate_email: str, 
                         meeting_time: str, role: str) -> str:
    """
    Schedule a Zoom meeting for the interview.
    
    Returns:
        Meeting URL (join link)
    """
    try:
        # Get OAuth token
        access_token = get_zoom_access_token(account_id, client_id, client_secret)
        
        if not access_token:
            logger.error("Failed to get Zoom access token")
            return "https://zoom.us"  # Fallback
        
        # Parse meeting time
        try:
            meeting_datetime = datetime.strptime(meeting_time, "%Y-%m-%d %H:%M:%S")
        except:
            meeting_datetime = datetime.now()
        
        # Create meeting
        meeting_url = "https://api.zoom.us/v2/users/me/meetings"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        meeting_data = {
            "topic": f"Interview - {role}",
            "type": 2,  # Scheduled meeting
            "start_time": meeting_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "duration": 60,  # 60 minutes
            "timezone": "UTC",
            "agenda": f"Interview with {candidate_name} for {role} position",
            "settings": {
                "host_video": True,
                "participant_video": True,
                "join_before_host": False,
                "mute_upon_entry": True,
                "waiting_room": True,
                "email_notification": True,
                "contact_email": candidate_email,
                "contact_name": candidate_name
            }
        }
        
        response = requests.post(meeting_url, headers=headers, json=meeting_data)
        
        if response.status_code == 201:
            meeting_info = response.json()
            join_url = meeting_info.get("join_url", "https://zoom.us")
            logger.info(f"Zoom meeting created successfully: {join_url}")
            return join_url
        else:
            logger.error(f"Error creating Zoom meeting: {response.status_code} - {response.text}")
            return "https://zoom.us"  # Fallback
            
    except Exception as e:
        logger.error(f"Error scheduling Zoom meeting: {str(e)}")
        return "https://zoom.us"  # Fallback

def get_zoom_access_token(account_id: str, client_id: str, client_secret: str) -> str:
    """Get Zoom OAuth access token."""
    try:
        token_url = "https://zoom.us/oauth/token"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "account_credentials",
            "account_id": account_id
        }
        
        response = requests.post(
            token_url,
            headers=headers,
            data=data,
            auth=(client_id, client_secret)
        )
        
        if response.status_code == 200:
            token_info = response.json()
            access_token = token_info.get("access_token", "")
            logger.info("Zoom access token obtained successfully")
            return access_token
        else:
            logger.error(f"Error fetching Zoom token: {response.status_code} - {response.text}")
            return ""
            
    except Exception as e:
        logger.error(f"Error getting Zoom access token: {str(e)}")
        return ""
