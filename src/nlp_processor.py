import re
from typing import Dict, List, Any, Optional

try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    
    try:
        STOPWORDS = set(stopwords.words('english'))
    except Exception:
        STOPWORDS = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
            'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it',
            'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
            'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
            'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
            'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
            'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
            'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there'
        }
        
    try:
        LEMMATIZER = WordNetLemmatizer()
    except Exception:
        LEMMATIZER = None
        
    NLTK_AVAILABLE = True
except Exception:
    NLTK_AVAILABLE = False
    STOPWORDS = {
        'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', "you're",
        'he', 'him', 'his', 'himself', 'she', "she's", 'her', 'hers', 'herself', 'it',
        'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which',
        'who', 'whom', 'this', 'that', "that'll", 'these', 'those', 'am', 'is', 'are', 'was',
        'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did',
        'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while',
        'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through',
        'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out',
        'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there'
    }
    LEMMATIZER = None


class NLPProcessor:
    """
    Handles text cleaning, tokenization, entity detection (contact details),
    and resume quality heuristics (action verbs, quantifiable metrics).
    """

    ACTION_VERBS = {
        "developed", "designed", "implemented", "engineered", "created", "built",
        "architected", "optimized", "spearheaded", "orchestrated", "deployed",
        "formulated", "maintained", "analyzed", "reduced", "increased", "boosted",
        "automated", "streamlined", "delivered", "mentored", "collaborated",
        "refactored", "integrated", "transformed", "led", "managed", "scaled"
    }

    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b")
    PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
    LINKEDIN_PATTERN = re.compile(r"linkedin\.com/in/([A-Za-z0-9_-]+)", re.IGNORECASE)
    GITHUB_PATTERN = re.compile(r"github\.com/([A-Za-z0-9_-]+)", re.IGNORECASE)
    URL_PATTERN = re.compile(r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b[-a-zA-Z0-9()@:%_\+.~#?&//=]*")
    METRIC_PATTERN = re.compile(r"(?:\b\d+(?:\.\d+)?%|\$\d+(?:,\d+)*(?:\.\d+)?(?:k|m|b)?|\b\d+\+\s*(?:users|clients|queries|requests|projects|members|engineers|people|times))", re.IGNORECASE)

    @classmethod
    def extract_contact_info(cls, text: str) -> Dict[str, Optional[str]]:
        """Extract email, phone, LinkedIn, GitHub, and portfolio links from text."""
        # Find email
        emails = cls.EMAIL_PATTERN.findall(text)
        email = emails[0] if emails else None

        # Find phone
        phones = cls.PHONE_PATTERN.findall(text)
        phone = phones[0] if phones else None

        # Find LinkedIn
        linkedin_match = cls.LINKEDIN_PATTERN.search(text)
        linkedin = f"https://linkedin.com/in/{linkedin_match.group(1)}" if linkedin_match else None

        # Find GitHub
        github_match = cls.GITHUB_PATTERN.search(text)
        github = f"https://github.com/{github_match.group(1)}" if github_match else None

        # General URLs (excluding linkedin and github)
        all_urls = cls.URL_PATTERN.findall(text)
        portfolio = None
        for u in all_urls:
            if "linkedin.com" not in u.lower() and "github.com" not in u.lower():
                portfolio = u
                break

        # Candidate name heuristic (typically first non-empty line of resume)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        candidate_name = "Candidate"
        if lines:
            first_line = lines[0]
            # Avoid picking "Resume" or "Curriculum Vitae" as name
            if not any(kw in first_line.lower() for kw in ["resume", "curriculum", "cv", "page", "profile"]):
                words = first_line.split()
                if 1 <= len(words) <= 4:
                    candidate_name = first_line

        return {
            "name": candidate_name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "github": github,
            "portfolio": portfolio,
        }

    @classmethod
    def preprocess_text(cls, text: str, remove_stopwords: bool = True, lemmatize: bool = True) -> str:
        """Clean, normalize, tokenize, filter stop words, and lemmatize text."""
        # Lowercase
        text_lower = text.lower()
        # Keep letters, numbers, and basic punctuation for tokens
        tokens = re.findall(r"\b[a-z0-9]+(?:[-_][a-z0-9]+)*\b", text_lower)

        filtered_tokens = []
        for t in tokens:
            if remove_stopwords and t in STOPWORDS:
                continue
            if len(t) <= 1 and not t.isdigit():
                continue
            if lemmatize and LEMMATIZER and NLTK_AVAILABLE:
                try:
                    t = LEMMATIZER.lemmatize(t)
                except Exception:
                    pass
            filtered_tokens.append(t)

        return " ".join(filtered_tokens)

    @classmethod
    def evaluate_resume_quality(cls, text: str, sections: Dict[str, str], skills_count: int) -> Dict[str, Any]:
        """
        Evaluate resume ATS quality based on action verbs, quantifiable metrics,
        section completeness, and word count.
        """
        text_lower = text.lower()
        words = re.findall(r"\b[a-z]+\b", text_lower)
        total_words = len(words)

        # Check action verbs
        matched_verbs = list(cls.ACTION_VERBS.intersection(set(words)))
        action_verb_score = min(100, int((len(matched_verbs) / 10) * 100))

        # Check quantifiable metrics (percentages, dollar amounts, scale numbers)
        metrics_found = cls.METRIC_PATTERN.findall(text)
        quantifiable_score = min(100, len(metrics_found) * 20)

        # Section completeness (Education, Experience, Skills, Projects)
        key_sections = ["skills", "experience", "education", "projects"]
        present_sections = [s for s in key_sections if len(sections.get(s, "").strip()) > 30]
        section_score = int((len(present_sections) / len(key_sections)) * 100)

        # Skill density score
        skill_score = min(100, int((skills_count / 15) * 100))

        # Word count suitability (ideal resume: 350 - 900 words)
        if 350 <= total_words <= 900:
            length_score = 100
        elif 250 <= total_words < 350 or 900 < total_words <= 1200:
            length_score = 80
        else:
            length_score = 50

        # Overall ATS Score (weighted)
        overall_ats_score = int(
            (action_verb_score * 0.20) +
            (quantifiable_score * 0.20) +
            (section_score * 0.30) +
            (skill_score * 0.20) +
            (length_score * 0.10)
        )

        # Recommendations for resume improvements
        recommendations = []
        if len(matched_verbs) < 6:
            recommendations.append("Incorporate more strong action verbs (e.g., 'Architected', 'Spearheaded', 'Optimized', 'Deployed') to describe your experience.")
        if len(metrics_found) < 3:
            recommendations.append("Add quantifiable metrics and measurable outcomes to your bullet points (e.g., 'Improved accuracy by 18%', 'Reduced response latency by 35%').")
        if "projects" not in present_sections:
            recommendations.append("Highlight a dedicated 'Projects' section showing technical implementations and GitHub links.")
        if skills_count < 8:
            recommendations.append("Expand your Technical Skills section to include modern frameworks, databases, and DevOps tools.")
        if total_words < 300:
            recommendations.append("Your resume appears too brief; elaborate more on your project responsibilities and accomplishments.")
        elif total_words > 1000:
            recommendations.append("Your resume exceeds recommended length; consider condensing to 1-2 pages for maximum recruiter readability.")

        return {
            "ats_score": overall_ats_score,
            "action_verb_score": action_verb_score,
            "quantifiable_score": quantifiable_score,
            "section_score": section_score,
            "skill_density_score": skill_score,
            "length_score": length_score,
            "matched_action_verbs": matched_verbs[:10],
            "quantified_achievements": metrics_found[:8],
            "present_sections": present_sections,
            "improvement_tips": recommendations,
        }
