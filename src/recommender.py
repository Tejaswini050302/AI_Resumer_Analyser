import os
import json
import urllib.parse
from typing import Dict, List, Any, Optional

from src.job_matcher import JobMatcher


class Recommender:
    """
    Generates personalized recommendations:
    1. Content-based job matches ranked by compatibility score.
    2. Targeted learning resources and roadmaps for missing skills.
    3. Actionable resume optimization advice.
    """

    def __init__(self, resources_path: str = None):
        if resources_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            resources_path = os.path.join(base_dir, "data", "learning_resources.json")

        self.resources_path = resources_path
        self.learning_catalog: Dict[str, Any] = {}
        self.job_matcher = JobMatcher()
        self._load_catalog()

    def _load_catalog(self):
        """Load curated learning resources from JSON."""
        if os.path.exists(self.resources_path):
            with open(self.resources_path, "r", encoding="utf-8") as f:
                self.learning_catalog = json.load(f)
        else:
            self.learning_catalog = {}

    def recommend_jobs(
        self,
        resume_text: str,
        resume_skills: List[str],
        jobs_list: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Content-based job recommendations ranked by composite compatibility score.
        """
        ranked_jobs = []

        for job in jobs_list:
            req_skills = job.get("required_skills", [])
            pref_skills = job.get("preferred_skills", [])
            job_desc = job.get("description", "")

            # Combine title + description for matching
            full_job_text = f"{job.get('title', '')}\n{job_desc}\nRequired Skills: {', '.join(req_skills)}"

            comp = self.job_matcher.calculate_compatibility(
                resume_text=resume_text,
                resume_skills=resume_skills,
                job_description=full_job_text,
                required_skills=req_skills,
                preferred_skills=pref_skills
            )

            job_rec = {
                "id": job.get("id"),
                "title": job.get("title"),
                "company": job.get("company"),
                "location": job.get("location"),
                "salary_range": job.get("salary_range"),
                "experience_level": job.get("experience_level"),
                "required_skills": req_skills,
                "preferred_skills": pref_skills,
                "overall_score": comp["overall_score"],
                "skill_match_score": comp["skill_match_score"],
                "semantic_score": comp["semantic_score"],
                "tfidf_score": comp["tfidf_score"],
                "grade": comp["grade"],
                "grade_color": comp["grade_color"],
                "matched_required": comp["matched_required_skills"],
                "missing_required": comp["missing_required_skills"],
                "verdict": comp["verdict"],
                "description": job_desc,
                "source": job.get("source", "system"),
                "url": job.get("url", "")
            }
            ranked_jobs.append(job_rec)

        # Sort descending by overall_score
        ranked_jobs.sort(key=lambda x: x["overall_score"], reverse=True)
        return ranked_jobs[:top_n]

    def recommend_learning_paths(self, missing_skills: List[str]) -> Dict[str, Any]:
        """
        Generate structured learning paths for identified skill gaps.
        """
        courses = []
        total_hours = 0

        for skill in missing_skills:
            skill_lower = skill.strip().lower()
            if skill_lower in self.learning_catalog:
                item = self.learning_catalog[skill_lower]
                courses.append({
                    "skill": skill.title(),
                    "title": item.get("title", f"Mastering {skill.title()}"),
                    "platform": item.get("platform", "Online Course"),
                    "url": item.get("url", f"https://www.google.com/search?q={urllib.parse.quote(skill)}+course"),
                    "difficulty": item.get("difficulty", "Intermediate"),
                    "est_hours": item.get("est_hours", 15),
                    "key_topics": item.get("key_topics", ["Fundamentals", "Hands-on projects", "Best practices"]),
                })
                total_hours += item.get("est_hours", 15)
            else:
                # Dynamic fallback course card
                query = urllib.parse.quote(f"learn {skill} programming course tutorial")
                courses.append({
                    "skill": skill.title(),
                    "title": f"Complete Guide to {skill.title()}",
                    "platform": "Coursera / FreeCodeCamp / Docs",
                    "url": f"https://www.google.com/search?q={query}",
                    "difficulty": "Intermediate",
                    "est_hours": 15,
                    "key_topics": [f"{skill.title()} Core Concepts", "Architecture & Syntax", "Real-world Project Implementation"],
                })
                total_hours += 15

        # Group by difficulty
        grouped_by_difficulty = {
            "Beginner": [c for c in courses if "Beginner" in c["difficulty"]],
            "Intermediate": [c for c in courses if "Intermediate" in c["difficulty"] and "Beginner" not in c["difficulty"]],
            "Advanced": [c for c in courses if "Advanced" in c["difficulty"]]
        }

        return {
            "total_courses": len(courses),
            "estimated_study_hours": total_hours,
            "courses": courses,
            "grouped_roadmap": {k: v for k, v in grouped_by_difficulty.items() if v}
        }
