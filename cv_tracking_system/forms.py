from django import forms
from .models import Candidate


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
