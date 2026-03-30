import streamlit as st
from processor import extract_text, get_entities, match_score
from utils import clean_text, get_keywords, create_pdf_report, categorize_keywords

st.set_page_config(page_title="AI Resume Analyzer Pro", layout="wide")

# Custom UI Styling
st.markdown("""
    <style>
    .metric-card { background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 5px solid #0366d6; }
    .stProgress > div > div > div > div { background-color: #0366d6; }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 AI Resume Analyzer (NLP)")

if "jd_text" not in st.session_state: st.session_state.jd_text = ""

col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 1: Job Description")
    jd_option = st.radio("Input Type:", ["Paste Text", "Upload PDF"], horizontal=True)
    if jd_option == "Paste Text":
        st.session_state.jd_text = st.text_area("Paste JD:", height=250, value=st.session_state.jd_text)
    else:
        jd_file = st.file_uploader("Upload JD", type="pdf", key="jd_up")
        if jd_file: st.session_state.jd_text = extract_text(jd_file)

with col2:
    st.subheader("Step 2: Resume")
    uploaded_file = st.file_uploader("Upload Resume", type="pdf", key="res_up")

if st.button("Analyze Now", type="primary", use_container_width=True):
    if st.session_state.jd_text and uploaded_file:
        with st.spinner("Running NLP Pipeline..."):
            # A. Extract & Find Name
            raw_resume = extract_text(uploaded_file)
            entities = get_entities(raw_resume)
            
            # Smart Name Extraction: Use NER first, fallback to first line of PDF
            user_name = next((e[0] for e in entities if e[1] == 'PERSON'), None)
            if not user_name:
                lines = [line.strip() for line in raw_resume.split('\n') if line.strip()]
                user_name = lines[0] if lines else "Candidate"
            
            # B. Processing & Scoring
            c_resume = clean_text(raw_resume)
            c_jd = clean_text(st.session_state.jd_text)
            score = match_score(c_resume, c_jd)
            
            # C. Keyword & Category Analysis
            jd_keys = get_keywords(c_jd)
            res_keys = get_keywords(c_resume)
            missing = jd_keys - res_keys
            matched = jd_keys & res_keys

            tech_m, soft_m, other_m = categorize_keywords(matched)
            tech_miss, soft_miss, other_miss = categorize_keywords(missing)

            def calc_cat(m, miss):
                total = len(m) + len(miss)
                return round((len(m)/total)*100, 2) if total > 0 else 0

            t_score = calc_cat(tech_m, tech_miss)
            s_score = calc_cat(soft_m, soft_miss)

            # D. Results UI
            st.divider()
            st.subheader(f"Analysis for: {user_name}")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Overall Match", f"{score}%")
            c2.metric("Tech Match", f"{t_score}%")
            c3.metric("Soft Skills", f"{s_score}%")

            # Visual Progress Bars
            st.write(f"**Technical Match Progress**")
            st.progress(t_score / 100)

            tab1, tab2, tab3 = st.tabs(["✅ Matched Skills", "❌ Skill Gap", "📥 Download Report"])
            
            with tab1:
                st.success(f"Matched {len(matched)} key attributes!")
                st.write("**Technical Matches:** " + (", ".join(tech_m) if tech_m else "None identified"))
                st.write("**Soft Skill Matches:** " + (", ".join(soft_m) if soft_m else "None identified"))
            
            with tab2:
                st.error(f"Missing Technical: {', '.join(tech_miss) if tech_miss else 'None'}")
                st.warning(f"Missing Soft Skills: {', '.join(soft_miss) if soft_miss else 'None'}")
                st.info("💡 Tip: Try incorporating these keywords into your experience descriptions naturally.")

            with tab3:
                # Generate PDF
                try:
                    pdf_data = create_pdf_report(score, matched, missing, t_score, s_score, user_name)
                    st.download_button(
                        label="Download Official PDF Report", 
                        data=pdf_data, 
                        file_name=f"Report_{user_name.replace(' ', '_')}.pdf", 
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Error generating PDF: {e}")
                    
    else:
        st.error("Missing Input: Please provide both a Job Description and a Resume PDF.")