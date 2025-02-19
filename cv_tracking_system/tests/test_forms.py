from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from cv_tracking_system.forms import CVUploadForm, QueryForm
from cv_tracking_system.models import Candidate


#python manage.py test cv_tracking_system.tests.test_forms
class CVUploadFormTest(TestCase):
    def test_valid_cv_upload_form(self):
        """Test that a valid CV file is accepted."""
        file = SimpleUploadedFile("resume.pdf", b"dummy data", content_type="application/pdf")
        form = CVUploadForm(data={}, files={"file_path": file})
        self.assertTrue(form.is_valid())

    def test_invalid_cv_upload_form(self):
        """Test that an invalid file type is rejected."""
        file = SimpleUploadedFile("resume.txt", b"dummy data", content_type="text/plain")
        form = CVUploadForm(data={}, files={"file_path": file})
        self.assertFalse(form.is_valid())
        self.assertIn("file_path", form.errors)

class QueryFormTest(TestCase):
    def test_valid_query_form(self):
        """Test that the QueryForm accepts a valid query string."""
        form = QueryForm(data={"query": "Tell me about candidate John Doe."})
        self.assertTrue(form.is_valid())

    def test_empty_query_form(self):
        """Test that an empty query is invalid."""
        form = QueryForm(data={"query": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("query", form.errors)

