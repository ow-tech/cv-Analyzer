from django.db import models
from django.core.exceptions import ValidationError
# import magic  # File type detection
import os
import uuid
import json

# ---------------------------------------------
#Sanitize File Names
#Users may try to upload files with malicious filenames (e.g., script.php.exe). To prevent this, rename files securely before saving.
# Model: Candidate
# Purpose: Stores information about job candidates, including personal details, 
# resume text, AI-processed structured data, and AI-generated summaries.
# ---------------------------------------------


# Validate file type (PDF & Word only)
# def validate_file_type(file):
#     mime = magic.Magic(mime=True)
#     file_mime = mime.from_buffer(file.read(1024))  # Read first 1024 bytes
#     file.seek(0)  # Reset file pointer

#     allowed_mimes = [
#         'application/pdf',
#         'application/msword',
#         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
#     ]
    
#     if file_mime not in allowed_mimes:
#         raise ValidationError("Invalid file type. Only PDF and Word documents are allowed.")

# Validate file size (Max 5MB)
def validate_file_size(file):
    max_size = 5 * 1024 * 1024  # 5MB
    if file.size > max_size:
        raise ValidationError("File size exceeds the 5MB limit.")

# Secure filename (Avoid execution risks)
def unique_filename(instance, filename):
    ext = filename.split('.')[-1].lower()
    new_filename =f"{uuid.uuid4()}.{ext}"
    return new_filename


class Candidate(models.Model):
    name = models.CharField(max_length=200)  
    email = models.EmailField(unique=True, blank=True, null=True)  
    phone = models.CharField(max_length=20, blank=True, null=True) 
    location = models.CharField(max_length=200, blank=True, null=True) 
    raw_text = models.TextField()  # Raw extracted resume text
    structured_data = models.JSONField(default=dict)
    file_path = models.FileField(
        upload_to=unique_filename,validators=[validate_file_size])  
    last_updated = models.DateTimeField(auto_now=True)  
    ai_summary = models.TextField(blank=True, null=True)  

    def __str__(self):
        skills = ", ".join(self.structured_data.get("skills", [])) or "No skills"
        education = "; ".join(self.structured_data.get("education", [])) or "No education"
        experience = "; ".join(self.structured_data.get("experience", [])) or "No experience"

        return f"{self.name} | {self.email} | Skills: {skills} | Education: {education} | Experience: {experience}"


    # Helper methods to retrieve structured AI-parsed data
    def get_skills(self):
        skills = self.structured_data.get('skills', [])
        return skills if isinstance(skills, list) else []


    def get_education(self):
        return self.structured_data.get('education', [])

    def get_experience(self):
        return self.structured_data.get('work_experience', [])

    def get_projects(self):
        return self.structured_data.get('projects', [])

    def get_certifications(self):
        return self.structured_data.get('certifications', [])


# ---------------------------------------------
# Model: ChatSession
# Purpose: Represents a conversation session for OpenAI API-based chatbot interactions.
# ---------------------------------------------
class ChatSession(models.Model):
    session_id = models.CharField(max_length=100, unique=True)  
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Chat Session {self.session_id}"


# # ---------------------------------------------
# # Model: ChatMessage
# # Purpose: Stores chat messages exchanged during a session, including user inputs and OpenAI responses.
# # ---------------------------------------------
class ChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),  # Message from the user
        ('assistant', 'Assistant'),  # Response from OpenAI
        ('system', 'System'),  # System messages (if needed)
    ]

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')  
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)  
    content = models.TextField()  
    timestamp = models.DateTimeField(auto_now_add=True) 
    openai_message_id = models.CharField(max_length=255, blank=True, null=True)  

    class Meta:
        ordering = ['timestamp'] 
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."
