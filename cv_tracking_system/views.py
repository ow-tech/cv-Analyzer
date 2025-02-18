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
        return render(request, 'cv_tracking_system/home.html')
class ChatView(View):
    def get(self, request, pk):
        return render(request, 'cv_tracking_system/home.html')
