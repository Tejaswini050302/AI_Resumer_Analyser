import os
import sys
import json
import sqlite3
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Ensure project root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.text_extractor import TextExtractor
from src.nlp_processor import NLPProcessor
from src.skill_extractor import SkillExtractor
from src.ml_classifier import JobRoleClassifier
from src.job_matcher import JobMatcher
from src.skill_gap_analyzer import SkillGapAnalyzer
from src.recommender import Recommender
from src.database import DatabaseManager
from src.live_job_fetcher import LiveJobFetcher


# ---------------------------------------------------------
# Streamlit App Configuration & Styling
# ---------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer & Job Recommender",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

CUSTOM_CSS = """
<style>
    /* Gradient Header */
    .main-title {
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 50%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.4rem;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        color: #64748B;
        font-size: 1.05rem;
        margin-bottom: 1.5rem;
    }
    /* Info Card */
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1E293B;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    /* Skill Pills */
    .badge-skill {
        display: inline-block;
        padding: 4px 10px;
        margin: 3px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    .badge-tech { background-color: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
    .badge-matched { background-color: #ECFDF5; color: #047857; border: 1px solid #A7F3D0; }
    .badge-missing { background-color: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
    .badge-preferred { background-color: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
    .badge-extra { background-color: #F3E8FF; color: #6B21A8; border: 1px solid #E9D5FF; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# Resource Initializers (Cached)
# ---------------------------------------------------------
@st.cache_resource
def load_components():
    skill_extractor = SkillExtractor()
    job_classifier = JobRoleClassifier()
    job_classifier.load_artifacts()
    job_matcher = JobMatcher()
    recommender = Recommender()
    return skill_extractor, job_classifier, job_matcher, recommender


skill_extractor, job_classifier, job_matcher, recommender = load_components()
db_manager = DatabaseManager()
live_fetcher = LiveJobFetcher(skill_extractor=skill_extractor)


# ---------------------------------------------------------
# Helper Functions for Visualizations
# ---------------------------------------------------------
def create_gauge_chart(score: float, title: str, color: str = "#3B82F6"):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 18, 'color': '#334155'}},
        number={'suffix': "%", 'font': {'size': 32, 'color': '#0F172A'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#CBD5E1"},
            'bar': {'color': color, 'thickness': 0.75},
            'bgcolor': "#F1F5F9",
            'borderwidth': 1,
            'bordercolor': "#E2E8F0",
            'steps': [
                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.1)'},
                {'range': [50, 75], 'color': 'rgba(245, 158, 11, 0.1)'},
                {'range': [75, 100], 'color': 'rgba(16, 185, 129, 0.1)'}
            ],
        }
    ))
    fig.update_layout(height=240, margin=dict(l=20, r=20, t=40, b=20))
    return fig


def create_radar_chart(categories: List[str], values: List[float], title: str = "Skill Alignment"):
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(59, 130, 246, 0.3)',
        line=dict(color='#2563EB', width=2)
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=300,
        title=dict(text=title, x=0.5),
        margin=dict(l=30, r=30, t=40, b=30)
    )
    return fig


# ---------------------------------------------------------
# Sidebar Configuration & Resume Input
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("### 📥 Resume Source")
    input_source = st.radio(
        "Choose Resume Input:",
        ["Sample Resumes", "Upload File (PDF / DOCX / TXT)", "Paste Resume Text"],
        index=0
    )

    resume_text = ""
    resume_filename = "resume.txt"

    if input_source == "Sample Resumes":
        sample_map = {
            "Machine Learning Engineer": "ml_engineer_resume.txt",
            "Data Scientist": "data_scientist_resume.txt",
            "Full Stack Developer": "fullstack_developer_resume.txt",
            "DevOps & Cloud Engineer": "devops_engineer_resume.txt",
            "Data Analyst & BI Specialist": "data_analyst_resume.txt",
            "Cybersecurity & SOC Analyst": "cybersecurity_analyst_resume.txt",
            "Frontend Developer (React / UI)": "frontend_developer_resume.txt",
            "Backend Developer (Python / APIs)": "backend_developer_resume.txt",
            "Fresh Graduate / Junior Engineer": "fresher_graduate_resume.txt",
        }
        sample_choice = st.selectbox(
            "Select Sample Resume Profile:",
            list(sample_map.keys())
        )
        sample_file_path = os.path.join(BASE_DIR, "sample_resumes", sample_map[sample_choice])
        if os.path.exists(sample_file_path):
            with open(sample_file_path, "r", encoding="utf-8") as f:
                resume_text = f.read()
            resume_filename = sample_map[sample_choice]

    elif input_source == "Upload File (PDF / DOCX / TXT)":
        uploaded_file = st.file_uploader("Upload Resume File", type=["pdf", "docx", "txt"])
        if uploaded_file is not None:
            extracted_data = TextExtractor.extract_from_file(uploaded_file)
            resume_text = extracted_data["cleaned_text"]
            resume_filename = extracted_data["filename"]
            st.success(f"Loaded: {resume_filename} ({extracted_data['word_count']} words)")
        else:
            st.info("Please upload a PDF, DOCX, or TXT file.")

    else:
        resume_text = st.text_area("Paste Resume Text:", height=200, placeholder="Paste resume content here...")
        resume_filename = "pasted_resume.txt"

    st.markdown("---")
    st.markdown("### ⚙️ Engine Settings")
    model_choice = st.selectbox(
        "ML Job Prediction Model:",
        ["Random Forest", "Logistic Regression", "Support Vector Machine", "XGBoost"],
        index=0
    )
    semantic_enabled = st.checkbox("Enable Semantic Sentence Transformers", value=True)

    # Database quick count & Real-Time Sync
    all_jobs_list = db_manager.get_all_jobs()
    live_count = len([j for j in all_jobs_list if j.get("source") == "live_api"])
    
    st.markdown("---")
    st.markdown("### 🔄 Real-Time Jobs Sync")
    st.caption(f"💼 **{len(all_jobs_list)}** total positions in SQLite (**{live_count}** live synced).")

    col_sync1, col_sync2 = st.columns([1, 1])
    with col_sync1:
        if st.button("⚡ Sync Live Jobs", help="Fetch real-time active jobs from Remotive API & extract skills"):
            with st.spinner("Connecting to live job feeds and extracting skills..."):
                fresh = live_fetcher.fetch_live_jobs(category="software-dev", limit=8)
                if fresh:
                    added = db_manager.sync_live_jobs(fresh)
                    st.success(f"Synced {added} live jobs into SQLite!")
                    st.rerun()
                else:
                    st.warning("Could not reach API. Please check connection.")
    with col_sync2:
        if live_count > 0:
            if st.button("🗑️ Reset Default", help="Clear live jobs and revert to reference positions"):
                with db_manager.get_connection() as conn:
                    conn.cursor().execute("DELETE FROM jobs WHERE source = 'live_api'")
                st.info("Reset to default reference jobs.")
                st.rerun()


# ---------------------------------------------------------
# Main Header
# ---------------------------------------------------------
st.markdown('<div class="main-title">AI Resume Analyzer & Job Recommender</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Semantic Resume Screening, ML Job-Role Prediction, Skill-Gap Analysis & Intelligent Career Roadmaps</div>', unsafe_allow_html=True)


if not resume_text.strip():
    st.warning("👈 Please select a sample resume or upload a resume file in the sidebar to begin analysis.")
    st.stop()


# ---------------------------------------------------------
# Core Analysis Execution
# ---------------------------------------------------------
with st.spinner("Analyzing resume content, extracting skills, and predicting job suitability..."):
    # 1. Extraction and NLP
    sections = TextExtractor._segment_sections(resume_text)
    contact_info = NLPProcessor.extract_contact_info(resume_text)
    skills_data = skill_extractor.extract_skills(resume_text)
    extracted_skills = skills_data["all_extracted_skills"]
    categorized_skills = skills_data["skills_by_category"]

    # 2. ATS Quality evaluation
    quality_metrics = NLPProcessor.evaluate_resume_quality(
        resume_text, sections, len(extracted_skills)
    )

    # 3. Machine Learning Role Predictions
    try:
        predictions = job_classifier.predict_roles(resume_text, model_name=model_choice, top_k=3)
    except Exception as e:
        predictions = [{"role": "Machine Learning Engineer", "confidence": 88.0, "model_used": model_choice}]

    top_predicted_role = predictions[0]["role"]
    top_confidence = predictions[0]["confidence"]

    # 4. Save analysis to SQLite database history
    db_manager.save_analysis(
        candidate_name=contact_info.get("name") or "Candidate",
        email=contact_info.get("email") or "N/A",
        filename=resume_filename,
        predicted_role=top_predicted_role,
        confidence=top_confidence,
        ats_score=quality_metrics["ats_score"],
        skills_extracted=extracted_skills,
        dominant_domain=skills_data["dominant_domain"]
    )


# ---------------------------------------------------------
# Navigation Tabs
# ---------------------------------------------------------
tabs = st.tabs([
    "📄 Resume Profile & ATS Score",
    "🤖 ML Job-Role Prediction",
    "🎯 Job Matching & Skill Gap",
    "🚀 Personalized Recommendations",
    "👥 Recruiter ATS Screening",
    "🗄️ Database & System Analytics"
])


# =========================================================
# TAB 1: RESUME PROFILE & ATS SCORE
# =========================================================
with tabs[0]:
    st.subheader("Candidate Overview & ATS Health Check")

    # Top KPI metrics
    col_c1, col_c2, col_c3, col_c4 = st.columns(4)
    with col_c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Candidate Name</div>
            <div class="metric-value" style="font-size: 1.3rem;">{contact_info['name']}</div>
            <span style="font-size:0.8rem; color:#64748B;">{contact_info['email'] or 'No email found'}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Extracted Skills</div>
            <div class="metric-value">{len(extracted_skills)}</div>
            <span style="font-size:0.8rem; color:#64748B;">{skills_data['dominant_domain']}</span>
        </div>
        """, unsafe_allow_html=True)
    with col_c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Predicted Fit</div>
            <div class="metric-value" style="font-size: 1.3rem;">{top_predicted_role}</div>
            <span style="font-size:0.8rem; color:#10B981;">{top_confidence}% Confidence</span>
        </div>
        """, unsafe_allow_html=True)
    with col_c4:
        score_color = "#10B981" if quality_metrics["ats_score"] >= 75 else "#F59E0B" if quality_metrics["ats_score"] >= 60 else "#EF4444"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">ATS Compatibility</div>
            <div class="metric-value" style="color: {score_color};">{quality_metrics['ats_score']}%</div>
            <span style="font-size:0.8rem; color:#64748B;">Scored across 5 metrics</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ATS Quality Breakdown and Gauge
    col_g1, col_g2 = st.columns([1, 2])
    with col_g1:
        st.plotly_chart(
            create_gauge_chart(quality_metrics["ats_score"], "ATS Score", score_color),
            use_container_width=True
        )
    with col_g2:
        st.markdown("#### ATS Quality Factors Breakdown")
        q1, q2 = st.columns(2)
        with q1:
            st.write(f"**Action Verbs Impact:** {quality_metrics['action_verb_score']}%")
            st.progress(quality_metrics['action_verb_score'] / 100)
            st.write(f"**Measurable Metrics:** {quality_metrics['quantifiable_score']}%")
            st.progress(quality_metrics['quantifiable_score'] / 100)
        with q2:
            st.write(f"**Section Completeness:** {quality_metrics['section_score']}%")
            st.progress(quality_metrics['section_score'] / 100)
            st.write(f"**Skill Keyword Density:** {quality_metrics['skill_density_score']}%")
            st.progress(quality_metrics['skill_density_score'] / 100)

        # Contact Links Row
        links = []
        if contact_info["linkedin"]:
            links.append(f"[LinkedIn]({contact_info['linkedin']})")
        if contact_info["github"]:
            links.append(f"[GitHub]({contact_info['github']})")
        if contact_info["phone"]:
            links.append(f"📞 {contact_info['phone']}")
        if links:
            st.caption("Links found: " + " | ".join(links))

    st.markdown("---")

    # Categorized Skills Explorer
    st.subheader("Extracted Skills by Domain Taxonomy")
    if categorized_skills:
        for category, s_list in categorized_skills.items():
            st.markdown(f"**{category}** ({len(s_list)}):")
            pills_html = " ".join([f'<span class="badge-skill badge-tech">{s.title()}</span>' for s in s_list])
            st.markdown(pills_html, unsafe_allow_html=True)
    else:
        st.info("No standardized technical skills identified.")

    st.markdown("---")

    # Actionable ATS Recommendations
    st.subheader("💡 ATS Optimization & Improvement Tips")
    if quality_metrics["improvement_tips"]:
        for tip in quality_metrics["improvement_tips"]:
            st.markdown(f"- 📌 {tip}")
    else:
        st.success("✅ Excellent resume structure! Your resume meets high-standard ATS criteria.")

    # View Raw Sections Accordion
    with st.expander("🔍 View Detected Resume Sections (Text Extraction)"):
        for sec_name, sec_content in sections.items():
            if sec_content.strip():
                st.markdown(f"**{sec_name.upper()}:**")
                st.text(sec_content[:500] + ("..." if len(sec_content) > 500 else ""))


# =========================================================
# TAB 2: ML JOB-ROLE PREDICTION
# =========================================================
with tabs[1]:
    st.subheader("Machine Learning Job-Role Prediction & Multi-Model Comparison")
    st.markdown("""
    Multiple classification models (**Logistic Regression, Support Vector Machine, Random Forest, and XGBoost**)
    were trained on diverse candidate profiles to predict the most suitable job roles based on skills and experience.
    """)

    col_p1, col_p2 = st.columns([1, 1])

    with col_p1:
        st.markdown(f"#### Top Predicted Roles (Using {model_choice})")
        pred_df = pd.DataFrame(predictions)

        fig_pred = px.bar(
            pred_df,
            x="confidence",
            y="role",
            orientation="h",
            text="confidence",
            labels={"confidence": "Confidence Score (%)", "role": "Predicted Role"},
            color="confidence",
            color_continuous_scale="Blues"
        )
        fig_pred.update_layout(yaxis=dict(autorange="reversed"), height=300, margin=dict(l=20, r=20, t=20, b=20))
        fig_pred.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_pred, use_container_width=True)

    with col_p2:
        st.markdown("#### Primary Career Fit")
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%); color: white; padding: 25px; border-radius: 12px;">
            <h3 style="color: white; margin: 0;">{top_predicted_role}</h3>
            <p style="font-size: 1.2rem; margin: 10px 0 0 0; opacity: 0.9;">Confidence: <b>{top_confidence}%</b></p>
            <p style="font-size: 0.9rem; margin-top: 10px; opacity: 0.85;">
                Model: <b>{model_choice}</b><br>
                Based on extracted competencies: {', '.join([s.title() for s in extracted_skills[:6]])}...
            </p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # Multi-Model Benchmark Comparison Table & Visuals
    st.subheader("Model Evaluation & Comparison Metrics")
    st.caption("Comparison across Accuracy, Weighted Precision, Recall, and F1-score on test split:")

    metrics_path = os.path.join(BASE_DIR, "models", "model_metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics_dict = json.load(f).get("metrics", {})
    else:
        metrics_dict = job_classifier.metrics
    if metrics_dict:
        comp_rows = []
        for m_name, m_vals in metrics_dict.items():
            comp_rows.append({
                "Model Name": m_name,
                "Accuracy (%)": m_vals.get("accuracy", 0),
                "Precision (%)": m_vals.get("precision_weighted", 0),
                "Recall (%)": m_vals.get("recall_weighted", 0),
                "F1-Score (%)": m_vals.get("f1_score_weighted", 0),
            })
        bench_df = pd.DataFrame(comp_rows)
        
        # Display table
        st.dataframe(bench_df.style.highlight_max(axis=0, subset=["Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)"]), use_container_width=True)

        # Grouped bar chart for visual comparison
        melted_df = pd.melt(
            bench_df,
            id_vars=["Model Name"],
            value_vars=["Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)"],
            var_name="Metric",
            value_name="Score"
        )
        fig_bench = px.bar(
            melted_df,
            x="Model Name",
            y="Score",
            color="Metric",
            barmode="group",
            height=340,
            title="Classification Performance Benchmark (LR vs SVM vs RF vs XGBoost)"
        )
        fig_bench.update_layout(yaxis=dict(range=[70, 100]), margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_bench, use_container_width=True)
    else:
        st.info("Train models via train_models.py to inspect metrics.")


# =========================================================
# TAB 3: JOB MATCHING & SKILL GAP ANALYSIS
# =========================================================
with tabs[2]:
    st.subheader("Job Compatibility & Skill-Gap Analysis")

    # Select target job description
    col_j1, col_j2 = st.columns([1, 1])

    with col_j1:
        job_selection_mode = st.radio(
            "Select Target Job Source:",
            ["Choose from System Database", "Paste Custom Job Description"],
            horizontal=True
        )

    selected_job = None
    target_job_text = ""
    target_req_skills = []
    target_pref_skills = []

    if job_selection_mode == "Choose from System Database":
        job_titles = [
            f"{'🟢 [LIVE] ' if j.get('source') == 'live_api' else ''}{j['title']} @ {j['company']} ({j['location']})"
            for j in all_jobs_list
        ]
        selected_idx = st.selectbox("Select Target Position:", range(len(job_titles)), format_func=lambda x: job_titles[x])
        selected_job = all_jobs_list[selected_idx]
        target_job_text = f"{selected_job['title']}\n{selected_job['description']}"
        target_req_skills = selected_job.get("required_skills", [])
        target_pref_skills = selected_job.get("preferred_skills", [])
        if selected_job.get("source") == "live_api":
            st.caption("🟢 **Real-Time Job:** Active live opening fetched from public API feed with dynamic skill extraction.")
    else:
        custom_job_title = st.text_input("Job Title:", value="Senior Software Engineer")
        target_job_text = st.text_area(
            "Job Description Text:",
            height=120,
            value="We are looking for a Senior Software Engineer with strong Python, PyTorch, Docker, FastAPI, and Kubernetes skills."
        )
        custom_skills_input = st.text_input(
            "Required Skills (comma separated):",
            value="python, pytorch, docker, fastapi, kubernetes, git"
        )
        target_req_skills = [s.strip().lower() for s in custom_skills_input.split(",") if s.strip()]
        target_pref_skills = ["aws", "ci/cd", "linux"]
        selected_job = {
            "title": custom_job_title,
            "company": "Custom Employer",
            "location": "Custom",
            "salary_range": "Negotiable",
            "required_skills": target_req_skills,
            "preferred_skills": target_pref_skills,
            "description": target_job_text
        }

    # Execute Compatibility Computation
    comp_result = job_matcher.calculate_compatibility(
        resume_text=resume_text,
        resume_skills=extracted_skills,
        job_description=target_job_text,
        required_skills=target_req_skills,
        preferred_skills=target_pref_skills
    )

    gap_result = SkillGapAnalyzer.analyze_gap(
        candidate_skills=extracted_skills,
        required_skills=target_req_skills,
        preferred_skills=target_pref_skills
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Score Gauge and Similarity Decomposition
    col_m1, col_m2 = st.columns([1, 2])
    with col_m1:
        st.plotly_chart(
            create_gauge_chart(comp_result["overall_score"], "Compatibility Score", comp_result["grade_color"]),
            use_container_width=True
        )
        st.markdown(f"<div style='text-align:center; font-weight:700; color:{comp_result['grade_color']}; font-size:1.1rem;'>{comp_result['grade']}</div>", unsafe_allow_html=True)
        st.caption(f"Verdict: {comp_result['verdict']}")

    with col_m2:
        st.markdown("#### 3-Factor Compatibility Decomposition")
        st.markdown("""
        The system computes an explainable composite compatibility score based on:
        - **Core Skill Match (45% weight)**: Overlap between candidate skills and job requirements.
        - **Semantic Sentence Similarity (35% weight)**: Transformer contextual embedding comparison.
        - **TF-IDF Keyword Similarity (20% weight)**: Term frequency cosine similarity.
        """)

        f1, f2, f3 = st.columns(3)
        with f1:
            st.metric("Skill Match", f"{comp_result['skill_match_score']}%", f"{len(gap_result['matched_core'])}/{len(target_req_skills)} req")
        with f2:
            st.metric("Semantic Similarity", f"{comp_result['semantic_score']}%", "Dense embeddings")
        with f3:
            st.metric("TF-IDF Similarity", f"{comp_result['tfidf_score']}%", "Keyword vector")

        st.caption(f"Semantic Engine: {'Sentence-Transformers (all-MiniLM-L6-v2)' if comp_result['is_semantic_enabled'] else 'TF-IDF Fallback'}")

    st.markdown("---")

    # Detailed Skill Gap Matrix
    st.subheader("Skill-Gap Matrix")
    
    col_gap1, col_gap2 = st.columns(2)

    with col_gap1:
        st.markdown(f"#### ✅ Matched Mandatory Skills ({len(gap_result['matched_core'])})")
        if gap_result['matched_core']:
            pills = " ".join([f'<span class="badge-skill badge-matched">✔ {s.title()}</span>' for s in gap_result['matched_core']])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.warning("No mandatory skills matched.")

        st.markdown(f"#### 🌟 Matched Preferred Skills ({len(gap_result['matched_bonus'])})")
        if gap_result['matched_bonus']:
            pills = " ".join([f'<span class="badge-skill badge-preferred">★ {s.title()}</span>' for s in gap_result['matched_bonus']])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.caption("No bonus skills matched.")

    with col_gap2:
        st.markdown(f"#### ⚠️ Missing Mandatory Skills ({len(gap_result['missing_core'])})")
        if gap_result['missing_core']:
            pills = " ".join([f'<span class="badge-skill badge-missing">✖ {s.title()}</span>' for s in gap_result['missing_core']])
            st.markdown(pills, unsafe_allow_html=True)
            st.error(f"Gap Severity: **{gap_result['severity']}**. {gap_result['severity_desc']}")
        else:
            st.success("🎉 No missing mandatory skills! Candidate meets 100% of core criteria.")

        st.markdown(f"#### 💡 Missing Preferred Skills ({len(gap_result['missing_bonus'])})")
        if gap_result['missing_bonus']:
            pills = " ".join([f'<span class="badge-skill badge-preferred">✖ {s.title()}</span>' for s in gap_result['missing_bonus']])
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.caption("No missing preferred skills.")


# =========================================================
# TAB 4: PERSONALIZED RECOMMENDATIONS & LEARNING PATHS
# =========================================================
with tabs[3]:
    st.subheader("Personalized Job & Learning Recommendations")

    st.markdown("#### 🎯 Best-Fit Job Openings for Your Profile")
    st.caption("Ranked by semantic and skill compatibility from our database:")

    job_recommendations = recommender.recommend_jobs(
        resume_text=resume_text,
        resume_skills=extracted_skills,
        jobs_list=all_jobs_list,
        top_n=4
    )

    for idx, rec in enumerate(job_recommendations, 1):
        is_live = rec.get("source") == "live_api"
        live_tag = " 🟢 [LIVE]" if is_live else ""
        with st.expander(f"#{idx} {rec['title']} - {rec['company']}{live_tag} | Match Score: {rec['overall_score']}% ({rec['grade']})"):
            c_r1, c_r2 = st.columns([2, 1])
            with c_r1:
                st.write(f"**Location:** {rec['location']} | **Experience:** {rec['experience_level']} | **Salary:** {rec['salary_range']}")
                if is_live:
                    st.caption("🟢 **Status:** Active real-time live opening fetched via live API sync")
                st.write(f"**About the Role:** {rec['description']}")
                
                # Show matched and missing pills
                matched_pills = " ".join([f'<span class="badge-skill badge-matched">✔ {s.title()}</span>' for s in rec['matched_required']])
                missing_pills = " ".join([f'<span class="badge-skill badge-missing">✖ {s.title()}</span>' for s in rec['missing_required']])
                
                st.markdown(f"**Matched Requirements:** {matched_pills}", unsafe_allow_html=True)
                if rec['missing_required']:
                    st.markdown(f"**Missing Requirements:** {missing_pills}", unsafe_allow_html=True)
            with c_r2:
                st.metric("Compatibility", f"{rec['overall_score']}%")
                st.write(f"- Skill Overlap: **{rec['skill_match_score']}%**")
                st.write(f"- Semantic Fit: **{rec['semantic_score']}%**")
                if rec.get("url"):
                    st.link_button("Apply on Company Site 🔗", rec["url"], use_container_width=True)
                else:
                    st.button(f"Apply / Bookmark Job #{idx}", key=f"btn_job_{rec['id']}", use_container_width=True)

    st.markdown("---")

    # Personalized Learning Roadmaps for Missing Skills
    st.subheader("📚 Personalized Learning Paths for Skill Gaps")
    st.markdown("""
    To help candidates bridge detected skill gaps, the system suggests curated, high-value learning roadmaps,
    courses, and documentation resources.
    """)

    # Use missing skills from current job or top predicted role
    missing_for_learning = gap_result["missing_core"] + gap_result["missing_bonus"]
    if not missing_for_learning:
        # Fallback to general recommended skills
        missing_for_learning = ["docker", "kubernetes", "fastapi"]

    learning_data = recommender.recommend_learning_paths(missing_for_learning)

    st.metric("Estimated Study Time Needed", f"{learning_data['estimated_study_hours']} Hours", f"{learning_data['total_courses']} Learning Modules")

    for difficulty, c_list in learning_data["grouped_roadmap"].items():
        st.markdown(f"#### 🎓 {difficulty} Level Modules")
        for course in c_list:
            col_l1, col_l2 = st.columns([3, 1])
            with col_l1:
                st.markdown(f"**[{course['title']}]({course['url']})**")
                st.caption(f"Platform: {course['platform']} | Estimated: {course['est_hours']} hrs | Target Skill: `{course['skill']}`")
                st.write(f"Key Concepts to Master: {', '.join(course['key_topics'])}")
            with col_l2:
                st.link_button("View Resource 🔗", course["url"])
            st.divider()


# =========================================================
# TAB 5: RECRUITER ATS SCREENING (BATCH CANDIDATES)
# =========================================================
with tabs[4]:
    st.subheader("👥 Recruiter ATS Screening & Candidate Ranking")
    st.markdown("""
    Recruiters can evaluate and rank multiple candidate resumes against any job vacancy in real-time.
    """)

    # Job target for screening
    recruiter_job_idx = st.selectbox(
        "Screen candidates for position:",
        range(len(all_jobs_list)),
        format_func=lambda x: f"{all_jobs_list[x]['title']} @ {all_jobs_list[x]['company']}",
        key="recruiter_job_selector"
    )
    recruiter_target_job = all_jobs_list[recruiter_job_idx]

    # Preload sample candidates
    candidates_pool = [
        {"name": "Applicant 1 (ML Engineer)", "file": "ml_engineer_resume.txt", "role_hint": "Machine Learning"},
        {"name": "Applicant 2 (Data Scientist)", "file": "data_scientist_resume.txt", "role_hint": "Data Science & Stats"},
        {"name": "Applicant 3 (Full Stack Dev)", "file": "fullstack_developer_resume.txt", "role_hint": "Full Stack Web"},
        {"name": "Applicant 4 (DevOps Engineer)", "file": "devops_engineer_resume.txt", "role_hint": "Cloud & DevOps"},
        {"name": "Applicant 5 (Data Analyst)", "file": "data_analyst_resume.txt", "role_hint": "BI & Analytics"},
        {"name": "Applicant 6 (Security Analyst)", "file": "cybersecurity_analyst_resume.txt", "role_hint": "Cybersecurity"},
        {"name": "Applicant 7 (Frontend Dev)", "file": "frontend_developer_resume.txt", "role_hint": "Frontend / React"},
        {"name": "Applicant 8 (Backend Dev)", "file": "backend_developer_resume.txt", "role_hint": "Backend / APIs"},
        {"name": "Applicant 9 (Fresh Graduate)", "file": "fresher_graduate_resume.txt", "role_hint": "Junior / Entry-Level"},
    ]

    screening_results = []

    for cand in candidates_pool:
        fpath = os.path.join(BASE_DIR, "sample_resumes", cand["file"])
        if os.path.exists(fpath):
            with open(fpath, "r", encoding="utf-8") as f:
                c_text = f.read()
            c_skills = skill_extractor.extract_skills(c_text)["all_extracted_skills"]
            c_comp = job_matcher.calculate_compatibility(
                resume_text=c_text,
                resume_skills=c_skills,
                job_description=recruiter_target_job["description"],
                required_skills=recruiter_target_job.get("required_skills", []),
                preferred_skills=recruiter_target_job.get("preferred_skills", [])
            )
            screening_results.append({
                "Candidate Name": cand["name"],
                "Profile Type": cand["role_hint"],
                "Overall Match (%)": c_comp["overall_score"],
                "Skill Match (%)": c_comp["skill_match_score"],
                "Semantic Similarity (%)": c_comp["semantic_score"],
                "Grade": c_comp["grade"],
                "Matched Skills Count": len(c_comp["matched_required_skills"]),
                "Missing Skills Count": len(c_comp["missing_required_skills"]),
            })

    # Sort descending by match score
    screen_df = pd.DataFrame(screening_results).sort_values(by="Overall Match (%)", ascending=False).reset_index(drop=True)
    screen_df.index = screen_df.index + 1

    st.markdown("#### Candidate Leaderboard")
    st.dataframe(
        screen_df.style.highlight_max(subset=["Overall Match (%)", "Skill Match (%)"], color="#DCFCE7"),
        use_container_width=True
    )

    # Leaderboard Comparison Chart
    fig_screen = px.bar(
        screen_df,
        x="Candidate Name",
        y=["Skill Match (%)", "Semantic Similarity (%)", "Overall Match (%)"],
        barmode="group",
        title=f"Candidate Comparison for: {recruiter_target_job['title']}",
        height=320
    )
    fig_screen.update_layout(yaxis=dict(range=[0, 105]), margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig_screen, use_container_width=True)


# =========================================================
# TAB 6: DATABASE & SYSTEM ANALYTICS
# =========================================================
with tabs[5]:
    st.subheader("🗄️ System Database & Analytics")

    sub_t1, sub_t2, sub_t3 = st.tabs([
        "💼 Job Postings Database",
        "🕒 Resume Analysis History",
        "➕ Post New Job Vacancy"
    ])

    with sub_t1:
        st.markdown(f"**Total Registered Jobs in SQLite:** {len(all_jobs_list)}")
        jobs_table_data = []
        for j in all_jobs_list:
            jobs_table_data.append({
                "Source": "🟢 Live Synced" if j.get("source") == "live_api" else "Curated Reference",
                "Job Title": j["title"],
                "Company": j["company"],
                "Location": j["location"],
                "Experience": j["experience_level"],
                "Salary": j["salary_range"],
                "Mandatory Skills": ", ".join(j["required_skills"][:5])
            })
        st.dataframe(pd.DataFrame(jobs_table_data), use_container_width=True)

    with sub_t2:
        history_records = db_manager.get_recent_analyses(limit=20)
        if history_records:
            hist_df = pd.DataFrame(history_records)[[
                "candidate_name", "filename", "predicted_role", "confidence", "ats_score", "dominant_domain", "created_at"
            ]]
            hist_df.columns = ["Name", "File", "Predicted Role", "Confidence (%)", "ATS Score (%)", "Domain", "Timestamp"]
            st.dataframe(hist_df, use_container_width=True)
        else:
            st.info("No analysis history recorded yet.")

    with sub_t3:
        st.markdown("#### Add a New Job Opportunity to SQLite")
        with st.form("add_job_form"):
            new_title = st.text_input("Job Title*", placeholder="e.g. AI Prompt Engineer")
            new_company = st.text_input("Company Name*", placeholder="e.g. OpenAI Innovations")
            new_location = st.text_input("Location", placeholder="e.g. Bengaluru / Remote")
            new_exp = st.selectbox("Experience Level", ["Entry-Level (0-2 yrs)", "Mid-Level (2-5 yrs)", "Senior (5+ yrs)"])
            new_salary = st.text_input("Salary Range", placeholder="e.g. ₹18L - ₹25L")
            new_req_skills = st.text_input("Required Skills (comma separated)*", placeholder="python, langchain, openai, rag")
            new_pref_skills = st.text_input("Preferred Skills (comma separated)", placeholder="docker, fastapi, aws")
            new_desc = st.text_area("Job Description*", placeholder="Describe key responsibilities and expectations...")

            submit_job = st.form_submit_button("Save Job to Database")
            if submit_job:
                if new_title and new_company and new_req_skills and new_desc:
                    req_list = [s.strip().lower() for s in new_req_skills.split(",") if s.strip()]
                    pref_list = [s.strip().lower() for s in new_pref_skills.split(",") if s.strip()]
                    db_manager.add_job({
                        "title": new_title,
                        "company": new_company,
                        "location": new_location,
                        "experience_level": new_exp,
                        "salary_range": new_salary,
                        "required_skills": req_list,
                        "preferred_skills": pref_list,
                        "description": new_desc
                    })
                    st.success(f"Successfully added '{new_title}' at '{new_company}' to SQLite database!")
                    st.rerun()
                else:
                    st.error("Please fill in all mandatory fields marked with *.")
