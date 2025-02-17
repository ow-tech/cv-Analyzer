from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
      path('upload/', views.UploadView.as_view(), name='upload'),
    path('candidates/', views.CandidatesView.as_view(), name='candidates'),
    path('candidates/<int:pk>/', views.CandidateDetailView.as_view(), name='candidate_detail'),
    path('chat/', views.ChatView.as_view(), name='chat'),

]
