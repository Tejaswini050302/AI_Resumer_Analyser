from typing import Dict, List, Set, Any


class SkillGapAnalyzer:
    """
    Analyzes discrepancies between candidate's acquired skills and job expectations.
    Categorizes gaps by priority and computes role-readiness indicators.
    """

    @classmethod
    def analyze_gap(
        cls,
        candidate_skills: List[str],
        required_skills: List[str],
        preferred_skills: List[str] = None
    ) -> Dict[str, Any]:
        """
        Compare candidate skills with job requirements to identify concrete gaps.
        """
        preferred_skills = preferred_skills or []
        cand_set = set(s.strip().lower() for s in candidate_skills)
        req_set = set(s.strip().lower() for s in required_skills)
        pref_set = set(s.strip().lower() for s in preferred_skills)

        # Matched and missing
        matched_core = sorted(list(cand_set.intersection(req_set)))
        missing_core = sorted(list(req_set - cand_set))

        matched_bonus = sorted(list(cand_set.intersection(pref_set)))
        missing_bonus = sorted(list(pref_set - cand_set))

        # Additional skills possessed by candidate that are not in the job reqs
        extra_skills = sorted(list(cand_set - req_set - pref_set))

        # Readiness metrics
        total_core = len(req_set)
        core_coverage = round((len(matched_core) / total_core * 100), 1) if total_core > 0 else 100.0

        total_all_reqs = total_core + len(pref_set)
        total_matched = len(matched_core) + len(matched_bonus)
        total_coverage = round((total_matched / total_all_reqs * 100), 1) if total_all_reqs > 0 else 100.0

        # Gap severity classification
        if len(missing_core) == 0:
            severity = "None"
            severity_desc = "Fully qualified for all mandatory requirements."
        elif len(missing_core) <= 2:
            severity = "Low"
            severity_desc = "Minor gap. A few focused tutorials will close this gap quickly."
        elif len(missing_core) <= 4:
            severity = "Moderate"
            severity_desc = "Moderate gap. Upskilling in 3-4 core technologies recommended."
        else:
            severity = "High"
            severity_desc = "Significant skill deficit. Dedicated coursework and projects required before applying."

        return {
            "core_coverage_pct": core_coverage,
            "overall_coverage_pct": total_coverage,
            "matched_core": matched_core,
            "missing_core": missing_core,
            "matched_bonus": matched_bonus,
            "missing_bonus": missing_bonus,
            "extra_skills": extra_skills,
            "total_core_needed": total_core,
            "total_core_matched": len(matched_core),
            "severity": severity,
            "severity_desc": severity_desc,
        }
