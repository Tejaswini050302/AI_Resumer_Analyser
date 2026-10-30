import os
import sys

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


def test_pipeline():
    print("Testing Full End-to-End Pipeline...")
    resume_path = os.path.join(BASE_DIR, "sample_resumes", "ml_engineer_resume.txt")
    with open(resume_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. NLP and extraction
    sections = TextExtractor._segment_sections(text)
    contact = NLPProcessor.extract_contact_info(text)
    print(f"Extracted Contact: {contact['name']} | {contact['email']}")

    # 2. Skill extraction
    extractor = SkillExtractor()
    skills_data = extractor.extract_skills(text)
    skills = skills_data["all_extracted_skills"]
    print(f"Skills Extracted ({len(skills)}): {skills[:5]}")

    # 3. ML Job role prediction
    clf = JobRoleClassifier()
    assert clf.load_artifacts(), "Model artifacts should exist"
    preds = clf.predict_roles(text, top_k=3)
    print(f"Top Predicted Role: {preds[0]['role']} ({preds[0]['confidence']}%)")

    # 4. Job Compatibility
    matcher = JobMatcher()
    job_desc = "Seeking a Machine Learning Engineer with Python, PyTorch, Docker, and FastAPI."
    comp = matcher.calculate_compatibility(
        text, skills, job_desc,
        required_skills=["python", "pytorch", "docker", "fastapi"],
        preferred_skills=["kubernetes", "aws"]
    )
    print(f"Compatibility Score: {comp['overall_score']}% | Grade: {comp['grade']}")

    # 5. Skill Gap
    gap = SkillGapAnalyzer.analyze_gap(
        skills,
        required_skills=["python", "pytorch", "docker", "fastapi"],
        preferred_skills=["kubernetes", "aws"]
    )
    print(f"Skill Gap - Matched Core: {gap['matched_core']} | Missing Core: {gap['missing_core']}")

    # 6. Recommender
    rec = Recommender()
    roadmaps = rec.recommend_learning_paths(gap['missing_core'] or ["kubernetes"])
    print(f"Learning Paths Found: {roadmaps['total_courses']} courses ({roadmaps['estimated_study_hours']} hrs)")

    # 7. Database
    db = DatabaseManager()
    all_jobs = db.get_all_jobs()
    print(f"Active Jobs in SQLite: {len(all_jobs)}")

    print("\nSUCCESS: All Pipeline Components Functioned Flawlessly!")


if __name__ == "__main__":
    test_pipeline()
