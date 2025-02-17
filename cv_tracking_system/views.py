from django.shortcuts import render
from django.views import View

class HomeView(View):
    def get(self, request):
        return render(request, 'cv_tracking_system/home.html')
class UploadView(View):
    def get(self, request):
        return render(request, 'cv_tracking_system/upload.html')
class CandidatesView(View):
    def get(self, request):
        return render(request, 'cv_tracking_system/upload.html')

class CandidateDetailView(View):
    def get(self, request, pk):
        return render(request, 'cv_tracking_system/home.html')
class ChatView(View):
    def get(self, request, pk):
        return render(request, 'cv_tracking_system/home.html')
