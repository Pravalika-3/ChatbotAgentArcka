import os
from pdfminer.high_level import extract_text as extract_pdf_text
import docx

class ResumeParser:
    def __init__(self, resume_dir="resumes"):
        self.resume_dir = resume_dir

    def parse_resume(self, filename):
        """Parse a single resume and return extracted text"""
        filepath = os.path.join(self.resume_dir, filename)
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Resume file not found: {filepath}")

        if filename.lower().endswith(".pdf"):
            return self._parse_pdf(filepath)
        elif filename.lower().endswith(".docx"):
            return self._parse_docx(filepath)
        else:
            raise ValueError("Unsupported file format (only PDF and DOCX are supported)")

    def _parse_pdf(self, filepath):
        """Extract text from PDF"""
        try:
            text = extract_pdf_text(filepath)
            return text.strip()
        except Exception as e:
            print(f"Error parsing PDF {filepath}: {str(e)}")
            return ""

    def _parse_docx(self, filepath):
        """Extract text from DOCX"""
        try:
            doc = docx.Document(filepath)
            text = "\n".join([para.text for para in doc.paragraphs])
            return text.strip()
        except Exception as e:
            print(f"Error parsing DOCX {filepath}: {str(e)}")
            return ""

    def parse_resumes(self, filenames):
        """
        Parse only given list of filenames.
        Returns dict {filename: text}.
        """
        parsed_data = {}
        for filename in filenames:
            print(f"Parsing resume: {filename}")
            text = self.parse_resume(filename)
            parsed_data[filename] = text
        return parsed_data
