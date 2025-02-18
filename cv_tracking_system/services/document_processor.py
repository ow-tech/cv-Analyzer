# core/services/document_processor.py
import PyPDF2
import docx
import pytesseract
from PIL import Image
import pdf2image
import re
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF files using PyPDF2 and fallback to OCR if needed"""
    text = ""
    try:
        # Try direct text extraction first
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num in range(len(reader.pages)):
                text += reader.pages[page_num].extract_text() + "\n"
                
        # If extracted text is too little, use OCR
        if len(text.strip()) < 100:  # Arbitrary threshold
            images = pdf2image.convert_from_path(pdf_path)
            for img in images:
                text += pytesseract.image_to_string(img) + "\n"
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {e}")
    return text

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
    
    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")
    
    if file_path.suffix.lower() == '.pdf':
        raw_text = extract_text_from_pdf(file_path)
    elif file_path.suffix.lower() in ['.docx', '.doc']:
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    return preprocess_text(raw_text)