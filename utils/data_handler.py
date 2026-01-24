"""
Data Handler Utility Module
Handles all JSON file operations for roles, MCQs, and analytics
"""
import json
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# File paths
FILE_PATH = "roles.json"
MCQS_FILE_PATH = "mcqs.json"
ANALYTICS_FILE_PATH = "analytics.json"
PREDEFINED_TIMES_PATH = "predefined_times.json"

def load_json_file(filepath: str, default_value: Dict = None) -> Dict:
    """Generic function to load JSON files with error handling."""
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            return data if data else (default_value or {})
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.warning(f"File issue with {filepath}: {e}")
        return default_value or {}

def save_json_file(filepath: str, data: Dict) -> bool:
    """Generic function to save JSON files with error handling."""
    try:
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)
        return True
    except Exception as e:
        logger.error(f"Error saving to {filepath}: {e}")
        return False

def load_roles() -> Dict:
    """Load job roles from JSON file."""
    return load_json_file(FILE_PATH, {})

def save_roles(roles: Dict) -> bool:
    """Save job roles to JSON file."""
    return save_json_file(FILE_PATH, roles)

def load_mcqs(role_choice: str = "") -> List[Dict]:
    """Load MCQs for a specific role or all roles."""
    mcqs_data = load_json_file(MCQS_FILE_PATH, {})
    return mcqs_data.get(role_choice, []) if role_choice else mcqs_data

def save_mcqs(role_choice: str, role_mcqs: List[Dict]) -> bool:
    """Save MCQs for a specific role."""
    mcqs_data = load_json_file(MCQS_FILE_PATH, {})
    mcqs_data[role_choice] = role_mcqs
    return save_json_file(MCQS_FILE_PATH, mcqs_data)

def load_analytics() -> Dict:
    """Load analytics data."""
    return load_json_file(ANALYTICS_FILE_PATH, {"roles": {}, "interviews": []})

def update_analytics(role: str, test_result: bool):
    """Update analytics.json with test results."""
    try:
        data = load_analytics()
        if role not in data["roles"]:
            data["roles"][role] = {
                "total_applicants": 0,
                "selected_for_test": 0,
                "passed": 0,
                "failed": 0
            }
        data["roles"][role]["selected_for_test"] += 1
        data["roles"][role]["passed" if test_result else "failed"] += 1
        save_json_file(ANALYTICS_FILE_PATH, data)
    except Exception as e:
        logger.error(f"Error updating analytics: {e}")

def increment_total_applicants(role: str):
    """Increment total applicants count for a role."""
    try:
        data = load_analytics()
        if role not in data["roles"]:
            data["roles"][role] = {
                "total_applicants": 0,
                "selected_for_test": 0,
                "passed": 0,
                "failed": 0
            }
        data["roles"][role]["total_applicants"] += 1
        save_json_file(ANALYTICS_FILE_PATH, data)
    except Exception as e:
        logger.error(f"Error incrementing applicants: {e}")
