from django.test import TestCase
from cv_tracking_system.models import Candidate, ChatSession, ChatMessage
from datetime import datetime
from django.core.exceptions import ValidationError



# python manage.py test cv_tracking_system.tests.test_models

class CandidateModelTest(TestCase):

    def setUp(self):
        """Setup a candidate object for testing."""
        self.candidate = Candidate.objects.create(
            name="John Doe",
            email="john.doe@example.com",
            phone="+1234567890",
            location="New York",
            raw_text="Experienced software engineer with expertise in Python.",
            structured_data={
                "skills": ["Python", "Django", "Machine Learning"],
                "education": ["BSc Computer Science"],
                "work_experience": ["Software Engineer at Google"]
            },
            ai_summary="AI-generated summary here."
        )

    def test_candidate_creation(self):
        """Test that a Candidate instance is created correctly."""
        self.assertEqual(self.candidate.name, "John Doe")
        self.assertEqual(self.candidate.email, "john.doe@example.com")
        self.assertEqual(self.candidate.location, "New York")

    def test_candidate_string_representation(self):
        print("DEBUG: structured_data =", self.candidate.structured_data) 
        """Test the __str__ method of Candidate model."""
        expected_str = "John Doe | john.doe@example.com | Skills: Python, Django, Machine Learning | Education: BSc Computer Science | Experience: Software Engineer at Google"
        self.assertEqual(str(self.candidate), expected_str)

    def test_candidate_get_skills(self):
        """Test retrieval of skills from structured data."""
        self.assertEqual(self.candidate.get_skills(), ["Python", "Django", "Machine Learning"])

    def test_candidate_get_education(self):
        """Test retrieval of education details."""
        self.assertEqual(self.candidate.get_education(), ["BSc Computer Science"])

    def test_candidate_get_experience(self):
        """Test retrieval of work experience."""
        self.assertEqual(self.candidate.get_experience(), ["Software Engineer at Google"])

    def test_candidate_empty_fields(self):
        """Test creating a Candidate with blank optional fields."""
        candidate = Candidate.objects.create(name="Alice")
        self.assertIsNone(candidate.email)
        self.assertIsNone(candidate.phone)
        self.assertIsNone(candidate.location)
        self.assertEqual(candidate.get_skills(), [])  # Expecting an empty list
        self.assertEqual(candidate.get_experience(), [])  # No experience data

    def test_candidate_invalid_email(self):
        """Test validation for invalid email format."""
        candidate = Candidate(name="Bob", email="invalid-email")
        with self.assertRaises(ValidationError):
            candidate.full_clean()  # Forces model validation


class ChatSessionModelTest(TestCase):

    def setUp(self):
        """Setup a ChatSession instance for testing."""
        self.session = ChatSession.objects.create(session_id="123ABC")

    def test_chat_session_creation(self):
        """Test that a ChatSession instance is created successfully."""
        self.assertEqual(self.session.session_id, "123ABC")
        self.assertIsInstance(self.session.created_at, datetime)
        self.assertIsInstance(self.session.last_activity, datetime)

    def test_chat_session_string_representation(self):
        """Test the __str__ method of ChatSession model."""
        self.assertEqual(str(self.session), "Chat Session 123ABC")


class ChatMessageModelTest(TestCase):

    def setUp(self):
        """Setup a ChatSession and ChatMessage instance for testing."""
        self.session = ChatSession.objects.create(session_id="456DEF")
        self.message = ChatMessage.objects.create(
            session=self.session,
            role="user",
            content="Hello, how are you?",
            openai_message_id="msg-123"
        )

    def test_chat_message_creation(self):
        """Test that a ChatMessage instance is created successfully."""
        self.assertEqual(self.message.session, self.session)
        self.assertEqual(self.message.role, "user")
        self.assertEqual(self.message.content, "Hello, how are you?")
        self.assertEqual(self.message.openai_message_id, "msg-123")

    def test_chat_message_string_representation(self):
        """Test the __str__ method of ChatMessage model."""
        self.assertEqual(str(self.message), "user: Hello, how are you?...")

    def test_chat_message_role_choices(self):
        """Test that the role field accepts only predefined choices."""
        with self.assertRaises(ValidationError):
            invalid_message = ChatMessage(session=self.session, role="invalid_role", content="Test")
            invalid_message.full_clean()  # This should raise a ValidationError

    def test_chat_message_ordering(self):
        """Test that messages are ordered by timestamp."""
        msg1 = ChatMessage.objects.create(session=self.session, role="assistant", content="Hi, I'm fine.")
        msg2 = ChatMessage.objects.create(session=self.session, role="system", content="System message.")

        messages = list(self.session.messages.all())  # Fetch messages in order
        self.assertEqual(messages[0], self.message)  # First message created should be first
        self.assertEqual(messages[1], msg1)  # Second should be assistant reply
        self.assertEqual(messages[2], msg2)  # Third should be system message
