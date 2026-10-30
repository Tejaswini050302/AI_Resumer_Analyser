import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def create_report(output_docx_path):
    doc = Document()
    base_dir = os.path.dirname(os.path.abspath(__file__))
    screenshots_dir = os.path.join(base_dir, "docs", "screenshots")

    # Set 1-inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.header_distance = Inches(0.5)
        section.footer_distance = Inches(0.5)

        # Header
        header_p = section.header.paragraphs[0]
        header_p.text = "AI-Powered Resume Analysis & Job Recommendation System  |  Machine Learning (CSE_3148)"
        header_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        header_p.style.font.size = Pt(8.5)
        header_p.style.font.color.rgb = RGBColor(100, 116, 139)

        # Footer
        footer_p = section.footer.paragraphs[0]
        footer_p.text = "Faculty Guide: Shreya Banerjee  •  Tejaswini Singh (245805418) & Shriya Shet (245805454)"
        footer_p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        footer_p.style.font.size = Pt(8.5)
        footer_p.style.font.color.rgb = RGBColor(100, 116, 139)

    # Styles & Colors
    c_navy = RGBColor(30, 58, 138)       # #1E3A8A
    c_dark = RGBColor(15, 23, 42)        # #0F172A
    c_teal = RGBColor(13, 148, 136)      # #0D9488
    c_gray = RGBColor(100, 116, 139)     # #64748B

    def add_h1(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(16)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(14)
        run.font.color.rgb = c_navy
        return p

    def add_h2(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(11.5)
        run.font.color.rgb = c_teal
        return p

    def add_h3(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.keep_with_next = True
        run = p.add_run(text)
        run.bold = True
        run.font.size = Pt(10.5)
        run.font.color.rgb = c_dark
        return p

    def add_body(text):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.line_spacing = 1.15
        run = p.add_run(text)
        run.font.size = Pt(10)
        run.font.color.rgb = c_dark
        return p

    def add_bullet(text, bold_prefix=""):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_b = p.add_run(bold_prefix)
            r_b.bold = True
            r_b.font.size = Pt(10)
            r_b.font.color.rgb = c_navy
        r_t = p.add_run(text)
        r_t.font.size = Pt(10)
        r_t.font.color.rgb = c_dark
        return p

    def add_figure(image_filename, fig_num, fig_title, fig_caption):
        img_path = os.path.join(screenshots_dir, image_filename)
        if os.path.exists(img_path):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(10)
            p_img.paragraph_format.space_after = Pt(4)
            p_img.paragraph_format.keep_with_next = True
            run = p_img.add_run()
            run.add_picture(img_path, width=Inches(6.0))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(12)
            
            r_bold = p_cap.add_run(f"Figure {fig_num}: {fig_title}. ")
            r_bold.bold = True
            r_bold.font.size = Pt(9)
            r_bold.font.color.rgb = c_navy

            r_text = p_cap.add_run(fig_caption)
            r_text.italic = True
            r_text.font.size = Pt(8.5)
            r_text.font.color.rgb = c_gray

    # =============================================================
    # TITLE BLOCK & METADATA
    # =============================================================
    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(0)
    p_meta.paragraph_format.space_after = Pt(2)
    r_meta = p_meta.add_run("ACADEMIC MINI PROJECT REPORT  |  MACHINE LEARNING (CSE_3148)")
    r_meta.bold = True
    r_meta.font.size = Pt(10)
    r_meta.font.color.rgb = c_teal

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(2)
    p_title.paragraph_format.space_after = Pt(4)
    r_title = p_title.add_run("AI-Powered Resume Analysis and Job Recommendation System")
    r_title.bold = True
    r_title.font.size = Pt(20)
    r_title.font.color.rgb = c_navy

    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_before = Pt(0)
    p_sub.paragraph_format.space_after = Pt(10)
    r_sub = p_sub.add_run("Semantic Parsing, Multi-Class ML Role Prediction, Explainable Hybrid Matching & Live Job Synchronization")
    r_sub.font.size = Pt(10.5)
    r_sub.font.color.rgb = c_gray

    # Metadata Summary Box
    tbl_meta = doc.add_table(rows=2, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_info = [
        [("Course Code & Title:", " Machine Learning (CSE_3148)"), ("Due Date of Submission:", " 30th October 2026")],
        [("Faculty Guide:", " Shreya Banerjee"), ("Architecture:", " Streamlit + NLP + Scikit-Learn + SQLite")]
    ]
    for r_idx, row in enumerate(meta_info):
        for c_idx, (k, v) in enumerate(row):
            cell = tbl_meta.cell(r_idx, c_idx)
            set_cell_background(cell, "F1F5F9")
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            rk = p.add_run(k)
            rk.bold = True
            rk.font.size = Pt(9)
            rk.font.color.rgb = c_navy
            rv = p.add_run(v)
            rv.font.size = Pt(9)
            rv.font.color.rgb = c_dark

    doc.add_paragraph().paragraph_format.space_after = Pt(4)

    # Team Members Table
    t_team = doc.add_table(rows=3, cols=3)
    t_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    team_headers = ["S. No.", "Student Name", "Registration Number"]
    team_data = [
        ["1.", "Tejaswini Singh", "245805418"],
        ["2.", "Shriya Shet", "245805454"]
    ]
    for c_idx, h in enumerate(team_headers):
        cell = t_team.cell(0, c_idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row in enumerate(team_data):
        for c_idx, val in enumerate(row):
            cell = t_team.cell(r_idx + 1, c_idx)
            set_cell_background(cell, "F8FAFC" if r_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx in [0, 2] else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.size = Pt(9)
            if c_idx == 1:
                r.bold = True
            r.font.color.rgb = c_dark

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # =============================================================
    # 1. ABSTRACT
    # =============================================================
    add_h1("1. Abstract")
    add_body(
        "In modern talent acquisition, recruitment teams face overwhelming application volumes, receiving hundreds of resumes for every "
        "advertised vacancy. Manual document screening is slow, resource-intensive, and inherently prone to unconscious human bias and cognitive fatigue, "
        "with studies indicating that recruiters spend merely 6 to 8 seconds scanning an individual resume. Concurrently, legacy Applicant Tracking "
        "Systems (ATS) depend on rigid, exact keyword matching; candidates who express identical competencies using industry synonyms (such as 'K8s' "
        "versus 'Kubernetes' or 'container orchestration' versus 'Docker') are routinely and erroneously rejected. Furthermore, conventional job portals "
        "function strictly as one-way rejection funnels, offering job seekers zero constructive feedback regarding missing competencies."
    )
    add_body(
        "To resolve these structural bottlenecks, this project presents an end-to-end AI-Powered Resume Analysis and Job Recommendation System. "
        "The system parses resumes across PDF, DOCX, and TXT formats using PyMuPDF and python-docx, segments structural sections, extracts contact coordinates, "
        "and computes an automated 5-factor ATS quality health score. Technical competencies are identified using a curated 1,000+ skill taxonomy covering "
        "11 specialized domains with boundary-aware alias resolution. A multi-class machine learning classification engine benchmarks four algorithms—Support "
        "Vector Machine (LinearSVC), Random Forest, Logistic Regression, and XGBoost—trained on 700 balanced candidate profiles without target label leakage. "
        "Empirical evaluations prove that Support Vector Machine achieves superior classification performance with 90.86% accuracy and a 90.83% weighted F1-score. "
        "Candidate-job alignment is computed via an explainable 3-factor hybrid matching engine that integrates core skill overlap (45%), dense contextual "
        "embeddings via Sentence-Transformers (all-MiniLM-L6-v2) (35%), and lexical TF-IDF cosine similarity (20%). A granular Skill-Gap Matrix pinpoints "
        "mandatory vs. preferred deficits, calculates gap severity, and suggests curated learning roadmaps with realistic study timelines. Finally, a real-time "
        "REST API synchronization client connects to public job feeds (Remotive) to ingest live vacancies directly into an embedded SQLite database. "
        "The complete framework is deployed as an interactive web dashboard via Streamlit and Plotly."
    )

    # =============================================================
    # 2. INTRODUCTION
    # =============================================================
    add_h1("2. Introduction")
    add_body(
        "The recruitment domain has transformed drastically with the rise of digital employment platforms, remote working arrangements, and single-click "
        "job applications. While these innovations have expanded career accessibility, they have created an unprecedented screening dilemma for organizations. "
        "Talent acquisition teams are flooded with massive applicant pools, rendering thorough manual review practically impossible."
    )
    add_body(
        "Existing commercial ATS platforms present critical operational limitations:"
    )
    add_bullet(" Recruiters scan resumes in 6 to 8 seconds, resulting in heuristic-driven rejections and subjective bias.", "Cognitive Fatigue & Human Bias:")
    add_bullet(" Early-generation ATS engines enforce rigid string equality checks. A resume listing 'Postgres' or 'Relational Database' will fail a filter searching strictly for 'PostgreSQL'.", "Brittleness of Lexical Keyword Matching:")
    add_bullet(" Candidates who fail automated screening receive automated rejection notices devoid of diagnostic advice, leaving them uninformed on how to upskill effectively.", "The Guidance Void in Career Portals:")
    add_bullet(" Most research prototypes rely on static, pre-packaged CSV datasets that do not reflect real-time market hiring criteria.", "Lack of Real-Time Market Integration:")
    add_body(
        "This project introduces an intelligent, transparent, and dual-purpose recruitment screening platform. By synergizing Natural Language Processing, "
        "supervised classification, contextual transformer embeddings, and relational database persistence, the platform simultaneously empowers corporate "
        "recruiters with high-throughput batch screening and equips job applicants with diagnostic ATS feedback and actionable upskilling roadmaps."
    )

    # =============================================================
    # 3. OBJECTIVE
    # =============================================================
    add_h1("3. Objective")
    add_body("The primary technical objectives of this project are:")
    add_bullet(" Build a robust ingestion engine supporting PDF, DOCX, and TXT files, extracting contact coordinates (Email, Phone, LinkedIn, GitHub) and scoring ATS formatting across 5 dimensions.", "1. Multi-Format Parsing & ATS Quality Scoring:")
    add_bullet(" Implement a boundary-aware regular expression engine driven by an 11-domain taxonomy encompassing over 1,000 skills with alias resolution.", "2. Domain-Aware Skill Extraction:")
    add_bullet(" Train and benchmark four multi-class classification models (SVM, Random Forest, Logistic Regression, XGBoost) to predict suitability across 10 industry tracks without label leakage.", "3. Supervised Machine Learning Role Classification:")
    add_bullet(" Formulate a 3-factor composite compatibility index synergizing core skill overlap (45%), dense Sentence-BERT contextual embeddings (35%), and lexical TF-IDF cosine similarity (20%).", "4. Explainable Hybrid Job Compatibility Scoring:")
    add_bullet(" Deconstruct target job descriptions into verified core skills, missing mandatory requirements, and bonus preferred skills with a quantitative Gap Severity Index.", "5. Granular Skill-Gap Diagnostics:")
    add_bullet(" Generate targeted instructional roadmaps mapping missing competencies directly to recognized instructional platforms (Coursera, DeepLearning.AI, Docker Docs) with estimated study hours.", "6. Personalized Career Upskilling Pathways:")
    add_bullet(" Implement an automated REST API ingestion pipeline connecting to live job boards (Remotive) to batch-upsert active market openings into an embedded SQLite database.", "7. Real-Time Job Ingestion & Market Sync:")

    # =============================================================
    # 4. DATA SOURCE
    # =============================================================
    add_h1("4. Data Source")
    add_body("The system operates on four synchronized data layers to ensure rigor, real-world relevance, and reproducibility:")

    add_h2("4.1 Curated Skills Taxonomy (skills_dataset.json)")
    add_body(
        "A hierarchical repository cataloging over 1,000 technical competencies across 11 industry domains: Programming Languages, "
        "Machine Learning & Data Science, Web Frameworks, Cloud & DevOps, Database Systems, Cybersecurity & Networking, Mobile Development, "
        "Software Engineering Methodologies, and Professional Competencies. The taxonomy maps colloquial abbreviations to canonical identifiers "
        "(e.g., 'K8s' -> 'Kubernetes', 'tf' -> 'TensorFlow', 'scikit' -> 'Scikit-Learn') using regex word boundaries to prevent substring collisions."
    )

    add_h2("4.2 Balanced Resume Training Corpus (resume_training_data.csv)")
    add_body(
        "A balanced corpus of 700 candidate profiles synthesized across 10 specialized career tracks (70 profiles per track). "
        "To guarantee academic integrity and avoid artificial metric inflation, target label leakage was strictly eliminated: role titles "
        "(e.g., 'Backend Developer') never appear within the resume text. Each profile models authentic engineering resumes by combining "
        "3 to 5 core domain competencies, 2 to 3 universal engineering tools (Git, Linux, CI/CD, Docker), cross-disciplinary skill overlaps "
        "(e.g., Data Scientists utilizing FastAPI; ML Engineers using PostgreSQL), and realistic professional achievement statements."
    )

    add_h2("4.3 Reference Job Descriptions & Real-Time Live Feed (resumes_database.db)")
    add_body(
        "The job matching subsystem operates on a dual-tier repository: (1) A curated baseline of 10 comprehensive job postings "
        "stored in an embedded SQLite database (resumes_database.db), detailing mandatory skills, preferred qualifications, and compensation bands; "
        "and (2) An automated real-time live synchronization client (src/live_job_fetcher.py) connecting to the Remotive REST API. Live job postings "
        "are dynamically stripped of web markup, parsed on ingestion using the 1,000+ skill taxonomy engine, and batch-upserted into SQLite "
        "with direct company application URLs."
    )

    add_h2("4.4 Curated Learning Resources Catalog (learning_resources.json)")
    add_body(
        "A structured database mapping technical competencies to curated educational roadmaps, specifying instructional platforms "
        "(Coursera, DeepLearning.AI, Docker Docs, Microsoft Learn), course titles, difficulty levels, estimated completion hours, and key syllabus topics."
    )

    # =============================================================
    # 5. METHODOLOGY
    # =============================================================
    add_h1("5. Methodology")
    add_body(
        "The end-to-end processing pipeline executes through five modular phases: Document Ingestion, NLP Preprocessing, Skill Extraction, "
        "Supervised ML Role Prediction, and Hybrid Compatibility & Skill-Gap Analysis."
    )

    add_h2("5.1 Mathematical Formulations & Feature Extraction")
    add_body(
        "1. TF-IDF Feature Representation: Resume texts are transformed into unigram and bigram numerical vectors using Term Frequency-Inverse "
        "Document Frequency (TF-IDF) with sublinear term-frequency scaling and a maximum feature vocabulary of 3,000 dimensions:"
    )
    add_bullet(" TF-IDF(t, d, D) = TF(t, d) × log((1 + |D|) / (1 + DF(t, D))) + 1", "TF-IDF Weighting: ")
    add_body(
        "2. Dense Semantic Sentence Embeddings: To overcome lexical mismatch, the pipeline utilizes the sentence-transformers all-MiniLM-L6-v2 "
        "model, producing 384-dimensional dense semantic vectors. Cosine similarity between candidate embedding vector u and job embedding vector v is computed as:"
    )
    add_bullet(" Cosine Similarity(u, v) = (u · v) / (||u|| × ||v||)", "Dense Semantic Fit: ")
    add_body(
        "3. Explainable 3-Factor Composite Compatibility Engine: To evaluate candidate alignment against job descriptions, the system computes a "
        "balanced composite compatibility index:"
    )
    add_bullet(" Overall Score = (0.45 × Core Skill Match) + (0.35 × Semantic Sentence-BERT) + (0.20 × TF-IDF Cosine)", "Composite Compatibility Formula: ")
    add_body(
        "The 45% weight on core skill overlap guarantees that non-negotiable hard prerequisites (e.g., Python, Docker) are strictly honored; "
        "the 35% weight on Sentence-BERT captures semantic and contextual experience; and the 20% weight on TF-IDF cosine similarity validates "
        "overall terminology and domain vocabulary overlap."
    )

    # =============================================================
    # 6. IMPLEMENTATION DETAILS
    # =============================================================
    add_h1("6. Implementation Details")
    add_body("The project is developed using the following software and architectural components:")

    # Tech Stack Table
    t_tech = doc.add_table(rows=8, cols=3)
    t_tech.alignment = WD_TABLE_ALIGNMENT.CENTER
    tech_headers = ["Subsystem Layer", "Technology / Framework", "Functional Role in Project"]
    tech_data = [
        ["Language & Runtime", "Python 3.11", "Core execution environment for backend, ML, and frontend modules"],
        ["Document Parsing", "PyMuPDF (fitz) & python-docx", "High-performance digital text extraction from PDF, DOCX, TXT files"],
        ["Text Mining & NLP", "Regex (re) & NLTK", "Taxonomy skill extraction, tokenization, and ATS heuristic scoring"],
        ["Machine Learning Suite", "Scikit-Learn & XGBoost", "TF-IDF vectorizer + SVM, Random Forest, Logistic Regression, XGBoost"],
        ["Semantic Embeddings", "sentence-transformers (all-MiniLM-L6-v2)", "384-dimensional dense contextual sentence representations"],
        ["Database Layer", "SQLite (resumes_database.db)", "Persistent relational storage for jobs, history, and profiles"],
        ["Frontend & Visuals", "Streamlit & Plotly", "Interactive multi-tab dashboard with gauges, radar charts, and tables"]
    ]
    for c_idx, h in enumerate(tech_headers):
        cell = t_tech.cell(0, c_idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row in enumerate(tech_data):
        for c_idx, val in enumerate(row):
            cell = t_tech.cell(r_idx + 1, c_idx)
            set_cell_background(cell, "F8FAFC" if r_idx % 2 == 0 else "FFFFFF")
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if c_idx == 0:
                r.bold = True
            r.font.color.rgb = c_dark

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_h2("6.1 User Interface & Functional Modules")
    add_body(
        "The application is accessible as an interactive web dashboard running on Streamlit (localhost:8501). "
        "Below are the primary operational modules demonstrated during the project evaluation:"
    )

    add_h3("Tab 1: Candidate Overview & ATS Health Check")
    add_body(
        "Upon uploading a candidate resume (e.g., Rohan Kulkarni, DevOps & Cloud Engineer), the system parses candidate coordinates, "
        "identifies 28 technical competencies across Cloud & DevOps, and evaluates the resume against standard ATS criteria. An ATS health score "
        "gauge (84%) is rendered alongside a quantitative breakdown across Action Verbs Impact (70%), Section Completeness (100%), Measurable Metrics (60%), "
        "and Skill Keyword Density (100%)."
    )
    add_figure(
        "fig1_ats_health_check.png",
        1,
        "Candidate Overview and ATS Health Check (Tab 1)",
        "Demonstrates automatic parsing of candidate coordinates, 28 extracted competencies, an 84% ATS health score gauge, and individual quality factor metrics."
    )

    add_h3("Tab 2: Machine Learning Role Prediction")
    add_body(
        "Tab 2 provides multi-class career role inference using the trained models. For the sample DevOps resume, Support Vector Machine "
        "predicts 'DevOps Engineer' as the Primary Career Fit with 59.2% calibrated confidence, followed by 'Cloud Solutions Architect' at 38.5% "
        "and 'Frontend Developer' at 0.5%. The prediction card outlines key extracted competencies driving the classification."
    )
    add_figure(
        "fig2_role_prediction.png",
        2,
        "Machine Learning Role Prediction and Confidence Distribution (Tab 2)",
        "Displays the primary career classification card (DevOps Engineer at 59.2% confidence via SVM) and the top-k confidence distribution chart."
    )

    add_h3("Tab 3: Job Compatibility & Skill-Gap Analysis")
    add_body(
        "Tab 3 allows candidates or recruiters to select a target position from the SQLite database or input custom requirements. "
        "Evaluating Rohan Kulkarni against 'DevOps & Cloud Engineer @ ScaleMatrix Infrastructure', the system outputs an overall 66% Compatibility Score "
        "('Strong Match') and provides complete mathematical explainability via the 3-Factor Decomposition: Core Skill Match (81.0%), "
        "Semantic Sentence Similarity (73.0%), and TF-IDF Keyword Similarity (20.0%)."
    )
    add_figure(
        "fig4_job_compatibility.png",
        3,
        "Explainable 3-Factor Compatibility Decomposition and Score Gauge (Tab 3)",
        "Illustrates the 66% Strong Match gauge and the exact percentage breakdown across Core Skills (81.0%), Semantic Similarity (73.0%), and TF-IDF (20.0%)."
    )

    # =============================================================
    # 7. RESULTS AND DISCUSSION: NOVELTIES AND LIMITATIONS
    # =============================================================
    add_h1("7. Results and Discussion: Novelties and Limitations")

    add_h2("7.1 Multi-Model Benchmark Comparison & Empirical Results")
    add_body(
        "All four machine learning models were trained on 700 balanced profiles across 10 career tracks and evaluated on an independent test partition "
        "of 175 samples. The evaluation measured Accuracy, Weighted Precision, Recall, and Weighted F1-Score:"
    )

    # Benchmark Table
    t_bench = doc.add_table(rows=5, cols=5)
    t_bench.alignment = WD_TABLE_ALIGNMENT.CENTER
    bench_headers = ["Classification Model", "Accuracy (%)", "Precision (%)", "Recall (%)", "F1-Score (%)"]
    bench_data = [
        ["Support Vector Machine (LinearSVC) 🏆", "90.86%", "92.03%", "90.86%", "90.83%"],
        ["Random Forest Classifier", "85.14%", "86.54%", "85.14%", "85.03%"],
        ["Logistic Regression", "84.57%", "85.93%", "84.57%", "84.55%"],
        ["XGBoost (Boosted Trees)", "83.43%", "84.37%", "83.43%", "83.43%"]
    ]
    for c_idx, h in enumerate(bench_headers):
        cell = t_bench.cell(0, c_idx)
        set_cell_background(cell, "1E3A8A")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h)
        r.bold = True
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, row in enumerate(bench_data):
        for c_idx, val in enumerate(row):
            cell = t_bench.cell(r_idx + 1, c_idx)
            set_cell_background(cell, "ECFDF5" if r_idx == 0 else ("F8FAFC" if r_idx % 2 == 1 else "FFFFFF"))
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(val)
            r.font.size = Pt(8.5)
            if r_idx == 0:
                r.bold = True
            r.font.color.rgb = c_dark

    doc.add_paragraph().paragraph_format.space_after = Pt(8)

    add_figure(
        "fig3_model_benchmark.png",
        4,
        "Classification Performance Benchmark and Comparative Bar Chart",
        "Visualizes empirical performance across all four ML models on the independent test set, highlighting SVM's peak accuracy (90.86%) and F1-score (90.83%)."
    )

    add_h3("Analytical Discussion: Why Support Vector Machine Outperformed")
    add_body(
        "Support Vector Machine (LinearSVC) demonstrated the highest overall performance across all four metrics. "
        "In natural language processing, TF-IDF vectorization produces a high-dimensional (3,000 features) and sparse vector space. "
        "Linear SVMs are mathematically designed to find optimal hyperplanes with maximum geometric margins in such spaces, showing superior "
        "generalization and resistance to overfitting. In contrast, decision-tree ensembles (Random Forest and XGBoost) partition feature spaces "
        "using axis-aligned orthogonal splits, which require deeper tree architectures and larger sample sizes to approximate continuous linear decision "
        "boundaries across sparse text features."
    )

    add_h2("7.2 Novelties of the Project")
    add_bullet(" Unlike opaque commercial ATS systems, the platform provides complete mathematical transparency: users see the exact contribution of Core Skills (45%), Dense Embeddings (35%), and Lexical TF-IDF (20%).", "1. Explainable Hybrid Matching Architecture:")
    add_bullet(" Synthetic resumes were rigorously engineered without role titles in feature text, ensuring that classifiers learn genuine competency patterns rather than memorizing labels.", "2. Elimination of Target Label Leakage:")
    add_bullet(" Replaces generic rejection notifications with constructive upskilling roadmaps linked to recognized course platforms with estimated study hours.", "3. Actionable Career Feedback Loop:")
    add_bullet(" Accommodates job applicants (ATS health scoring and diagnostic guidance) and corporate HR recruiters (multi-candidate batch screening leaderboards).", "4. Dual Stakeholder Utility:")
    add_bullet(" Integrates a dynamic REST API client that fetches real-world tech vacancies from Remotive, automatically strips HTML markup, extracts competencies on ingestion, and stores them in SQLite with direct application links.", "5. Real-Time Job Ingestion & Market Sync:")

    add_h2("7.3 Limitations of the Current System")
    add_bullet(" Sentence-Transformers process up to 512 sequence tokens (~1,500 characters); very lengthy multi-page resume appendices may not be fully embedded in dense semantic vectors.", "1. Fixed Context Window for Semantic Vectors:")
    add_bullet(" The text extraction pipeline assumes digital text layers in PDFs. Scanned image resumes without embedded text require external Optical Character Recognition (OCR).", "2. Scanned Image PDF Dependency:")
    add_bullet(" While job vacancies can be synced live via REST APIs, the educational roadmap catalog is currently maintained locally in SQLite rather than dynamically queried via course provider APIs.", "3. Offline Educational Catalog:")

    # =============================================================
    # 8. CONCLUSION AND FUTURE SCOPE
    # =============================================================
    add_h1("8. Conclusion and Future Scope")
    add_h2("8.1 Conclusion")
    add_body(
        "This project successfully designed, implemented, and benchmarked an end-to-end AI-Powered Resume Analysis and Job Recommendation System. "
        "By synthesizing NLP text mining, supervised machine learning classification, and dense contextual sentence embeddings, the system resolves "
        "the core shortcomings of traditional recruitment screening. Empirical benchmarks confirm that Support Vector Machine delivers superior role "
        "classification with 90.86% accuracy and a 90.83% weighted F1-score. The 3-factor hybrid matching engine delivers explainable compatibility scores, "
        "and the personalized skill-gap roadmaps transform resume screening from a punitive rejection barrier into an empowering career development platform."
    )

    add_h2("8.2 Future Scope")
    add_body("Future enhancements planned for the system include:")
    add_bullet(" Integrating Tesseract OCR or EasyOCR to extract and structure text from scanned image resumes and multi-column visual portfolios.", "1. Optical Character Recognition (OCR) Integration:")
    add_bullet(" Fine-tuning domain-specific Large Language Models (LLMs) (e.g., LLaMA or Mistral) for contextual sentence rewriting and automated resume improvement.", "2. Domain-Specific LLM Fine-Tuning:")
    add_bullet(" Expanding NLP preprocessing and taxonomy dictionaries to support multi-lingual resume screening across German, French, Spanish, and regional Indian languages.", "3. Multilingual Resume Processing:")
    add_bullet(" Building direct web scrapers and API integrations with Coursera, Udemy, and edX to fetch real-time course pricing, ratings, and active enrollment links.", "4. Dynamic Automated Course API Ingestion:")

    # =============================================================
    # 9. REFERENCES
    # =============================================================
    add_h1("9. References")
    refs = [
        "Devlin, J., Chang, M. W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT), pp. 4171-4186.",
        "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP), pp. 3982-3992.",
        "Cortes, C., & Vapnik, V. (1995). Support-Vector Networks. Machine Learning, 20(3), pp. 273-297.",
        "Breiman, L. (2001). Random Forests. Machine Learning, 45(1), pp. 5-32.",
        "Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining, pp. 785-794.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, pp. 2825-2830.",
        "Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval. Cambridge University Press.",
        "Streamlit Inc. (2024). Streamlit: The fastest way to build and share data apps. Streamlit Open Source Documentation. https://docs.streamlit.io",
        "Remotive Inc. (2026). Remotive Remote Jobs Public API Documentation. https://remotive.com/api/remote-jobs"
    ]
    for r in refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        p_ref.paragraph_format.left_indent = Inches(0.5)
        p_ref.paragraph_format.first_line_indent = Inches(-0.5)
        run = p_ref.add_run(r)
        run.font.size = Pt(9.5)
        run.font.color.rgb = c_dark

    doc.save(output_docx_path)
    print(f"Report DOCX successfully created with embedded figures at: {output_docx_path}")

if __name__ == "__main__":
    out_docx = r"C:\Users\tejas\.gemini\antigravity\scratch\ai-resume-analyzer\PROJECT_REPORT.docx"
    create_report(out_docx)
