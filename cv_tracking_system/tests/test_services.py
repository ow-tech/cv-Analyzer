import json
from django.test import TestCase
from unittest.mock import patch, MagicMock
from cv_tracking_system.models import Candidate, ChatSession, ChatMessage
from cv_tracking_system.services.query_processor import process_query
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open
import cv_tracking_system.services.document_processor as doc_proc

class ProcessQueryTest(TestCase):
    def setUp(self):
        """Setup initial data for testing"""
        self.session_id = "test-session"
        self.session = ChatSession.objects.create(session_id=self.session_id)
        
        self.candidate1 = Candidate.objects.create(
            name="John Doe",
            email="john@example.com",
            raw_text="Python developer with 5 years experience."
        )
        
        self.candidate2 = Candidate.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            raw_text="Machine Learning Engineer with strong Python skills."
        )

    @patch("cv_tracking_system.services.llm_client.LLMClient")
    def test_process_query_with_valid_filter(self, MockLLMClient):
        """Test processing a query with a valid filter."""
        # Mock LLM response
        mock_llm = MockLLMClient()
        mock_llm.generate_text.side_effect = [
            json.dumps({  # Mock query analysis response
                "intent": "skills",
                "parameters": {"skills": "Python"},
                "is_followup": False,
                "django_filter": "raw_text__icontains='Python'"
            }),
            "Here are Python developers."
        ]

        response = process_query("Find Python developers", self.session_id, mock_llm)
        
        self.assertIn("Python developers", response)
        self.assertTrue(ChatMessage.objects.filter(session=self.session, role="assistant").exists())

    @patch("cv_tracking_system.services.llm_client.LLMClient")
    def test_process_query_no_results(self, MockLLMClient):
        """Test processing a query that returns no candidates."""
        mock_llm = MockLLMClient()
        mock_llm.generate_text.side_effect = [
            json.dumps({
                "intent": "skills",
                "parameters": {"skills": "Java"},
                "is_followup": False,
                "django_filter": "raw_text__icontains='Java'"
            }),
            "No candidates found for Java."
        ]

        response = process_query("Find Java developers", self.session_id, mock_llm)
        
        self.assertIn("No candidates found", response)


    def test_chat_session_creation(self):
        """Ensure chat sessions are created and messages are saved."""
        process_query("Hello", self.session_id)
        session_exists = ChatSession.objects.filter(session_id=self.session_id).exists()
        messages_exist = ChatMessage.objects.filter(session=self.session).exists()
        
        self.assertTrue(session_exists)
        self.assertTrue(messages_exist)




class TestDocumentProcessor(unittest.TestCase):

    @patch("cv_tracking_system.services.document_processor.PyPDF2.PdfReader")
    def test_extract_text_from_pdf(self, mock_pdf_reader):
        """Test PDF text extraction without OCR fallback"""
        mock_pdf_reader.return_value.pages = [MagicMock()]
        mock_pdf_reader.return_value.pages[0].extract_text.return_value = "Extracted PDF text."

        text = doc_proc.extract_text_from_pdf("test.pdf")
        self.assertEqual(text, "Extracted PDF text.\n")

    @patch("cv_tracking_system.services.document_processor.convert_from_path")
    @patch("cv_tracking_system.services.document_processor.pytesseract.image_to_string")
    def test_extract_text_with_ocr(self, mock_ocr, mock_convert_from_path):
        """Test OCR extraction for scanned PDFs"""
        mock_convert_from_path.return_value = [MagicMock()]
        mock_ocr.return_value = "Scanned text result."

        text = doc_proc.extract_text_with_ocr("test.pdf")
        self.assertEqual(text, "Scanned text result.")

    @patch("cv_tracking_system.services.document_processor.PyPDF2.PdfReader")
    @patch("cv_tracking_system.services.document_processor.extract_text_with_ocr")
    def test_extract_text_from_pdf_fallback_to_ocr(self, mock_ocr, mock_pdf_reader):
        """Test that PDF processing falls back to OCR when direct extraction fails"""
        mock_pdf_reader.return_value.pages = [MagicMock()]
        mock_pdf_reader.return_value.pages[0].extract_text.return_value = None  # Simulate failed extraction
        mock_ocr.return_value = "OCR extracted text."

        text = doc_proc.extract_text_from_pdf("test.pdf")
        self.assertEqual(text, "OCR extracted text.")

    @patch("cv_tracking_system.services.document_processor.docx.Document")
    def test_extract_text_from_docx(self, mock_docx):
        """Test DOCX text extraction"""
        mock_doc = MagicMock()
        mock_doc.paragraphs = [MagicMock(text="Paragraph 1"), MagicMock(text="Paragraph 2")]
        mock_doc.tables = []
        mock_docx.return_value = mock_doc

        text = doc_proc.extract_text_from_docx("test.docx")
        self.assertEqual(text, "Paragraph 1\nParagraph 2")

    def test_preprocess_text(self):
        """Test text preprocessing to remove extra whitespace and unwanted characters"""
        raw_text = "   Hello,  World! \n\n Welcome to testing...  "
        cleaned_text = doc_proc.preprocess_text(raw_text)
        self.assertEqual(cleaned_text, "Hello, World! Welcome to testing...")

    @patch("cv_tracking_system.services.document_processor.extract_text_from_pdf")
    def test_process_document_pdf(self, mock_extract_pdf):
        """Test processing a PDF document"""
        mock_extract_pdf.return_value = "Raw extracted text from PDF."
        result = doc_proc.process_document("sample.pdf")
        self.assertEqual(result, "Raw extracted text from PDF.")

    @patch("cv_tracking_system.services.document_processor.extract_text_from_docx")
    def test_process_document_docx(self, mock_extract_docx):
        """Test processing a DOCX document"""
        mock_extract_docx.return_value = "Raw extracted text from DOCX."
        result = doc_proc.process_document("sample.docx")
        self.assertEqual(result, "Raw extracted text from DOCX.")

    def test_process_document_unsupported_format(self):
        """Test error handling for unsupported file formats"""
        with self.assertRaises(ValueError) as context:
            doc_proc.process_document("sample.txt")
        self.assertEqual(str(context.exception), "Unsupported file format: .txt")

if __name__ == "__main__":
    unittest.main()
