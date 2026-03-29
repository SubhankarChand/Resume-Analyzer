import PyPDF2
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fpdf import FPDF

def create_pdf_report(score, matched, missing):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Resume Analysis Report", ln=True, align='C')
    
    pdf.set_font("Arial", size=12)
    pdf.ln(10)
    pdf.cell(200, 10, f"Total Match Score: {score}%", ln=True)
    
    pdf.ln(5)
    pdf.set_text_color(0, 128, 0) # Green
    pdf.cell(200, 10, f"Top Matched Skills: {', '.join(list(matched)[:5])}", ln=True)
    
    pdf.ln(5)
    pdf.set_text_color(255, 0, 0) # Red
    pdf.cell(200, 10, f"Missing Critical Skills: {', '.join(list(missing)[:5])}", ln=True)
    
    return pdf.output(dest='S').encode('latin-1') # Return as bytes

#nlp = spacy.load("en_core_web_sm")
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    nlp = spacy.blank("en") 

def extract_text(file):
    """Extract text safely from PDF."""
    reader = PyPDF2.PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text

    return text


def get_entities(text):
    """Extract entities using spaCy."""
    doc = nlp(text)

    entities = {
        "PERSON": [],
        "ORG": [],
        "GPE": []
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)

    return entities

def section_scores(resume_text):
    categories = {
        "Technical Skills": ["python", "machine learning", "nlp", "sql", "aws", "gcp", "spark", "datasets"],
        "Soft Skills": ["collaborate", "leadership", "communication", "problemsolving", "strong"],
        "Education/Cert": ["degree", "master", "phd", "certification", "ibm", "btech"]
    }
    
    resume_text = resume_text.lower()
    results = {}
    for cat, keywords in categories.items():
        found = [word for word in keywords if word in resume_text]
        results[cat] = round((len(found) / len(keywords)) * 100, 2)
    return results

def match_score(resume_text, jd_text):
    """Calculate similarity score."""
    vectors = TfidfVectorizer().fit_transform([resume_text, jd_text])
    score = cosine_similarity(vectors)[0][1]

    return round(score * 100, 2)