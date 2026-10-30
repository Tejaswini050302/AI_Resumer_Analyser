import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional


class DatabaseManager:
    """
    Manages SQLite database for storing jobs, analysis sessions, and candidate profiles.
    """

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "resumes_database.db")

        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Create a connection with row factory enabled."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Initialize tables and seed default jobs if empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    location TEXT,
                    experience_level TEXT,
                    salary_range TEXT,
                    required_skills TEXT,
                    preferred_skills TEXT,
                    description TEXT,
                    source TEXT DEFAULT 'system',
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Ensure columns exist if table was already created
            cursor.execute("PRAGMA table_info(jobs)")
            cols = [col[1] for col in cursor.fetchall()]
            if "source" not in cols:
                cursor.execute("ALTER TABLE jobs ADD COLUMN source TEXT DEFAULT 'system'")
            if "url" not in cols:
                cursor.execute("ALTER TABLE jobs ADD COLUMN url TEXT")

            # Analysis history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    candidate_name TEXT,
                    email TEXT,
                    filename TEXT,
                    predicted_role TEXT,
                    confidence REAL,
                    ats_score INTEGER,
                    skills_extracted TEXT,
                    dominant_domain TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()

        # Seed initial jobs from job_descriptions.json if jobs table is empty
        self._seed_default_jobs()

    def _seed_default_jobs(self):
        """Populate jobs from JSON if table has 0 rows."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM jobs")
            count = cursor.fetchone()[0]

            if count == 0:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                json_path = os.path.join(base_dir, "data", "job_descriptions.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        jobs = json.load(f)
                        for j in jobs:
                            cursor.execute("""
                                INSERT INTO jobs (
                                    id, title, company, location, experience_level,
                                    salary_range, required_skills, preferred_skills, description
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (
                                j["id"],
                                j["title"],
                                j["company"],
                                j.get("location", ""),
                                j.get("experience_level", ""),
                                j.get("salary_range", ""),
                                json.dumps(j.get("required_skills", [])),
                                json.dumps(j.get("preferred_skills", [])),
                                j.get("description", "")
                            ))
                    conn.commit()

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Retrieve all active jobs from the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM jobs ORDER BY title ASC")
            rows = cursor.fetchall()

            jobs = []
            for r in rows:
                keys = r.keys()
                jobs.append({
                    "id": r["id"],
                    "title": r["title"],
                    "company": r["company"],
                    "location": r["location"],
                    "experience_level": r["experience_level"],
                    "salary_range": r["salary_range"],
                    "required_skills": json.loads(r["required_skills"] or "[]"),
                    "preferred_skills": json.loads(r["preferred_skills"] or "[]"),
                    "description": r["description"],
                    "source": r["source"] if "source" in keys else "system",
                    "url": r["url"] if "url" in keys else "",
                })
            return jobs

    def sync_live_jobs(self, jobs_list: List[Dict[str, Any]]) -> int:
        """Batch upsert live active jobs into SQLite."""
        if not jobs_list:
            return 0
        added_count = 0
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for job in jobs_list:
                cursor.execute("""
                    INSERT OR REPLACE INTO jobs (
                        id, title, company, location, experience_level,
                        salary_range, required_skills, preferred_skills, description, source, url
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'live_api', ?)
                """, (
                    job.get("id"),
                    job["title"],
                    job["company"],
                    job.get("location", "Remote"),
                    job.get("experience_level", "Full-time"),
                    job.get("salary_range", "Competitive"),
                    json.dumps(job.get("required_skills", [])),
                    json.dumps(job.get("preferred_skills", [])),
                    job.get("description", ""),
                    job.get("url", "")
                ))
                added_count += 1
            conn.commit()
        return added_count

    def add_job(self, job_dict: Dict[str, Any]) -> bool:
        """Add a new job vacancy."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO jobs (
                    id, title, company, location, experience_level,
                    salary_range, required_skills, preferred_skills, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_dict.get("id", f"job_{datetime.now().strftime('%Y%m%d%H%M%S')}"),
                job_dict["title"],
                job_dict["company"],
                job_dict.get("location", "Remote"),
                job_dict.get("experience_level", "Mid-Level"),
                job_dict.get("salary_range", "Competitive"),
                json.dumps(job_dict.get("required_skills", [])),
                json.dumps(job_dict.get("preferred_skills", [])),
                job_dict.get("description", "")
            ))
            conn.commit()
            return True

    def save_analysis(
        self,
        candidate_name: str,
        email: str,
        filename: str,
        predicted_role: str,
        confidence: float,
        ats_score: int,
        skills_extracted: List[str],
        dominant_domain: str
    ):
        """Save a resume analysis run to history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO analysis_history (
                    candidate_name, email, filename, predicted_role,
                    confidence, ats_score, skills_extracted, dominant_domain
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                candidate_name or "Anonymous Candidate",
                email or "N/A",
                filename or "resume.pdf",
                predicted_role,
                confidence,
                ats_score,
                json.dumps(skills_extracted),
                dominant_domain
            ))
            conn.commit()

    def get_recent_analyses(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieve recent resume analysis history."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM analysis_history ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            rows = cursor.fetchall()
            history = []
            for r in rows:
                history.append({
                    "id": r["id"],
                    "candidate_name": r["candidate_name"],
                    "email": r["email"],
                    "filename": r["filename"],
                    "predicted_role": r["predicted_role"],
                    "confidence": r["confidence"],
                    "ats_score": r["ats_score"],
                    "skills_extracted": json.loads(r["skills_extracted"] or "[]"),
                    "dominant_domain": r["dominant_domain"],
                    "created_at": r["created_at"],
                })
            return history
