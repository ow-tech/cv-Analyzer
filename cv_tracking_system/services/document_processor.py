import PyPDF2
import docx
import pytesseract
from PIL import Image
import pdf2image
import re
from pathlib import Path
import logging




# Configure logging
logging.basicConfig(level=logging.INFO)

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF files using PyPDF2 and OCR if needed."""
    text = ""
    try:
        # Try direct text extraction first
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                extracted_text = page.extract_text()
                if extracted_text:
                    text += extracted_text + "\n"

        # If text is empty, apply OCR
        if len(text.strip()) < 50:  # Lower threshold for OCR trigger
            logging.info(f"Applying OCR for {pdf_path} due to low extracted text.")
            images = pdf2image.convert_from_path(pdf_path)
            for img in images:
                processed_img = img.convert('L')  # Convert to grayscale
                text += pytesseract.image_to_string(processed_img, lang="eng") + "\n"

    except PyPDF2.errors.PdfReadError as e:
        logging.error(f"PyPDF2 error while reading {pdf_path}: {e}")
    except Exception as e:
        logging.error(f"Error processing PDF {pdf_path}: {e}")

    return text.strip()
def extract_text_from_docx(docx_path):
    """Extract text from Word documents"""
    doc = docx.Document(docx_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

def preprocess_text(text):
    """Clean and preprocess extracted text"""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove special characters but keep relevant punctuation
    text = re.sub(r'[^\w\s.,@:;()/-]', '', text)
    return text


def process_document(file_path):
    """Process a document based on its file extension"""
    file_path = Path(file_path)
    
    if file_path.suffix.lower() == '.pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() in ['.docx', '.doc']:
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    return preprocess_text(raw_text)

