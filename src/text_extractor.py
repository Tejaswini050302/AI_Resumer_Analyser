import os
import re
from typing import Dict, Any, Optional

try:
    import pymupdf as fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    try:
        import fitz
        PYMUPDF_AVAILABLE = True
    except ImportError:
        PYMUPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class TextExtractor:
    """
    Extracts text and structures sections from resumes (PDF, DOCX, TXT).
    """

    # Common section header regex patterns
    SECTION_PATTERNS = {
        "summary": r"(?:summary|professional\s+summary|profile|about\s+me|career\s+objective|objective)",
        "skills": r"(?:skills|technical\s+skills|skills\s+&\s+competencies|core\s+competencies|technologies|tech\s+stack)",
        "experience": r"(?:experience|work\s+experience|professional\s+experience|employment\s+history|internships|work\s+history)",
        "education": r"(?:education|academic\s+background|academic\s+qualifications|educational\s+background|qualifications)",
        "projects": r"(?:projects|key\s+projects|academic\s+projects|personal\s+projects|notable\s+projects)",
        "certifications": r"(?:certifications|certificates|licenses|courses\s+&\s+certifications|achievements|honors)",
    }

    @classmethod
    def extract_from_file(cls, file_path_or_buffer, file_extension: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract raw text, detected sections, and basic metadata from resume file or buffer.
        """
        ext = file_extension
        filename = "uploaded_resume"
        
        if isinstance(file_path_or_buffer, str):
            filename = os.path.basename(file_path_or_buffer)
            ext = os.path.splitext(file_path_or_buffer)[1].lower().strip(".")
            with open(file_path_or_buffer, "rb") as f:
                content_bytes = f.read()
        elif hasattr(file_path_or_buffer, "read"):
            content_bytes = file_path_or_buffer.read()
            if hasattr(file_path_or_buffer, "name"):
                filename = file_path_or_buffer.name
                ext = os.path.splitext(filename)[1].lower().strip(".")
        else:
            raise ValueError("Unsupported input format for resume extraction")

        if not ext:
            ext = "txt"

        raw_text = ""
        page_count = 1

        if ext == "pdf":
            raw_text, page_count = cls._extract_from_pdf(content_bytes)
        elif ext in ["docx", "doc"]:
            raw_text = cls._extract_from_docx(content_bytes)
        else:
            # Plain text fallback
            try:
                raw_text = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                raw_text = content_bytes.decode("latin-1", errors="ignore")

        # Clean text basic whitespace
        cleaned_text = cls._clean_text(raw_text)
        sections = cls._segment_sections(cleaned_text)

        # Basic text stats
        words = re.findall(r"\b\w+\b", cleaned_text)
        word_count = len(words)
        bullet_points = len(re.findall(r"(?:^|\n)\s*[\u2022\u2023\u25E6\u2043\u2219\*\-]\s*", raw_text))

        return {
            "filename": filename,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text,
            "page_count": page_count,
            "word_count": word_count,
            "bullet_points_count": bullet_points,
            "sections": sections,
        }

    @classmethod
    def _extract_from_pdf(cls, content_bytes: bytes) -> tuple[str, int]:
        """Extract text from PDF using PyMuPDF (fitz) with high fidelity."""
        text_parts = []
        page_count = 1
        
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(stream=content_bytes, filetype="pdf")
                page_count = len(doc)
                for page in doc:
                    text_parts.append(page.get_text("text"))
                doc.close()
                return "\n".join(text_parts), page_count
            except Exception as e:
                # In case fitz fails, fallback
                pass

        # Fallback to simple regex/ascii extraction if fitz is unavailable or corrupted
        try:
            ascii_text = content_bytes.decode("latin-1", errors="ignore")
            # Extract printable sequences
            printable = re.findall(r"[\x20-\x7E\n\r\t]+", ascii_text)
            return "\n".join(printable), 1
        except Exception:
            return "", 1

    @classmethod
    def _extract_from_docx(cls, content_bytes: bytes) -> str:
        """Extract text from docx file buffer."""
        import io
        if DOCX_AVAILABLE:
            try:
                doc = docx.Document(io.BytesIO(content_bytes))
                paras = [p.text for p in doc.paragraphs if p.text.strip()]
                for table in doc.tables:
                    for row in table.rows:
                        paras.append(" ".join(cell.text.strip() for cell in row.cells if cell.text.strip()))
                return "\n".join(paras)
            except Exception:
                pass
        return content_bytes.decode("utf-8", errors="ignore")

    @classmethod
    def _clean_text(cls, text: str) -> str:
        """Standardize newlines and strip excessive whitespace."""
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    @classmethod
    def _segment_sections(cls, text: str) -> Dict[str, str]:
        """Segment resume into standard sections using regex patterns."""
        lines = text.split("\n")
        sections = {k: [] for k in cls.SECTION_PATTERNS.keys()}
        current_section = "summary"
        
        # Build master regex for headings
        header_regex_map = {
            sec: re.compile(rf"^\s*(?:[0-9]+\.|\*|-)?\s*{pat}\s*[:\-]?\s*$", re.IGNORECASE)
            for sec, pat in cls.SECTION_PATTERNS.items()
        }

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check if this line is a section heading
            matched_sec = None
            for sec, reg in header_regex_map.items():
                if reg.match(line_str) or (len(line_str.split()) <= 4 and re.search(cls.SECTION_PATTERNS[sec], line_str, re.IGNORECASE) and line_str.isupper()):
                    matched_sec = sec
                    break

            if matched_sec:
                current_section = matched_sec
            else:
                sections[current_section].append(line_str)

        # Flatten sections into strings
        return {k: "\n".join(v).strip() for k, v in sections.items()}
