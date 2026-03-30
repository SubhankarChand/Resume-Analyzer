import re
import string
from fpdf import FPDF
from datetime import date

def clean_text(text):
    """Cleans text for NLP processing, preserving slashes for AI/ML terms."""
    text = str(text).lower()
    text = re.sub(r'http\S+\s*', ' ', text)
    text = re.sub(r'RT|cc', ' ', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'@\S+', ' ', text)
    # Replace slashes and dashes with spaces to avoid 'alml' or 'b2bb2c'
    text = text.replace('/', ' ').replace('-', ' ')
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'[^\x00-\x7f]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_keywords(text):
    """Extracts meaningful words by filtering out extensive 'Corporate Fluff'."""
    universal_stop_words = {
        'candidate', 'join', 'details', 'pvt', 'limited', 'office', 'will', 
        'has', 'using', 'work', 'strong', 'nextgeneration', 'preferred', 
        'qualifications', 'requirements', 'apply', 'team', 'world', 'seeking', 
        'looking', 'plus', 'benefits', 'equal', 'opportunity', 'within', 'into',
        'needed', 'several', 'provide', 'working', 'deliver', 'kept', 'summary', 
        'send', 'leverage', 'you', 'towards', 'including', 'across', 'highly', 'based', 
        'role', 'skills', 'responsibilities','job', 'description', 'position', 'company', 
        'business', 'industry', 'opportunities', 'growth', 'development', 'culture', 'values', 
        'mission','full','tools','knowledge','ability','excellent','good','proven',
        'demonstrated','solid','extensive','experience','position','may', 'the', 'with',
        'from', 'for', 'upon', 'questions', 'prorated', 'solely', 'manner', 'ones', 'basic'
    }
    # Find words with at least 3 characters
    words = set(re.findall(r'\b\w{3,}\b', text.lower()))
    return words - universal_stop_words

def categorize_keywords(keywords):
    """Splits keywords into Technical and Soft Skill buckets."""
    tech_lexicon = {
        'python', 'java', 'c++', 'sql', 'javascript', 'react', 'node', 'aws', 'azure', 'gcp',
        'docker', 'kubernetes', 'ml', 'ai', 'nlp', 'tensorflow', 'pytorch', 'pandas', 'numpy',
        'tableau', 'powerbi', 'excel', 'git', 'linux', 'api', 'mongodb', 'ci/cd', 'terraform', 'scikitlearn'
    }
    soft_lexicon = {
        'leadership', 'communication', 'teamwork', 'management', 'collaboration', 'problem-solving',
        'negotiation', 'strategy', 'planning', 'mentoring', 'presentation', 'analytical', 
        'creativity', 'adaptability', 'agile', 'scrum', 'organization', 'time-management'
    }
    
    tech_m = [w for w in keywords if w in tech_lexicon]
    soft_m = [w for w in keywords if w in soft_lexicon]
    other_m = [w for w in keywords if w not in tech_lexicon and w not in soft_lexicon]
    return tech_m, soft_m, other_m

def create_pdf_report(score, matched, missing, t_score, s_score, user_name):
    """Generates a professional, branded PDF Analysis Report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.rect(5, 5, 200, 287) # Border

    # Header: Candidate & Date
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(100, 10, f"Candidate: {user_name.upper()}", ln=False)
    pdf.cell(90, 10, f"Date: {date.today()}", ln=True, align='R')

    # Title
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(0, 51, 102) 
    pdf.cell(200, 20, "RESUME ANALYSIS REPORT", ln=True, align='C')
    
    pdf.set_draw_color(0, 51, 102)
    pdf.line(10, 52, 200, 52)
    pdf.ln(5)

    # Category Scores
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 60, 190, 25, 'F') # Light gray background box
    pdf.set_xy(12, 62)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(60, 10, f"Overall ATS Match: {score}%", ln=0)
    pdf.cell(60, 10, f"Technical Match: {t_score}%", ln=0)
    pdf.cell(60, 10, f"Soft Skill Match: {s_score}%", ln=1)
    
    # Overall ATS Score
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(45, 10, "Overall ATS Score: ", ln=False)
    if score >= 70: pdf.set_text_color(0, 128, 0) # Green
    else: pdf.set_text_color(255, 0, 0) # Red
    pdf.cell(50, 10, f"{score}%", ln=True)
    pdf.set_text_color(0, 0, 0) # Reset

    # 1. Matched Keywords
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "1. Key Strengths (Matched Keywords)", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, ", ".join(list(matched)[:25]))

    # 2. Skill Gap
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "2. Missing Competencies & Keywords", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 7, ", ".join(list(missing)[:25]))

    # 3. Recommendations
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, "3. Final Verdict & Recommendation", ln=True)
    pdf.set_font("Arial", size=10)
    if score < 50:
        verdict = "Verdict: REVISE RESUME. Significant skill gaps identified. Align experience with JD keywords."
    elif score < 75:
        verdict = "Verdict: POTENTIAL MATCH. Good alignment, but consider highlighting soft skills more explicitly."
    else:
        verdict = "Verdict: STRONG MATCH. Profile highly aligns with requirements. Ready for technical interview."
    pdf.multi_cell(0, 7, verdict)

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "AI Resume Analyzer Pro | Engineering Project 2026", align='C')

    return bytes(pdf.output())
