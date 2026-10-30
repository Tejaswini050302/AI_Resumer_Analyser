import os
import json
import re
from typing import Dict, List, Set, Any, Tuple


class SkillExtractor:
    """
    Extracts skills using a curated skill taxonomy and advanced regex boundary matching.
    Avoids false positives for short acronyms and handles canonical aliases.
    """

    ALIASES = {
        "k8s": "kubernetes",
        "sklearn": "scikit-learn",
        "js": "javascript",
        "ts": "typescript",
        "reactjs": "react",
        "react.js": "react",
        "nodejs": "node.js",
        "node": "node.js",
        "postgres": "postgresql",
        "py": "python",
        "nlp": "natural language processing",
        "cv": "computer vision",
        "dl": "deep learning",
        "ml": "machine learning",
        "ai": "artificial intelligence",
        "gcp": "google cloud platform",
        "aws": "amazon web services",
        "pbi": "power bi",
        "tf": "tensorflow",
        "llms": "large language models",
        "llm": "large language models",
        "genai": "generative ai",
    }

    # Short skills that require strict isolated word matching
    SHORT_SKILLS = {"c", "r", "go", "ci", "cd", "bi", "qa", "ui", "ux"}

    def __init__(self, taxonomy_path: str = None):
        if taxonomy_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            taxonomy_path = os.path.join(base_dir, "data", "skills_dataset.json")

        self.taxonomy_path = taxonomy_path
        self.categories: Dict[str, List[str]] = {}
        self.skill_to_category: Dict[str, str] = {}
        self.all_skills: Set[str] = set()
        self._load_taxonomy()

    def _load_taxonomy(self):
        """Load skills dataset from JSON."""
        if os.path.exists(self.taxonomy_path):
            with open(self.taxonomy_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.categories = data.get("categories", {})
        else:
            self.categories = {}

        # Invert category map and populate skill set
        for category, skills in self.categories.items():
            for s in skills:
                s_norm = s.strip().lower()
                self.all_skills.add(s_norm)
                self.skill_to_category[s_norm] = category

    def extract_skills(self, text: str) -> Dict[str, Any]:
        """
        Extract categorized skills, matched tokens, and stats from text.
        """
        text_lower = text.lower()
        extracted: Set[str] = set()

        # 1. First pass: Multi-word skill phrases (2, 3, 4 words)
        multi_word_skills = [s for s in self.all_skills if " " in s or "-" in s or "." in s]
        for skill in multi_word_skills:
            # Escape regex symbols
            pattern = r"(?:\b|_)" + re.escape(skill) + r"(?:\b|_)"
            if re.search(pattern, text_lower):
                extracted.add(skill)

        # 2. Second pass: Single-word skills & aliases
        # Tokenize by punctuation/space
        raw_tokens = set(re.findall(r"\b[a-z0-9+#.-]+\b", text_lower))

        for tok in raw_tokens:
            canonical = self.ALIASES.get(tok, tok)
            
            if canonical in self.all_skills:
                # Extra caution for 1-2 letter words
                if canonical in self.SHORT_SKILLS:
                    # Match exact standalone word with boundaries
                    pattern = rf"(?<=[\s,;:(]){re.escape(tok)}(?=[\s,;:).!?])"
                    if re.search(pattern, f" {text_lower} "):
                        extracted.add(canonical)
                else:
                    extracted.add(canonical)

        # 3. Categorize extracted skills
        categorized: Dict[str, List[str]] = {cat: [] for cat in self.categories.keys()}
        other_skills = []

        for skill in sorted(extracted):
            cat = self.skill_to_category.get(skill)
            if cat and cat in categorized:
                categorized[cat].append(skill)
            else:
                other_skills.append(skill)

        # Remove empty categories
        categorized = {k: v for k, v in categorized.items() if v}

        # Determine dominant skill category
        top_category = None
        max_count = 0
        for cat, skills in categorized.items():
            if cat != "Soft Skills" and len(skills) > max_count:
                max_count = len(skills)
                top_category = cat

        return {
            "all_extracted_skills": sorted(list(extracted)),
            "skills_by_category": categorized,
            "total_skills_count": len(extracted),
            "dominant_domain": top_category or "General Technology",
            "skill_density": len(extracted)
        }
