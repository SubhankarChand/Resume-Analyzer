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
        'demonstrated','solid','extensive','experience','may', 'the', 'with',
        'from', 'for', 'upon', 'questions', 'prorated', 'solely', 'manner', 'ones', 'basic'
    }
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
    return tech_m, soft_m

def create_pdf_report(score, matched, missing, t_score, s_score, user_name):
    """Generates a professional, single-page PDF Analysis Report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.rect(5, 5, 200, 287) 

    # Header
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(100, 10, f"Candidate: {user_name.upper()}", ln=0)
    pdf.cell(90, 10, f"Date: {date.today()}", ln=1, align='R')

    # Title
    pdf.ln(2)
    pdf.set_font("Arial", 'B', 22)
    pdf.set_text_color(0, 51, 102) 
    pdf.cell(200, 15, "RESUME ANALYSIS REPORT", ln=1, align='C')
    pdf.line(10, 48, 200, 48)

    # Consolidated Score Box
    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 55, 190, 20, 'F') 
    pdf.set_xy(12, 57)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(60, 8, f"Technical Match: {t_score}%", ln=0)
    pdf.cell(60, 8, f"Soft Skill Match: {s_score}%", ln=0)
    pdf.cell(35, 8, "Overall Match: ", ln=0)
    if score >= 70: pdf.set_text_color(0, 128, 0)
    else: pdf.set_text_color(220, 0, 0)
    pdf.cell(20, 8, f"{score}%", ln=1)
    pdf.set_text_color(0, 0, 0)

    # Sections
    pdf.set_xy(10, 80)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "1. Key Strengths (Matched Keywords)", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 6, ", ".join(list(matched)[:25]))

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "2. Missing Competencies & Keywords", ln=1)
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(0, 6, ", ".join(list(missing)[:25]))

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "3. Final Verdict & Recommendation", ln=1)
    pdf.set_font("Arial", size=10)
    if score < 50:
        verdict = "Verdict: REVISE RESUME. Align experience with missing keywords in Section 2."
    elif score < 75:
        verdict = "Verdict: POTENTIAL MATCH. Good alignment; strengthen soft skill descriptions."
    else:
        verdict = "Verdict: STRONG MATCH. Profile aligns highly with core requirements."
    pdf.multi_cell(0, 6, verdict)

    # Footer
    pdf.set_y(-15)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "AI Resume Analyzer Pro | Engineering Project 2026", align='C')

    return bytes(pdf.output())