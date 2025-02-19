from django import forms
from .models import Candidate
from django.core.exceptions import ValidationError

def validate_cv_file(value):
    """Custom validator to allow only PDF and Word files."""
    valid_extensions = ['.pdf', '.doc', '.docx']
    if not any(value.name.lower().endswith(ext) for ext in valid_extensions):
        raise ValidationError("Only PDF and Word documents are allowed.")

class CVUploadForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields = ['file_path']
        labels = {
            'file_path': 'CV Document (PDF or Word)',
        }
        widgets = {
            'file_path': forms.FileInput(attrs={'class': 'form-input'}),
        }

    def clean_file_path(self):
        file = self.cleaned_data.get('file_path')
        if file:
            validate_cv_file(file)
        return file


class QueryForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Ask about candidates...'
        }),
        label=''
    )