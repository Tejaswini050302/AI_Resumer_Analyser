import os
import re
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable, Image as RLImage
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))
        
        # Header (on pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "AI-Powered Resume Analysis & Job Recommendation System | Machine Learning (CSE_3148)")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 744, letter[0] - 54, 744)
        
        # Footer
        footer_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(letter[0] - 54, 36, footer_text)
        self.drawString(54, 36, "Guide: Shreya Banerjee  •  Tejaswini Singh (245805418) & Shriya Shet (245805454)")
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 48, letter[0] - 54, 48)
        
        self.restoreState()


def build_pdf_report(output_pdf_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    screenshots_dir = os.path.join(base_dir, "docs", "screenshots")

    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0D9488"),
        spaceAfter=6
    )

    h1_style = ParagraphStyle(
        'SecH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=12.5,
        leading=16,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=5,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SecH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#0D9488"),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SecH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=8,
        spaceAfter=3,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'ReportBody',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=8.8,
        leading=13,
        textColor=colors.HexColor("#1E293B"),
        spaceAfter=5
    )

    bullet_style = ParagraphStyle(
        'ReportBullet',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    caption_style = ParagraphStyle(
        'FigureCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#64748B"),
        alignment=1, # Center
        spaceBefore=4,
        spaceAfter=10
    )

    meta_style = ParagraphStyle(
        'MetaText',
        parent=body_style,
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        fontName='Helvetica',
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#1E293B"),
        alignment=0
    )

    table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=table_cell_style,
        alignment=1
    )

    elements = []

    # Title block
    elements.append(Paragraph("ACADEMIC MINI PROJECT REPORT | MACHINE LEARNING (CSE_3148)", subtitle_style))
    elements.append(Paragraph("AI-Powered Resume Analysis and Job Recommendation System", title_style))
    elements.append(Paragraph("Semantic Parsing, Multi-Class ML Role Prediction, Explainable Hybrid Matching & Live Job Synchronization", subtitle_style))
    elements.append(Spacer(1, 2))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=8))

    # Meta card / metadata table
    meta_info = [
        [Paragraph("<b>Course Code & Title:</b> Machine Learning (CSE_3148)", meta_style),
         Paragraph("<b>Due Date of Submission:</b> 30th October 2026", meta_style)],
        [Paragraph("<b>Faculty Guide:</b> Shreya Banerjee", meta_style),
         Paragraph("<b>Architecture:</b> Streamlit + NLP + Scikit-Learn + SQLite", meta_style)],
    ]
    t_meta = Table(meta_info, colWidths=[250, 254])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F1F5F9")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 6))

    # Team Members Table
    team_data = [
        [Paragraph("S. No.", table_header_style), Paragraph("Student Name", table_header_style), Paragraph("Registration Number", table_header_style)],
        [Paragraph("1.", table_cell_center), Paragraph("<b>Tejaswini Singh</b>", table_cell_style), Paragraph("<b>245805418</b>", table_cell_center)],
        [Paragraph("2.", table_cell_center), Paragraph("<b>Shriya Shet</b>", table_cell_style), Paragraph("<b>245805454</b>", table_cell_center)],
    ]
    t_team = Table(team_data, colWidths=[44, 280, 180])
    t_team.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    elements.append(t_team)
    elements.append(Spacer(1, 8))

    # Helper for adding figures
    def add_fig_element(filename, fig_num, title, caption):
        p_img = os.path.join(screenshots_dir, filename)
        if os.path.exists(p_img):
            elements.append(Spacer(1, 4))
            img_obj = RLImage(p_img, width=460, height=265)
            elements.append(KeepTogether([
                img_obj,
                Paragraph(f"<b>Figure {fig_num}: {title}.</b> <i>{caption}</i>", caption_style)
            ]))
            elements.append(Spacer(1, 4))

    # 1. Abstract
    elements.append(Paragraph("1. Abstract", h1_style))
    elements.append(Paragraph(
        "In modern talent acquisition, recruitment teams face overwhelming application volumes, receiving hundreds of resumes for every "
        "advertised vacancy. Manual document screening is slow, resource-intensive, and inherently prone to unconscious human bias and cognitive fatigue, "
        "with studies indicating that recruiters spend merely 6 to 8 seconds scanning an individual resume. Concurrently, legacy Applicant Tracking "
        "Systems (ATS) depend on rigid, exact keyword matching; candidates who express identical competencies using industry synonyms (such as 'K8s' "
        "versus 'Kubernetes' or 'container orchestration' versus 'Docker') are routinely rejected. Furthermore, conventional job portals function "
        "strictly as one-way rejection funnels, offering applicants zero constructive feedback regarding missing qualifications.", body_style
    ))
    elements.append(Paragraph(
        "To resolve these structural bottlenecks, this project presents an integrated <b>AI-Powered Resume Analysis and Job Recommendation System</b>. "
        "The system parses multi-format resumes (PDF, DOCX, TXT) using PyMuPDF and python-docx, extracts contact information, and computes an automated "
        "5-factor ATS quality score. Competencies are extracted using a 1,000+ skill taxonomy covering 11 technical domains with boundary-aware alias resolution. "
        "A multi-class machine learning classification engine benchmarks four models—<b>Support Vector Machine (LinearSVC), Random Forest, Logistic Regression, "
        "and XGBoost</b>—trained on 700 balanced candidate profiles without target label leakage. Empirical evaluations confirm that Support Vector Machine "
        "achieves superior performance with <b>90.86% accuracy</b> and a <b>90.83% weighted F1-score</b>. Alignment is computed via an explainable 3-factor "
        "hybrid matching engine combining core skill overlap (45%), dense contextual embeddings via Sentence-Transformers (35%), and lexical TF-IDF cosine "
        "similarity (20%). A granular Skill-Gap Matrix pinpoints deficits and suggests curated learning roadmaps. Finally, a real-time REST API synchronization "
        "client connects to public job feeds (Remotive) to ingest live vacancies directly into an embedded SQLite database.", body_style
    ))

    # 2. Introduction
    elements.append(Paragraph("2. Introduction", h1_style))
    elements.append(Paragraph(
        "The digital recruitment ecosystem has expanded rapidly with the rise of online job boards and remote employment. While these tools have expanded "
        "career accessibility, they have created an unprecedented screening dilemma. Traditional screening approaches fall into two problematic extremes:", body_style
    ))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Manual Screening Fatigue:</b> Recruiters scan resumes in 6 to 8 seconds, introducing subjective cognitive bias.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Brittle Keyword Matching:</b> Legacy ATS engines rely on exact string equality, rejecting qualified candidates using synonyms.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>The Guidance Void:</b> Rejection emails provide no diagnostic feedback or actionable upskilling pathways.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Static Disconnect:</b> Traditional prototypes rely on static CSV dumps disconnected from active market hiring.", bullet_style))

    # 3. Objective
    elements.append(Paragraph("3. Objective", h1_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>1. Document Parsing & ATS Audit:</b> Multi-format ingestion and 5-factor ATS scoring (word count, sections, contacts, density, action verbs).", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>2. Domain Skill Extraction:</b> Boundary-aware regex extraction against a 1,000+ skill taxonomy across 11 technical tracks.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>3. Supervised ML Classification:</b> Multi-class role prediction across 10 career tracks benchmarking SVM, RF, LR, and XGBoost.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>4. Explainable Hybrid Matching:</b> Synergizing core skill overlap (45%), dense Sentence-BERT vectors (35%), and TF-IDF cosine (20%).", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>5. Granular Skill-Gap Matrix:</b> Deconstructing requirements into verified mandatory, missing, and bonus skills with severity indexing.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>6. Personalized Upskilling:</b> Mapping skill deficits to curated course roadmaps with estimated hours.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>7. Real-Time Job Ingestion:</b> Connecting to Remotive public REST API to batch-upsert live openings into SQLite.", bullet_style))

    # 4. Data Source
    elements.append(Paragraph("4. Data Source", h1_style))
    elements.append(Paragraph("<b>4.1 Curated Skills Taxonomy:</b> 1,000+ skills categorized into 11 domains with regex boundary alias resolution.", body_style))
    elements.append(Paragraph("<b>4.2 Balanced Resume Corpus:</b> 700 balanced candidate profiles across 10 career tracks (70 per track). Explicitly engineered without role titles in feature text to eliminate target label leakage.", body_style))
    elements.append(Paragraph("<b>4.3 Reference Job Descriptions & Real-Time Feed:</b> SQLite repository (resumes_database.db) holding 10 reference vacancies + live synced Remotive API postings.", body_style))
    elements.append(Paragraph("<b>4.4 Curated Learning Resources Catalog:</b> Structured catalog mapping skills to Coursera, DeepLearning.AI, and documentation modules.", body_style))

    # 5. Methodology
    elements.append(Paragraph("5. Methodology", h1_style))
    elements.append(Paragraph(
        "<b>Feature Representation & Formulations:</b><br/>"
        "• <i>TF-IDF Vectorization:</i> Extracts unigram/bigram numerical vectors (3,000 features max).<br/>"
        "• <i>Dense Semantic Embeddings:</i> Utilizes Sentence-Transformers (all-MiniLM-L6-v2) for 384-dimensional dense semantic vectors.<br/>"
        "• <i>Explainable 3-Factor Formula:</i> Overall Score = (0.45 × Core Skill Match) + (0.35 × Semantic Sentence-BERT) + (0.20 × TF-IDF Cosine).", body_style
    ))

    # 6. Implementation Details
    elements.append(Paragraph("6. Implementation Details", h1_style))
    
    # Tech Table
    tech_data = [
        [Paragraph("Subsystem Layer", table_header_style), Paragraph("Technology / Framework", table_header_style), Paragraph("Functional Role", table_header_style)],
        [Paragraph("Runtime", table_cell_style), Paragraph("Python 3.11", table_cell_style), Paragraph("Core backend & ML execution environment", table_cell_style)],
        [Paragraph("Parsing", table_cell_style), Paragraph("PyMuPDF & python-docx", table_cell_style), Paragraph("Digital text extraction from PDF, DOCX, TXT", table_cell_style)],
        [Paragraph("ML Suite", table_cell_style), Paragraph("Scikit-Learn & XGBoost", table_cell_style), Paragraph("TF-IDF vectorizer + SVM, RF, LR, XGBoost", table_cell_style)],
        [Paragraph("Embeddings", table_cell_style), Paragraph("sentence-transformers", table_cell_style), Paragraph("384-dimensional dense contextual sentence vectors", table_cell_style)],
        [Paragraph("Database", table_cell_style), Paragraph("SQLite (resumes_database.db)", table_cell_style), Paragraph("Persistent relational storage for jobs & analysis", table_cell_style)],
        [Paragraph("Frontend", table_cell_style), Paragraph("Streamlit & Plotly", table_cell_style), Paragraph("Interactive multi-tab dashboard with gauges & bars", table_cell_style)],
    ]
    t_tech = Table(tech_data, colWidths=[80, 160, 264])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    elements.append(t_tech)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("<b>6.1 UI Walkthrough and System Verification:</b>", h2_style))
    elements.append(Paragraph(
        "The application provides an interactive web dashboard running on Streamlit (localhost:8501). "
        "During live demonstration, candidate resumes are parsed and evaluated in real-time:", body_style
    ))

    # Figure 1: ATS Health Check
    add_fig_element(
        "fig1_ats_health_check.png",
        1,
        "Candidate Overview and ATS Health Check (Tab 1)",
        "Demonstrates automatic parsing of candidate coordinates (Rohan Kulkarni), 28 extracted competencies, an 84% ATS health score gauge, and individual quality factor metrics."
    )

    # Figure 2: ML Role Prediction
    add_fig_element(
        "fig2_role_prediction.png",
        2,
        "Machine Learning Role Prediction and Confidence Distribution (Tab 2)",
        "Displays the primary career classification card (DevOps Engineer at 59.2% confidence via SVM) and the top-k confidence distribution chart."
    )

    # Figure 3: Job Compatibility
    add_fig_element(
        "fig4_job_compatibility.png",
        3,
        "Explainable 3-Factor Compatibility Decomposition and Score Gauge (Tab 3)",
        "Illustrates the 66% Strong Match gauge and the exact percentage breakdown across Core Skills (81.0%), Semantic Similarity (73.0%), and TF-IDF (20.0%)."
    )

    # 7. Results and Discussion
    elements.append(Paragraph("7. Results and Discussion: Novelties and Limitations", h1_style))
    elements.append(Paragraph("<b>7.1 Multi-Model Benchmark Comparison:</b>", h2_style))

    # Benchmark Table
    bench_data = [
        [Paragraph("Model Algorithm", table_header_style), Paragraph("Accuracy", table_header_style), Paragraph("Precision", table_header_style), Paragraph("Recall", table_header_style), Paragraph("F1-Score", table_header_style)],
        [Paragraph("<b>Support Vector Machine (SVM) 🏆</b>", table_cell_style), Paragraph("<b>90.86%</b>", table_cell_center), Paragraph("<b>92.03%</b>", table_cell_center), Paragraph("<b>90.86%</b>", table_cell_center), Paragraph("<b>90.83%</b>", table_cell_center)],
        [Paragraph("Random Forest Classifier", table_cell_style), Paragraph("85.14%", table_cell_center), Paragraph("86.54%", table_cell_center), Paragraph("85.14%", table_cell_center), Paragraph("85.03%", table_cell_center)],
        [Paragraph("Logistic Regression", table_cell_style), Paragraph("84.57%", table_cell_center), Paragraph("85.93%", table_cell_center), Paragraph("84.57%", table_cell_center), Paragraph("84.55%", table_cell_center)],
        [Paragraph("XGBoost (Boosted Trees)", table_cell_style), Paragraph("83.43%", table_cell_center), Paragraph("84.37%", table_cell_center), Paragraph("83.43%", table_cell_center), Paragraph("83.43%", table_cell_center)],
    ]
    t_bench = Table(bench_data, colWidths=[184, 80, 80, 80, 80])
    t_bench.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('BACKGROUND', (0,1), (-1,1), colors.HexColor("#ECFDF5")),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,2), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    elements.append(t_bench)
    elements.append(Spacer(1, 6))

    # Figure 4: Benchmark Bar Chart
    add_fig_element(
        "fig3_model_benchmark.png",
        4,
        "Classification Performance Benchmark and Comparative Bar Chart",
        "Visualizes empirical performance across all four ML models on the independent test set, highlighting SVM's peak accuracy (90.86%) and F1-score (90.83%)."
    )

    elements.append(Paragraph(
        "<b>Analytical Discussion: Why Support Vector Machine Outperformed:</b><br/>"
        "In natural language processing, TF-IDF vectorization produces a high-dimensional (3,000 features) sparse vector space. "
        "Linear SVMs are mathematically formulated to search for maximum-margin separating hyperplanes in high-dimensional geometries, "
        "exhibiting exceptional generalization and resistance to overfitting. In contrast, decision tree ensembles (Random Forest and XGBoost) "
        "partition feature spaces via orthogonal axis-aligned splits, which struggle to model subtle cross-skill gradients in sparse text.", body_style
    ))

    elements.append(Paragraph("<b>7.2 Novelties of the Project:</b>", h2_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Explainable Hybrid Matching:</b> Full transparency into Core Skill (45%), Sentence-BERT (35%), and TF-IDF (20%) contributions.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Zero Label Leakage:</b> Synthetic corpus engineered without role names in text, guaranteeing authentic generalization.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Actionable Upskilling Feedback:</b> Closes recruitment loop by providing structured learning roadmaps with study hours.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Dual Utility:</b> Serves applicants (diagnostics) and corporate talent acquisition teams (batch screening).", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Real-Time API Sync:</b> Live ingestion client fetching remote tech vacancies from Remotive directly into SQLite.", bullet_style))

    elements.append(Paragraph("<b>7.3 Limitations:</b>", h2_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Context Window:</b> Sentence-Transformers encode up to 512 tokens (~1,500 chars); lengthy appendices may be truncated.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Scanned PDFs:</b> Requires digital text layers; scanned image resumes require external OCR preprocessing.", bullet_style))
    elements.append(Paragraph("&bull;&nbsp;&nbsp;<b>Local Course Catalog:</b> Learning paths are stored locally in SQLite rather than scraped dynamically via live course APIs.", bullet_style))

    # 8. Conclusion and Future Scope
    elements.append(Paragraph("8. Conclusion and Future Scope", h1_style))
    elements.append(Paragraph(
        "This project successfully developed and validated an end-to-end AI-Powered Resume Analysis and Job Recommendation System. "
        "By synthesizing NLP text mining, supervised machine learning classification, and dense contextual sentence embeddings, the system resolves "
        "the core shortcomings of traditional recruitment screening. Empirical benchmarks confirm that Support Vector Machine delivers superior role "
        "classification with 90.86% accuracy and a 90.83% weighted F1-score. Future extensions will incorporate OCR for scanned documents, "
        "domain-specific LLM fine-tuning, and multilingual resume processing.", body_style
    ))

    # 9. References
    elements.append(Paragraph("9. References", h1_style))
    refs = [
        "Devlin, J., et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding. NAACL-HLT, pp. 4171-4186.",
        "Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks. EMNLP, pp. 3982-3992.",
        "Cortes, C., & Vapnik, V. (1995). Support-Vector Networks. Machine Learning, 20(3), pp. 273-297.",
        "Breiman, L. (2001). Random Forests. Machine Learning, 45(1), pp. 5-32.",
        "Chen, T., & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. ACM SIGKDD, pp. 785-794.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine Learning in Python. JMLR, 12, pp. 2825-2830.",
        "Remotive Inc. (2026). Remotive Remote Jobs Public REST API. https://remotive.com/api/remote-jobs"
    ]
    for r in refs:
        elements.append(Paragraph(f"&bull;&nbsp;&nbsp;{r}", bullet_style))

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"Report PDF successfully generated with embedded figures at: {output_pdf_path}")

if __name__ == "__main__":
    out_pdf = r"C:\Users\tejas\.gemini\antigravity\scratch\ai-resume-analyzer\PROJECT_REPORT.pdf"
    build_pdf_report(out_pdf)
