import re
import string
import spacy
from fpdf import FPDF
from datetime import date

# Load spaCy once at the top
try:
    nlp = spacy.load("en_core_web_sm")
except:
    import en_core_web_sm
    nlp = en_core_web_sm.load()

def clean_text(text):
    """Cleans text for NLP processing, preserving internal structure."""
    text = str(text).lower()
    text = re.sub(r'http\S+\s*', ' ', text)
    text = re.sub(r'RT|cc', ' ', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'@\S+', ' ', text)
    text = text.replace('/', ' ').replace('-', ' ')
    return text.strip()

def get_keywords(text):
    """
    Advanced Statistical Filtering using POS Tagging.
    Extracts Nouns/Proper Nouns, ignoring stop words and junk parts of speech.
    """
    doc = nlp(text)
    keywords = {
        token.text.lower() 
        for token in doc 
        if token.pos_ in ['NOUN', 'PROPN'] 
        and not token.is_stop 
        and len(token.text) > 2
    }
    return keywords

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
    """Generates a professional, Unicode-safe PDF Analysis Report."""
    pdf = FPDF()
    pdf.add_page()
    pdf.rect(5, 5, 200, 287) 

    # --- ENCODING SAFETY HELPER ---
    def clean_for_pdf(text_list):
        raw_text = ", ".join(list(text_list)[:25])
        # Removes characters that cannot be rendered in standard PDF fonts
        return raw_text.encode('latin-1', 'ignore').decode('latin-1')

    # Header
    pdf.set_font("helvetica", 'B', 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(100, 10, f"Candidate: {user_name.upper().encode('latin-1', 'ignore').decode('latin-1')}", ln=0)
    pdf.cell(90, 10, f"Date: {date.today()}", ln=1, align='R')

    # Title
    pdf.ln(2)
    pdf.set_font("helvetica", 'B', 22)
    pdf.set_text_color(0, 51, 102) 
    pdf.cell(200, 15, "RESUME ANALYSIS REPORT", ln=1, align='C')
    pdf.line(10, 48, 200, 48)

    # Consolidated Score Box
    pdf.ln(5)
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 55, 190, 20, 'F') 
    pdf.set_xy(12, 57)
    pdf.set_font("helvetica", 'B', 11)
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
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(200, 10, "1. Key Strengths (Matched Keywords)", ln=1)
    pdf.set_font("helvetica", size=10)
    pdf.multi_cell(0, 6, clean_for_pdf(matched))

    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(200, 10, "2. Missing Competencies & Keywords", ln=1)
    pdf.set_font("helvetica", size=10)
    pdf.multi_cell(0, 6, clean_for_pdf(missing))

    pdf.ln(5)
    pdf.set_font("helvetica", 'B', 12)
    pdf.cell(200, 10, "3. Final Verdict & Recommendation", ln=1)
    pdf.set_font("helvetica", size=10)
    if score < 50:
        verdict = "Verdict: REVISE RESUME. Align experience with missing keywords in Section 2."
    elif score < 75:
        verdict = "Verdict: POTENTIAL MATCH. Good alignment; strengthen soft skill descriptions."
    else:
        verdict = "Verdict: STRONG MATCH. Profile aligns highly with core requirements."
    pdf.multi_cell(0, 6, verdict)

    # Footer
    pdf.set_y(-12)
    pdf.set_font("helvetica", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 10, "AI Resume Analyzer Pro | Engineering Project 2026", align='C')

    return bytes(pdf.output())