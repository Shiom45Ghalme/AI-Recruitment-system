"""
Resume Analyzer Utility Module
Handles resume text extraction and AI-powered analysis
"""
import PyPDF2
import logging
from typing import Tuple
import openai

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from PDF file."""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting PDF text: {str(e)}")
        return ""

def analyze_resume_text(resume_text: str, role_criteria: str, api_key: str) -> Tuple[bool, float, str]:
    """
    Analyze resume text against role criteria using OpenAI.
    
    Returns:
        Tuple of (is_selected, match_score, feedback)
    """
    try:
        openai.api_key = api_key
        
        prompt = f"""
You are an expert recruiter analyzing a candidate's resume against job requirements.

Role Requirements:
{role_criteria}

Candidate Resume:
{resume_text}

Please analyze the resume and provide:
1. A match percentage (0-100) based on how well the candidate's skills align with the requirements
2. Brief feedback on strengths and areas for improvement

Format your response as:
MATCH_SCORE: [number]
FEEDBACK: [your feedback]
"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert recruiter and HR analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        result = response.choices[0].message.content
        
        # Parse the response
        match_score = 0
        feedback = result
        
        for line in result.split('\n'):
            if 'MATCH_SCORE:' in line:
                try:
                    score_str = line.split(':')[1].strip()
                    match_score = float(score_str) / 100  # Convert to 0-1 range
                except:
                    pass
            elif 'FEEDBACK:' in line:
                feedback = line.split(':', 1)[1].strip()
        
        is_selected = match_score >= 0.5  # 50% threshold
        
        return is_selected, match_score, feedback
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}")
        # Fallback: Simple keyword matching
        return fallback_analyze_resume(resume_text, role_criteria)

def fallback_analyze_resume(resume_text: str, role_criteria: str) -> Tuple[bool, float, str]:
    """
    Fallback resume analysis using keyword matching.
    Used when OpenAI API is unavailable.
    """
    resume_lower = resume_text.lower()
    criteria_lower = role_criteria.lower()
    
    # Extract keywords from criteria (simple approach)
    keywords = []
    for line in criteria_lower.split('\n'):
        if any(x in line for x in ['python', 'java', 'javascript', 'react', 'node', 'aws', 'docker', 
                                     'kubernetes', 'machine learning', 'tensorflow', 'pytorch']):
            words = line.strip('- ').split(',')
            keywords.extend([w.strip() for w in words if len(w.strip()) > 2])
    
    if not keywords:
        keywords = criteria_lower.split()
    
    # Count matching keywords
    matches = sum(1 for keyword in keywords if keyword in resume_lower)
    match_score = min(matches / max(len(keywords), 1), 1.0)
    
    is_selected = match_score >= 0.5
    
    feedback = f"Resume matched {int(match_score * 100)}% of the required keywords. "
    if is_selected:
        feedback += "The candidate shows relevant experience."
    else:
        feedback += "The candidate may need to develop more relevant skills."
    
    return is_selected, match_score, feedback
