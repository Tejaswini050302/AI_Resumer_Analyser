import re
import numpy as np
from typing import Dict, List, Any, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False


class JobMatcher:
    """
    Computes TF-IDF keyword cosine similarity, deep semantic sentence similarity,
    and structured skill-match overlap to produce an explainable job compatibility score.
    """

    _semantic_model = None

    def __init__(self, use_semantic: bool = True):
        self.use_semantic = use_semantic and SENTENCE_TRANSFORMER_AVAILABLE

    @classmethod
    def get_semantic_model(cls):
        """Lazy load SentenceTransformer model to optimize app startup."""
        if cls._semantic_model is None and SENTENCE_TRANSFORMER_AVAILABLE:
            try:
                # all-MiniLM-L6-v2 is ultra-fast, lightweight (80MB), and high accuracy
                cls._semantic_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception as e:
                print(f"Warning: Could not initialize SentenceTransformer ({e}). Falling back.")
                cls._semantic_model = None
        return cls._semantic_model

    def calculate_tfidf_similarity(self, resume_text: str, job_text: str) -> float:
        """Calculate TF-IDF n-gram cosine similarity between resume and job description."""
        if not resume_text.strip() or not job_text.strip():
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                stop_words='english',
                ngram_range=(1, 2),
                sublinear_tf=True
            )
            tfidf_matrix = vectorizer.fit_transform([resume_text, job_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(np.clip(sim, 0.0, 1.0))
        except Exception:
            return 0.0

    def calculate_semantic_similarity(self, resume_text: str, job_text: str) -> float:
        """Calculate dense semantic embedding similarity using SentenceTransformer."""
        model = self.get_semantic_model()
        if model is None:
            # Fallback to word-overlap / expanded TF-IDF similarity
            return self.calculate_tfidf_similarity(resume_text, job_text)

        try:
            # Truncate to first 1200 characters for focused semantic comparison
            res_snippet = resume_text[:1500]
            job_snippet = job_text[:1500]

            embeddings = model.encode([res_snippet, job_snippet], show_progress_bar=False)
            emb1 = embeddings[0].reshape(1, -1)
            emb2 = embeddings[1].reshape(1, -1)
            sim = cosine_similarity(emb1, emb2)[0][0]
            return float(np.clip(sim, 0.0, 1.0))
        except Exception as e:
            return self.calculate_tfidf_similarity(resume_text, job_text)

    def calculate_compatibility(
        self,
        resume_text: str,
        resume_skills: List[str],
        job_description: str,
        required_skills: List[str],
        preferred_skills: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Produce a comprehensive, explainable compatibility report.
        """
        preferred_skills = preferred_skills or []
        resume_skills_set = set(s.strip().lower() for s in resume_skills)
        req_skills_set = set(s.strip().lower() for s in required_skills)
        pref_skills_set = set(s.strip().lower() for s in preferred_skills)

        # 1. Skill overlap calculations
        matched_required = sorted(list(resume_skills_set.intersection(req_skills_set)))
        missing_required = sorted(list(req_skills_set - resume_skills_set))

        matched_preferred = sorted(list(resume_skills_set.intersection(pref_skills_set)))
        missing_preferred = sorted(list(pref_skills_set - resume_skills_set))

        # Weighted skill score: required skills have 2x weight of preferred
        total_weight = (len(req_skills_set) * 2.0) + (len(pref_skills_set) * 1.0)
        matched_weight = (len(matched_required) * 2.0) + (len(matched_preferred) * 1.0)

        skill_match_ratio = (matched_weight / total_weight) if total_weight > 0 else 0.5
        skill_match_percentage = round(skill_match_ratio * 100, 1)

        # 2. Text similarities
        tfidf_sim = self.calculate_tfidf_similarity(resume_text, job_description)
        semantic_sim = self.calculate_semantic_similarity(resume_text, job_description)

        tfidf_percentage = round(tfidf_sim * 100, 1)
        semantic_percentage = round(semantic_sim * 100, 1)

        # 3. Overall Composite Score (45% Skills + 35% Semantic + 20% TF-IDF)
        overall_score = round(
            (skill_match_percentage * 0.45) +
            (semantic_percentage * 0.35) +
            (tfidf_percentage * 0.20),
            1
        )
        overall_score = float(np.clip(overall_score, 0.0, 100.0))

        # Qualitative Grade & Interpretation
        if overall_score >= 80:
            grade = "Exceptional Match"
            grade_color = "#10B981"  # Emerald Green
            verdict = "Outstanding candidate profile. Meets nearly all core criteria and demonstrates deep contextual relevance."
        elif overall_score >= 65:
            grade = "Strong Match"
            grade_color = "#3B82F6"  # Blue
            verdict = "Very competitive profile with high core skill overlap. A few targeted improvements will make this application top-tier."
        elif overall_score >= 50:
            grade = "Moderate Match"
            grade_color = "#F59E0B"  # Amber
            verdict = "Promising foundational background, but critical skill gaps or experience differences exist for this target role."
        else:
            grade = "Low Match"
            grade_color = "#EF4444"  # Red
            verdict = "Substantial gap in required competencies and domain keywords. Upskilling in mandatory requirements is advised."

        return {
            "overall_score": overall_score,
            "skill_match_score": skill_match_percentage,
            "semantic_score": semantic_percentage,
            "tfidf_score": tfidf_percentage,
            "matched_required_skills": matched_required,
            "missing_required_skills": missing_required,
            "matched_preferred_skills": matched_preferred,
            "missing_preferred_skills": missing_preferred,
            "grade": grade,
            "grade_color": grade_color,
            "verdict": verdict,
            "is_semantic_enabled": SENTENCE_TRANSFORMER_AVAILABLE and (self.get_semantic_model() is not None),
        }
