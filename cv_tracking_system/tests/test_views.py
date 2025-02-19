from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from unittest.mock import patch
from cv_tracking_system.models import Candidate


# python manage.py test cv_tracking_system.tests.test_views

class UploadViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.upload_url = reverse('upload')  # Adjust based on your URL name

    def test_get_request_renders_upload_page(self):
        """Test that GET request returns the upload page with an empty form."""
        response = self.client.get(self.upload_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cv_tracking_system/upload.html')
        self.assertIn('form', response.context)

    def test_post_request_without_file_shows_error(self):
        """Test that submitting the form without a file shows an error message."""
        response = self.client.post(self.upload_url, {})
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Form submission error. Please check the form.", messages)

    def test_post_invalid_file_format(self):
        """Test that an invalid file format shows an error message."""
        invalid_file = SimpleUploadedFile("test.txt", b"Fake CV content", content_type="text/plain")
        response = self.client.post(self.upload_url, {'file_path': invalid_file})
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertTrue(any("Invalid data: Unsupported file format" in msg for msg in messages))

    @patch("cv_tracking_system.views.process_document", return_value="Extracted CV text")
    @patch("cv_tracking_system.views.extract_structured_info", return_value={
    "personal_info": {"name": "John Doe", "email": "john.doe@example.com"},
    "skills": ["Python", "Django"]
    })
    
    def test_post_valid_file_creates_candidate(self, mock_process_doc, mock_extract_info):
        """Test that a valid CV file is processed and saves a Candidate."""
        valid_cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 CV content", content_type="application/pdf")
        response = self.client.post(self.upload_url, {'file_path': valid_cv}) 
        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        
        print("Messages:", messages)
        candidate = Candidate.objects.filter(email="john.doe@example.com").first()
        self.assertIsNotNone(candidate, "Candidate was not created in the database.")
        
        self.assertRedirects(response, reverse('candidates'))
        
        expected_message = f"Successfully added candidate {candidate.name}"

        
        self.assertIn(expected_message, messages, f"Expected message '{expected_message}' not found in {messages}")

    @patch("cv_tracking_system.views.process_document", return_value=None)
    
    
    def test_post_with_cv_that_fails_text_extraction(self, mock_process_doc):
        """Test when CV text extraction fails, an error message is shown."""
        valid_cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 CV content", content_type="application/pdf")
        response = self.client.post(self.upload_url, {'file_path': valid_cv})

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Failed to extract text from CV.", messages)
        self.assertRedirects(response, self.upload_url)

    @patch("cv_tracking_system.views.process_document", return_value="Extracted CV text")
    @patch("cv_tracking_system.views.extract_structured_info", return_value={"error": "Invalid CV format"})
    def test_post_with_invalid_structured_info(self, mock_process_doc, mock_extract_info):
        """Test when structured info extraction fails, an error message is shown."""
        valid_cv = SimpleUploadedFile("cv.pdf", b"%PDF-1.4 CV content", content_type="application/pdf")
        response = self.client.post(self.upload_url, {'file_path': valid_cv})

        messages = [msg.message for msg in get_messages(response.wsgi_request)]
        self.assertIn("Failed to process structured info.", messages)
        self.assertRedirects(response, self.upload_url)
        
        
        
        
        
        
        
class CandidatesViewTest(TestCase):
    def setUp(self):
        """Set up sample candidates for testing."""
        self.candidate1 = Candidate.objects.create(name="Alice", email="alice@example.com")
        self.candidate2 = Candidate.objects.create(name="Bob", email="bob@example.com")

    def test_candidates_view_renders_correctly(self):
        """Test that the candidates page loads and displays candidates."""
        response = self.client.get(reverse('candidates'))  # Ensure 'candidates' is the correct URL name
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cv_tracking_system/candidates.html')
        self.assertContains(response, "Alice")
        self.assertContains(response, "Bob")


class CandidateDetailViewTest(TestCase):
    def setUp(self):
        """Set up a candidate for testing."""
        self.candidate = Candidate.objects.create(name="Alice", email="alice@example.com")

    def test_candidate_detail_view_renders_correctly(self):
        """Test that a specific candidate's page loads correctly."""
        response = self.client.get(reverse('candidate_detail', args=[self.candidate.pk]))  # Ensure URL matches
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cv_tracking_system/candidate_detail.html')
        self.assertContains(response, "Alice")
        self.assertContains(response, "alice@example.com")

    def test_candidate_detail_view_404_for_invalid_candidate(self):
        """Test that accessing a non-existent candidate returns a 404."""
        response = self.client.get(reverse('candidate_detail', args=[999]))  # Non-existent candidate
        self.assertEqual(response.status_code, 404)
    
from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
import uuid
from cv_tracking_system.models import ChatSession, ChatMessage
from cv_tracking_system.forms import QueryForm

class ChatViewTest(TestCase):
    def setUp(self):
        """Set up a client and a chat session for testing."""
        self.client = Client()
        self.session_id = str(uuid.uuid4())
        self.chat_session = ChatSession.objects.create(session_id=self.session_id)
        ChatMessage.objects.create(session=self.chat_session, content="Hello!")

    def test_chat_view_renders_correctly(self):
        """Test that the chat page loads and displays messages."""
        response = self.client.get(reverse('chat'))  # Ensure 'chat' matches your URL pattern
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'cv_tracking_system/chat.html')
        self.assertIsInstance(response.context['form'], QueryForm)

    def test_chat_view_sets_session_cookie(self):
        """Test that a new session ID is created and set in cookies."""
        response = self.client.get(reverse('chat'))
        self.assertTrue('chat_session_id' in response.cookies)

    @patch('cv_tracking_system.views.process_query')
    def test_chat_view_post_valid_query(self, mock_process_query):
        """Test that submitting a valid query processes a response."""
        mock_process_query.return_value = "Processed response"

        response = self.client.post(reverse('chat'), {'query': 'Test query'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'response': 'Processed response'})

    def test_chat_view_post_invalid_query(self):
        """Test that submitting an invalid query shows an error."""
        response = self.client.post(reverse('chat'), {'query': ''})  # Empty query
        self.assertRedirects(response, reverse('chat'))
