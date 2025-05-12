import os
import glob
import pdfplumber
from docx import Document
import chardet
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_encoding(file_path):
    """Detect the encoding of a file using chardet."""
    with open(file_path, 'rb') as f:
        raw_data = f.read()
    result = chardet.detect(raw_data)
    return result['encoding'] if result['encoding'] else 'utf-8'

def extract_pdf_text(pdf_file):
    """Extract text from a PDF file."""
    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from {pdf_file}: {str(e)}")
        return ""

def extract_docx_text(docx_file):
    """Extract text from a DOCX file."""
    try:
        doc = Document(docx_file)
        text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from {docx_file}: {str(e)}")
        return ""

def extract_resume_text(resume_file):
    """Extract text from a resume file based on its extension."""
    ext = os.path.splitext(resume_file)[1].lower()
    if ext == '.pdf':
        return extract_pdf_text(resume_file)
    elif ext in ['.docx', '.doc']:
        return extract_docx_text(resume_file)
    else:
        logger.warning(f"Unsupported file format: {resume_file}")
        return ""

def process_resumes(resume_dir="resumes", output_dir="data/resume_text"):
    """Process all resume files in the resume directory and save extracted text."""
    # Get the directory of the script (ChatBot_BE/scripts)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to ChatBot_BE
    base_dir = os.path.dirname(script_dir)
    # Construct absolute paths
    resume_dir = os.path.join(base_dir, resume_dir)  # ChatBot_BE/resumes
    output_dir = os.path.join(base_dir, output_dir)  # ChatBot_BE/data/resume_text

    os.makedirs(output_dir, exist_ok=True)
    resume_files = glob.glob(os.path.join(resume_dir, "*.pdf")) + glob.glob(os.path.join(resume_dir, "*.docx"))

    if not resume_files:
        logger.error(f"No resume files found in {resume_dir}")
        return

    for resume_file in resume_files:
        logger.info(f"Processing {resume_file}")
        text = extract_resume_text(resume_file)
        if text:
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(resume_file))[0]}_resume.txt")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"Text extracted and saved to {output_file}")
        else:
            logger.warning(f"No text extracted from {resume_file}")

if __name__ == "__main__":
    process_resumes()