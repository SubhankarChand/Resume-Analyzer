import streamlit as st
from processor import extract_text, get_entities, match_score
from utils import clean_text, get_keywords
from utils import clean_text, get_keywords, create_pdf_report

st.set_page_config(page_title="AI Resume Analyzer Pro", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .skill-tag {
        background-color: #e1e4e8;
        color: #0366d6;
        padding: 5px 10px;
        border-radius: 15px;
        margin: 5px;
        display: inline-block;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📄 AI Resume Analyzer (NLP)")

# --- SESSION STATE ---
if "jd_text" not in st.session_state: st.session_state.jd_text = ""
if "resume_file" not in st.session_state: st.session_state.resume_file = None

col1, col2 = st.columns(2)

with col1:
    st.subheader("Step 1: Job Description")
    jd_option = st.radio("Input Type:", ["Paste Text", "Upload PDF"], horizontal=True)
    if jd_option == "Paste Text":
        jd_input = st.text_area("Paste JD:", height=250, value=st.session_state.jd_text)
        st.session_state.jd_text = jd_input
    else:
        jd_file = st.file_uploader("Upload JD", type="pdf", key="jd_up")
        if jd_file: st.session_state.jd_text = extract_text(jd_file)

with col2:
    st.subheader("Step 2: Resume")
    uploaded_file = st.file_uploader("Upload Resume", type="pdf", key="res_up")
    if uploaded_file: st.session_state.resume_file = uploaded_file

if st.button("Analyze Now", type="primary", use_container_width=True):
    if st.session_state.jd_text and st.session_state.resume_file:
        with st.spinner("Analyzing depth of match..."):
            raw_resume = extract_text(st.session_state.resume_file)
            c_resume = clean_text(raw_resume)
            c_jd = clean_text(st.session_state.jd_text)
            
            score = match_score(c_resume, c_jd)
            
            # --- SKILL GAP DETECTION ---
            jd_keys = get_keywords(c_jd)
            res_keys = get_keywords(c_resume)
            missing = jd_keys - res_keys
            matched = jd_keys & res_keys

            # --- RESULTS UI ---
            st.divider()
            col_left, col_right = st.columns([1, 2])
            
            with col_left:
                st.metric("Match Score", f"{score}%")
                st.progress(score / 100)
                
            with col_right:
                if score >= 70:
                    st.success("✅ Strong Match! Your profile aligns with the core requirements.")
                else:
                    st.warning("⚠️ Improvement Needed: Look at the missing keywords below.")

            st.subheader("Skill Analysis")
            tab1, tab2 = st.tabs(["Matched Keywords", "Missing Keywords (Skill Gap)"])
            
            # Corrected Tab 1 (Matched Keywords)
            with tab1:
                if matched:
                    st.write("These keywords were found in both:")
                    # The closing bracket for .join() is now BEFORE the comma
                    st.write(" ".join([f'<span class="skill-tag">{m}</span>' for m in list(matched)[:20]]), unsafe_allow_html=True)
            
            # Corrected Tab 2 (Missing Keywords)
            with tab2:
                if missing:
                    st.write("Consider adding these to your resume:")
                    # The closing bracket for .join() is now BEFORE the comma
                    st.write(" ".join([f'<span class="skill-tag" style="color:red;">{m}</span>' for m in list(missing)[:20]]), unsafe_allow_html=True)
            # --- DOWNLOAD REPORT ---
            report_text = f"Resume Analysis Report\nScore: {score}%\n\nMatched: {list(matched)[:10]}\n\nMissing: {list(missing)[:10]}"
            st.download_button("Download Analysis Report", report_text, file_name="analysis_report.txt")
            
            pdf_data = create_pdf_report(score, matched, missing)
            st.download_button("Download Official PDF Report", pdf_data, file_name="Resume_Analysis.pdf", mime="application/pdf")

    else:
        st.error("Please provide both inputs.")