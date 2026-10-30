import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_deck(output_pptx_path):
    prs = Presentation()
    # 16:9 Widescreen
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Clean Color Palette
    c_navy = RGBColor(30, 58, 138)         # #1E3A8A - Deep Navy
    c_dark = RGBColor(15, 23, 42)          # #0F172A - Primary Dark Slate
    c_teal = RGBColor(13, 148, 136)        # #0D9488 - Teal Accent
    c_blue_bg = RGBColor(241, 245, 249)    # #F1F5F9 - Light Slate Fill
    c_card_border = RGBColor(203, 213, 225)# #CBD5E1 - Border Gray
    c_white = RGBColor(255, 255, 255)
    c_gray = RGBColor(100, 116, 139)       # #64748B - Muted Gray

    def add_header(slide, title_text, category="ACADEMIC PROJECT PRESENTATION"):
        # Category Tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(11.7), Inches(0.35))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(12)
        p_cat.font.bold = True
        p_cat.font.color.rgb = c_teal

        # Main Slide Title (Large & Bold)
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(11.7), Inches(0.8))
        tf = t_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(28)
        p.font.bold = True
        p.font.color.rgb = c_navy

        # Divider bar
        line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.5), Inches(11.733), Inches(0.03))
        line.fill.solid()
        line.fill.fore_color.rgb = c_teal
        line.line.fill.background()

        # Footer
        f_box = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(11.7), Inches(0.35))
        tf_f = f_box.text_frame
        p_f = tf_f.paragraphs[0]
        p_f.text = "AI-Powered Resume Analysis & Job Recommendation System  |  Machine Learning (CSE_3148 / CSE_3125)"
        p_f.font.size = Pt(11)
        p_f.font.color.rgb = c_gray

    # ==============================================================
    # SLIDE 1: TITLE SLIDE (Big, High-Contrast Typography)
    # ==============================================================
    s1 = prs.slides.add_slide(blank_layout)

    # Accent Top Banner
    top_bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.2))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = c_teal
    top_bar.line.fill.background()

    # Left Hero Box
    hero = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.85), Inches(7.6), Inches(5.8))
    hero.fill.solid()
    hero.fill.fore_color.rgb = c_navy
    hero.line.fill.background()

    tf_hero = hero.text_frame
    tf_hero.word_wrap = True
    tf_hero.vertical_anchor = MSO_ANCHOR.MIDDLE

    p0 = tf_hero.paragraphs[0]
    p0.text = "MACHINE LEARNING PROJECT DEFENSE\n"
    p0.font.size = Pt(13)
    p0.font.bold = True
    p0.font.color.rgb = c_teal

    p1 = tf_hero.add_paragraph()
    p1.text = "AI-Powered Resume Analysis & Job Recommendation System\n"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = c_white

    p2 = tf_hero.add_paragraph()
    p2.text = "Automated ATS Quality Scoring, Multi-Class ML Role Prediction, Explainable Hybrid Matching & Intelligent Skill-Gap Diagnostics"
    p2.font.size = Pt(15)
    p2.font.color.rgb = RGBColor(226, 232, 240)

    # Right Metadata Card
    card_meta = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.7), Inches(0.85), Inches(3.8), Inches(5.8))
    card_meta.fill.solid()
    card_meta.fill.fore_color.rgb = c_blue_bg
    card_meta.line.color.rgb = c_card_border
    card_meta.line.width = Pt(1.5)

    tf_m = card_meta.text_frame
    tf_m.word_wrap = True
    tf_m.vertical_anchor = MSO_ANCHOR.MIDDLE

    pm0 = tf_m.paragraphs[0]
    pm0.text = "PROJECT METADATA\n"
    pm0.font.size = Pt(14)
    pm0.font.bold = True
    pm0.font.color.rgb = c_navy

    pm1 = tf_m.add_paragraph()
    pm1.text = "Course / Subject:\nMachine Learning [CSE_3148 / CSE_3125]\n"
    pm1.font.size = Pt(13)
    pm1.font.color.rgb = c_dark

    pm2 = tf_m.add_paragraph()
    pm2.text = "Faculty Guide:\nShreya Banerjee\n"
    pm2.font.size = Pt(13)
    pm2.font.bold = True
    pm2.font.color.rgb = c_dark

    pm3 = tf_m.add_paragraph()
    pm3.text = "Team Members:\n• Tejaswini Singh (245805418)\n• Shriya Shet (245805454)\n"
    pm3.font.size = Pt(13)
    pm3.font.color.rgb = c_dark

    pm4 = tf_m.add_paragraph()
    pm4.text = "Date: October 2026"
    pm4.font.size = Pt(12)
    pm4.font.color.rgb = c_gray

    # ==============================================================
    # SLIDE 2: PROBLEM STATEMENT & MOTIVATION
    # ==============================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_header(s2, "Problem Statement & Project Motivation", "THE CHALLENGE")

    cards_data = [
        ("1. Screening Latency", [
            "High Volumes: Hundreds of applicants per role.",
            "Manual Fatigue: 6 to 8 seconds spent per resume.",
            "Human Bias: Evaluation inconsistency & fatigue."
        ]),
        ("2. Keyword ATS Flaws", [
            "Rigid Matching: Rejects profiles for missing exact words.",
            "Synonym Failure: Misses 'K8s' vs 'Kubernetes'.",
            "Context Blind: Ignores actual project depth."
        ]),
        ("3. The Guidance Void", [
            "One-Way Filter: Rejections offer zero feedback.",
            "Hidden Deficits: Candidates unaware of missing skills.",
            "No Learning Path: No roadmap on how to upskill."
        ])
    ]

    col_w = Inches(3.64)
    for idx, (title, bullets) in enumerate(cards_data):
        c_box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.05), Inches(1.85), col_w, Inches(4.8))
        c_box.fill.solid()
        c_box.fill.fore_color.rgb = c_blue_bg
        c_box.line.color.rgb = c_card_border
        c_box.line.width = Pt(1.5)
        
        tfc = c_box.text_frame
        tfc.word_wrap = True
        
        p = tfc.paragraphs[0]
        p.text = f"{title}\n"
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = c_navy

        for b in bullets:
            p = tfc.add_paragraph()
            p.text = f"• {b}\n"
            p.font.size = Pt(13.5)
            p.font.color.rgb = c_dark

    # ==============================================================
    # SLIDE 3: THREE-TIER SYSTEM ARCHITECTURE
    # ==============================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_header(s3, "Three-Tier System Architecture & Tech Stack", "SYSTEM DESIGN")

    arch_cards = [
        ("🖥️ FRONTEND LAYER", [
            "Streamlit Web Dashboard (app.py)",
            "Plotly Interactive Visuals (Radar & Gauges)",
            "6 Dedicated Tabs (Profile to Recruiter)",
            "Color-coded HTML/CSS Skill Badges"
        ]),
        ("⚙️ BACKEND & ML ENGINE", [
            "Text Parser: PyMuPDF & python-docx",
            "NLP: 1,000+ Taxonomy with Regex boundaries",
            "4 ML Models: SVM, Random Forest, LR, XGBoost",
            "Sentence-BERT: 384-d semantic vectors",
            "Live REST API: Real-time job synchronizer"
        ]),
        ("🗄️ DATABASE & STORAGE", [
            "SQLite Engine: resumes_database.db",
            "Jobs Table: Reference + Live synced jobs",
            "History Table: Candidate audit logs",
            "Learning Catalog: Curated course roadmaps"
        ])
    ]

    for idx, (title, bullets) in enumerate(arch_cards):
        a_box = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 4.05), Inches(1.85), col_w, Inches(4.8))
        a_box.fill.solid()
        a_box.fill.fore_color.rgb = c_blue_bg
        a_box.line.color.rgb = c_teal if idx != 1 else c_navy
        a_box.line.width = Pt(1.8)
        
        tfa = a_box.text_frame
        tfa.word_wrap = True
        
        p = tfa.paragraphs[0]
        p.text = f"{title}\n"
        p.font.size = Pt(17)
        p.font.bold = True
        p.font.color.rgb = c_navy

        for b in bullets:
            p = tfa.add_paragraph()
            p.text = f"• {b}\n"
            p.font.size = Pt(13)
            p.font.color.rgb = c_dark

    # ==============================================================
    # SLIDE 4: END-TO-END METHODOLOGY & PIPELINE
    # ==============================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_header(s4, "End-to-End Execution Methodology", "WORKFLOW PHASES")

    phase_cards = [
        ("Phase 1: Ingestion & ATS Audit", [
            "Multi-format PDF, DOCX, TXT parser.",
            "5-Factor ATS Quality Health Score:",
            "  - Word count (400-900 words)",
            "  - Essential resume sections",
            "  - Contact info detection",
            "  - Skill density & Action verbs"
        ]),
        ("Phase 2: Taxonomy Extraction", [
            "1,000+ skills across 11 tech domains.",
            "Boundary-aware Regex matching.",
            "Resolves synonyms (K8s -> Kubernetes).",
            "Groups: Languages, Frameworks, Cloud, Databases, and Tools."
        ]),
        ("Phase 3: ML Role Prediction", [
            "TF-IDF n-gram vectorization (3,000 max).",
            "Predicts across 10 industry tracks.",
            "Simultaneous 4-model evaluation.",
            "Calibrated confidence probability."
        ]),
        ("Phase 4: Hybrid Match & Roadmap", [
            "Explainable 3-factor match score.",
            "Identifies missing mandatory skills.",
            "Scores Gap Severity (High / Low).",
            "Links to curated courses & hours."
        ])
    ]

    p_w = Inches(2.75)
    for idx, (title, bullets) in enumerate(phase_cards):
        p_box = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + idx * 2.98), Inches(1.85), p_w, Inches(4.8))
        p_box.fill.solid()
        p_box.fill.fore_color.rgb = c_blue_bg
        p_box.line.color.rgb = c_card_border
        p_box.line.width = Pt(1.5)
        
        tfp = p_box.text_frame
        tfp.word_wrap = True
        
        p = tfp.paragraphs[0]
        p.text = f"{title}\n"
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = c_navy

        for b in bullets:
            p = tfp.add_paragraph()
            p.text = f"• {b}\n"
            p.font.size = Pt(12)
            p.font.color.rgb = c_dark

    # ==============================================================
    # SLIDE 5: MACHINE LEARNING BENCHMARKING (Big Fonts Table & Insights)
    # ==============================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_header(s5, "Supervised Machine Learning: 4-Model Benchmark", "EMPIRICAL RESULTS")

    # Table on Left
    t_shape = s5.shapes.add_table(5, 5, Inches(0.8), Inches(1.85), Inches(7.6), Inches(3.3))
    table = t_shape.table

    table_data = [
        ["Model Name", "Accuracy", "Precision", "Recall", "F1-Score"],
        ["Support Vector Machine (LinearSVC) 🏆", "90.86%", "92.03%", "90.86%", "90.83%"],
        ["Random Forest Classifier", "85.14%", "86.54%", "85.14%", "85.03%"],
        ["Logistic Regression", "84.57%", "85.93%", "84.57%", "84.55%"],
        ["XGBoost (Boosted Trees)", "83.43%", "84.37%", "83.43%", "83.43%"]
    ]

    for r_idx, row in enumerate(table_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER
            p.font.size = Pt(12.5)
            if r_idx == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = c_navy
                p.font.bold = True
                p.font.color.rgb = c_white
                p.font.size = Pt(13)
            elif r_idx == 1:
                cell.fill.solid()
                cell.fill.fore_color.rgb = RGBColor(236, 253, 245) # Light Green
                p.font.bold = True
                p.font.color.rgb = c_dark
                p.font.size = Pt(13)
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = c_white
                p.font.color.rgb = c_dark

    # Bottom Summary Callout on Left
    pill = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.35), Inches(7.6), Inches(1.3))
    pill.fill.solid()
    pill.fill.fore_color.rgb = RGBColor(239, 246, 255)
    pill.line.color.rgb = c_teal
    pill.line.width = Pt(1.5)
    tf_pill = pill.text_frame
    tf_pill.word_wrap = True
    p = tf_pill.paragraphs[0]
    p.text = "🎯 Benchmark Summary: Support Vector Machine (LinearSVC) achieved the peak score across all metrics with 90.86% Accuracy and 90.83% F1-score on the independent test set."
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_navy

    # Insights Card on Right
    ins_box = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.7), Inches(1.85), Inches(3.8), Inches(4.8))
    ins_box.fill.solid()
    ins_box.fill.fore_color.rgb = c_blue_bg
    ins_box.line.color.rgb = c_card_border
    ins_box.line.width = Pt(1.5)
    tfi = ins_box.text_frame
    tfi.word_wrap = True

    p = tfi.paragraphs[0]
    p.text = "🔬 Why SVM Outperformed:\n"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_navy

    insights = [
        "Sparse High-Dimensionality: TF-IDF text features create 3,000 dimensions. Linear hyperplanes excel in sparse geometric spaces.",
        "Overfitting Resistance: Maximum-margin separation avoids memorizing noise.",
        "Zero Label Leakage: Engineered corpus (700 balanced profiles) without role titles in text ensures genuine generalization.",
        "Probability Calibration: Integrated CalibratedClassifierCV ensures reliable confidence rankings."
    ]
    for ins in insights:
        p = tfi.add_paragraph()
        p.text = f"• {ins}\n"
        p.font.size = Pt(12)
        p.font.color.rgb = c_dark

    # ==============================================================
    # SLIDE 6: EXPLAINABLE HYBRID MATCHING & SKILL GAP
    # ==============================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_header(s6, "Explainable Hybrid Compatibility & Skill-Gap Analysis", "CORE MATCHING ALGORITHM")

    # Formula Card Top
    f_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(11.7), Inches(1.7))
    f_card.fill.solid()
    f_card.fill.fore_color.rgb = c_navy
    f_card.line.fill.background()
    tff = f_card.text_frame
    tff.word_wrap = True

    p = tff.paragraphs[0]
    p.text = "EXPLAINABLE 3-FACTOR COMPOSITE MATCH FORMULA:\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_teal

    p = tff.add_paragraph()
    p.text = "Overall Score = (0.45 × Core Skills) + (0.35 × Sentence-BERT) + (0.20 × TF-IDF Cosine)"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = c_white

    p = tff.add_paragraph()
    p.text = "• 45% Core Skills: Confirms mandatory hard requirements (Python, Docker) are never skipped.\n• 35% Sentence-BERT: Understands synonymous meaning and contextual experience beyond exact keywords.\n• 20% TF-IDF Cosine: Verifies broad lexical domain and terminology alignment."
    p.font.size = Pt(12)
    p.font.color.rgb = RGBColor(226, 232, 240)

    # Bottom Left: Skill Gap
    sg_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(3.75), Inches(5.7), Inches(2.9))
    sg_card.fill.solid()
    sg_card.fill.fore_color.rgb = c_blue_bg
    sg_card.line.color.rgb = c_card_border
    sg_card.line.width = Pt(1.5)
    tfsg = sg_card.text_frame
    tfsg.word_wrap = True

    p = tfsg.paragraphs[0]
    p.text = "🧩 Skill-Gap Matrix\n"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_navy

    sg_pts = [
        "Matched Skills (Green): Confirms verified competencies.",
        "Missing Skills (Red): Pinpoints critical missing requirements.",
        "Bonus Skills (Amber): Recognizes extra desirable skills.",
        "Severity Index: Scores High / Low gap urgency."
    ]
    for pt in sg_pts:
        p = tfsg.add_paragraph()
        p.text = f"• {pt}\n"
        p.font.size = Pt(13)
        p.font.color.rgb = c_dark

    # Bottom Right: Learning Paths
    lr_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(3.75), Inches(5.7), Inches(2.9))
    lr_card.fill.solid()
    lr_card.fill.fore_color.rgb = c_blue_bg
    lr_card.line.color.rgb = c_card_border
    lr_card.line.width = Pt(1.5)
    tflr = lr_card.text_frame
    tflr.word_wrap = True

    p = tflr.paragraphs[0]
    p.text = "📚 Actionable Learning Roadmaps\n"
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = c_navy

    lr_pts = [
        "Closes Feedback Loop: Replaces rejection with guidance.",
        "Curated Courses: DeepLearning.AI, Coursera, Docker Docs.",
        "Syllabus & Difficulty: Recommends targeted modules.",
        "Study Hours: Realistic time estimates (e.g. 25 hrs)."
    ]
    for pt in lr_pts:
        p = tflr.add_paragraph()
        p.text = f"• {pt}\n"
        p.font.size = Pt(13)
        p.font.color.rgb = c_dark

    # ==============================================================
    # SLIDE 7: LIVE DATA SYNC & KEY NOVELTIES
    # ==============================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_header(s7, "Real-Time Job Ingestion & Key Project Novelties", "TECHNICAL HIGHLIGHTS")

    # Left: Live Data Feature
    live_card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.85), Inches(5.7), Inches(4.8))
    live_card.fill.solid()
    live_card.fill.fore_color.rgb = c_blue_bg
    live_card.line.color.rgb = c_teal
    live_card.line.width = Pt(1.8)
    tflive = live_card.text_frame
    tflive.word_wrap = True

    p = tflive.paragraphs[0]
    p.text = "🌐 Live Job Synchronization\n"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = c_navy

    live_bullets = [
        "Public REST API: Connects to Remotive API to fetch active tech openings over the internet.",
        "Dynamic NLP Ingestion: Cleans HTML descriptions and extracts required skills on-the-fly.",
        "SQLite Persistence: Stores live jobs alongside curated reference jobs with source tags.",
        "1-Click Apply: Recommendations include direct 'Apply on Company Site' external URL links.",
        "UI Tagging: Clear 🟢 [LIVE] badges distinguish real market jobs from static benchmarks."
    ]
    for b in live_bullets:
        p = tflive.add_paragraph()
        p.text = f"• {b}\n"
        p.font.size = Pt(13)
        p.font.color.rgb = c_dark

    # Right: Novelties
    nov_card = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.85), Inches(5.7), Inches(4.8))
    nov_card.fill.solid()
    nov_card.fill.fore_color.rgb = c_blue_bg
    nov_card.line.color.rgb = c_navy
    nov_card.line.width = Pt(1.8)
    tfnov = nov_card.text_frame
    tfnov.word_wrap = True

    p = tfnov.paragraphs[0]
    p.text = "✨ Key Project Novelties\n"
    p.font.size = Pt(17)
    p.font.bold = True
    p.font.color.rgb = c_navy

    nov_bullets = [
        "1. Explainable Hybrid Matching: Transparent 3-factor weighting instead of black-box scoring.",
        "2. Zero Label Leakage: Academic dataset engineering prevents memorization of job titles.",
        "3. Dual Utility: Solves needs for both applicants (diagnostics) and recruiters (batch ranking).",
        "4. Feedback-Driven: Transforms ATS rejection into structured upskilling guidance.",
        "5. Semantic Robustness: Handles synonyms and terminology variations with Sentence-BERT."
    ]
    for b in nov_bullets:
        p = tfnov.add_paragraph()
        p.text = f"• {b}\n"
        p.font.size = Pt(13)
        p.font.color.rgb = c_dark

    # ==============================================================
    # SLIDE 8: CONCLUSION & Q&A
    # ==============================================================
    s8 = prs.slides.add_slide(blank_layout)

    # Accent Top Banner
    top_bar8 = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.2))
    top_bar8.fill.solid()
    top_bar8.fill.fore_color.rgb = c_teal
    top_bar8.line.fill.background()

    # Left Summary Card
    concl_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.85), Inches(7.6), Inches(5.8))
    concl_box.fill.solid()
    concl_box.fill.fore_color.rgb = c_navy
    concl_box.line.fill.background()
    tfc = concl_box.text_frame
    tfc.word_wrap = True
    tfc.vertical_anchor = MSO_ANCHOR.MIDDLE

    p = tfc.paragraphs[0]
    p.text = "CONCLUSION & SUMMARY\n"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = c_teal

    p = tfc.add_paragraph()
    p.text = "Project Takeaways:\n"
    p.font.size = Pt(24)
    p.font.bold = True
    p.font.color.rgb = c_white

    c_pts = [
        "Delivered a complete, operational AI Resume Analyzer & Job Recommender.",
        "Support Vector Machine achieved 90.86% Accuracy & 90.83% F1-score.",
        "3-Factor hybrid matching overcomes keyword fragility with dense BERT embeddings.",
        "Real-time live job ingestion bridges academic modeling with real market vacancies."
    ]
    for pt in c_pts:
        p = tfc.add_paragraph()
        p.text = f"✔ {pt}\n"
        p.font.size = Pt(13.5)
        p.font.color.rgb = RGBColor(226, 232, 240)

    p = tfc.add_paragraph()
    p.text = "Future Scope: Scanned PDF OCR, fine-tuning domain LLMs, and multi-lingual parsing."
    p.font.size = Pt(12)
    p.font.color.rgb = c_teal

    # Right Thank You / Q&A Card
    qa_box = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(8.7), Inches(0.85), Inches(3.8), Inches(5.8))
    qa_box.fill.solid()
    qa_box.fill.fore_color.rgb = c_blue_bg
    qa_box.line.color.rgb = c_card_border
    qa_box.line.width = Pt(1.5)
    tfqa = qa_box.text_frame
    tfqa.word_wrap = True
    tfqa.vertical_anchor = MSO_ANCHOR.MIDDLE

    p = tfqa.paragraphs[0]
    p.text = "THANK YOU!\n"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = c_navy

    p = tfqa.add_paragraph()
    p.text = "Open for Viva Defense & Live Demo Demonstration.\n"
    p.font.size = Pt(14)
    p.font.color.rgb = c_dark

    p = tfqa.add_paragraph()
    p.text = "Faculty Guide:\nShreya Banerjee\n"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = c_teal

    p = tfqa.add_paragraph()
    p.text = "Team Members:\n• Tejaswini Singh (245805418)\n• Shriya Shet (245805454)\n"
    p.font.size = Pt(13)
    p.font.color.rgb = c_dark

    p = tfqa.add_paragraph()
    p.text = "Course: Machine Learning\nCSE_3148 / CSE_3125"
    p.font.size = Pt(12)
    p.font.color.rgb = c_gray

    prs.save(output_pptx_path)
    print(f"Large-font presentation saved successfully at: {output_pptx_path}")

if __name__ == "__main__":
    v2_path = r"C:\Users\tejas\.gemini\antigravity\scratch\ai-resume-analyzer\PROJECT_PRESENTATION_v2.pptx"
    out_path = r"C:\Users\tejas\.gemini\antigravity\scratch\ai-resume-analyzer\PROJECT_PRESENTATION.pptx"
    
    # Save v2
    create_deck(v2_path)
    print(f"Large-font presentation saved to: {v2_path}")
    
    # Try overwriting original if not locked
    try:
        import shutil
        shutil.copyfile(v2_path, out_path)
        print(f"Successfully updated original file at: {out_path}")
    except Exception as e:
        print(f"Note: Original file is currently open in PowerPoint ({e}). Use PROJECT_PRESENTATION_v2.pptx!")
