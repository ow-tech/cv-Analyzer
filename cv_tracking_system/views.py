from django.shortcuts import render
from django.views import View
from django.utils.timezone import now

class HomeView(View):
    def get(self, request):
        return render(request, 'cv_tracking_system/home.html')
class UploadView(View):
    def get(self, request):
        return render(request, 'cv_tracking_system/upload.html')
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
