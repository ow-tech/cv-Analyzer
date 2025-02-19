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
class QueryForm(forms.Form):
    query = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Ask about candidates...'
        }),
        label=''
    )