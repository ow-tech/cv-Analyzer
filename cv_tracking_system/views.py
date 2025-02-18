from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.contrib import messages

from django.http import HttpResponseRedirect
from django.urls import reverse
import logging
import os
from .forms import CVUploadForm
from .models import Candidate, unique_filename
from .services.document_processor import process_document
from .services.llm_client import LLMClient
from .services.information_extractor import extract_structured_info
logger = logging.getLogger(__name__)
class HomeView(View):
    def get(self, request):
        return render(request, 'cv_tracking_system/home.html')
    


logger = logging.getLogger(__name__)

class UploadView(View):
    def get(self, request):
        form = CVUploadForm()
        return render(request, 'cv_tracking_system/upload.html', {'form': form})

    def post(self, request):
        form = CVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save(commit=False)
            if not request.FILES.get('file_path'):  # ✅ Check if file exists
                messages.error(request, "No file was uploaded.")
                return redirect('upload')
            candidate.save()
            #  Ensure file exists
            if not candidate.file_path or not candidate.file_path.name:
                messages.error(request, "No file was uploaded.")
                return redirect('upload')

            try:
                #  Process document safely
                raw_text = process_document(candidate.file_path.path)
                # print('raw_text', raw_text)
                if not raw_text:
                    messages.error(request, "Failed to extract text from CV.")
                    return redirect('upload')

                llm_client = LLMClient() 
                structured_info = extract_structured_info(raw_text, llm_client)
                print('structured_info structured_info', structured_info)
                if not structured_info or 'error' in structured_info:
                    messages.error(request, "Failed to process structured info.")
                    return redirect('upload')

                if 'error' in structured_info:
                    messages.error(request, f"Error processing CV: {structured_info['error']}")
                    return redirect('upload')

                #  Update candidate info
                personal_info = structured_info.get('personal_info') or {}
                candidate.name = personal_info.get('name', 'Unknown')
                candidate.email = personal_info.get('email', '')
                candidate.phone = personal_info.get('phone', '')
                candidate.location = personal_info.get('location', '')
                candidate.raw_text = raw_text
                candidate.structured_data = structured_info

                candidate.save()
                messages.success(request, f"Successfully processed CV for {candidate.name}")
                return redirect('upload')

            except ValueError as e:
                messages.error(request, f"Invalid data: {str(e)}")
                logger.error(f"ValueError in UploadView: {e}")
                return redirect('upload')

            except Exception as e:
                messages.error(request, "Unexpected error occurred.")
                logger.error(f"Unexpected error in UploadView: {e}", exc_info=True)
                return redirect('upload')

        else:
            messages.error(request, "Form submission error. Please check the form.")
            return render(request, 'cv_tracking_system/upload.html', {'form': form})

   
class CandidatesView(View):
    def get(self, request):
        candidates = [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                "location": "New York, USA",
                "skills": ["Python", "Django", "REST API"],
                "last_updated": now()
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "location": "London, UK",
                "skills": ["SEO", "Digital Marketing", "Google Ads"],
                "last_updated": now()
            },
            {
                "id": 3,
                "name": "Michael Brown",
                "email": "michael.brown@example.com",
                "location": "Paris, France",
                "skills": ["Machine Learning", "AI", "Python"],
                "last_updated": now()
            }
        ]
        return render(request, 'cv_tracking_system/candidates.html', {"candidates": candidates})

class CandidateDetailView(View):
    def get(self, request, pk):
        candidate = {
        "name": "John Doe",
        "email": "johndoe@example.com",
        "phone": "+1 234 567 890",
        "location": "New York, USA",
        "get_skills": lambda: ["Python", "Django", "JavaScript", "React"],
        "get_education": lambda: [
            {"degree": "BSc", "field": "Computer Science", "institution": "MIT", "years": "2015 - 2019"}
        ],
        "get_experience": lambda: [
            {"role": "Software Engineer", "company": "Google", "duration": "2019 - Present", "responsibilities": "Developing scalable web applications"}
        ],
        "get_projects": lambda: [
            {"name": "Portfolio Website", "description": "A personal portfolio website", "technologies": ["HTML", "CSS", "JavaScript"]}
        ],
        "get_certifications": lambda: [
            {"name": "AWS Certified Developer", "issuer": "Amazon", "date": "2022"}
        ],
    }
        return render(request, 'cv_tracking_system/candidate_detail.html', {"candidate": candidate})
class ChatView(View):
    def get(self, request):
        dummy_messages = [
            {"role": "user", "content": "Find candidates with Python experience."},
            {"role": "assistant", "content": "Here are some candidates with Python expertise:\n\n1. John Doe - 5 years of experience.\n2. Jane Smith - 3 years of experience."},
            {"role": "user", "content": "Who has experience in project management?"},
            {"role": "assistant", "content": "Candidates with project management experience:\n\n1. Alex Johnson - PMP Certified.\n2. Emily Davis - 7 years of experience."},
        ]
        return render(request, 'cv_tracking_system/chat.html', {"messages": dummy_messages})
