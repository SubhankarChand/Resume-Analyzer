import re
import string
from fpdf import FPDF

def clean_text(text):
    """Cleans text for NLP processing."""
    text = str(text).lower()
    text = re.sub(r'http\S+\s*', ' ', text)
    text = re.sub(r'RT|cc', ' ', text)
    text = re.sub(r'#\S+', '', text)
    text = re.sub(r'@\S+', ' ', text)
    text = text.translate(str.maketrans('', '', string.punctuation))
    text = re.sub(r'[^\x00-\x7f]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def get_keywords(text):
    """Extracts meaningful keywords, filtering out common 'noise' words."""
    # Words to ignore (Filtering noise)
    stop_words = {'into', 'type', 'required', 'and', 'the', 'for', 'from', 'with', 'this', 'that', 'our', 'your'}
    words = set(re.findall(r'\b\w{3,}\b', text.lower()))
    return words - stop_words

def create_pdf_report(score, matched, missing):
    """Generates a professional PDF report of the analysis."""
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "AI Resume Analysis Report", ln=True, align='C')
    
    # Score Section
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Total Match Score: {score}%", ln=True)
    
    # Matched Skills
    pdf.ln(5)
    pdf.set_text_color(0, 128, 0) # Green
    pdf.multi_cell(0, 10, f"Matched Keywords: {', '.join(list(matched)[:15])}")
    
    # Missing Skills
    pdf.ln(5)
    pdf.set_text_color(255, 0, 0) # Red
    pdf.multi_cell(0, 10, f"Missing Skills to Add: {', '.join(list(missing)[:15])}")
    
    # Return as bytes
    return pdf.output(dest='S').encode('latin-1')