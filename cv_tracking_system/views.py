from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.utils.safestring import mark_safe
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
import logging
import uuid
import markdown
from .forms import CVUploadForm,QueryForm
from .services.document_processor import process_document
from .services.llm_client import LLMClient
from .services.information_extractor import extract_structured_info
from .services.query_processor import process_query
from .models import Candidate,ChatSession,ChatMessage
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
                print('raw_text', raw_text)
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

                # #  Update candidate info
                personal_info = structured_info.get('personal_info') or {}
                email = personal_info.get('email', '').strip()
             
                candidate, created = Candidate.objects.update_or_create(
                    email=email,
                    defaults={
                        'name': personal_info.get('name', 'Unknown'),
                        'phone': personal_info.get('phone', ''),
                        'location': personal_info.get('location', ''),
                        'raw_text': raw_text,
                        'structured_data': structured_info,
                        'file_path': candidate.file_path,
                    }
                )
                if created:
                    messages.success(request, f"Successfully added candidate {candidate.name}")
                else:
                    messages.success(request, f"Candidate {candidate.name} updated successfully")
                    
                Candidate.objects.filter(Q(email__isnull=True) | Q(email='')).delete()
                return redirect('candidates')

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
        candidates = Candidate.objects.all().order_by('-last_updated')
        return render(request, 'cv_tracking_system/candidates.html', {'candidates': candidates})

class CandidateDetailView(View):
    def get(self, request, pk):
        candidate = get_object_or_404(Candidate, pk=pk)
        return render(request, 'cv_tracking_system/candidate_detail.html', {'candidate': candidate})


class ChatView(View):
    
    def get(self, request):
        form = QueryForm()
             
         # Create or get session ID from cookies
        session_id = request.COOKIES.get('chat_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
          # Get chat history if session exists
          
        try:
            session = ChatSession.objects.get(session_id=session_id)
            messages = ChatMessage.objects.filter(session=session).order_by('timestamp')
            for message in messages:
                message.content = mark_safe(markdown.markdown(message.content))
        except ChatSession.DoesNotExist:
            messages = []
        
        response = render(request, 'cv_tracking_system/chat.html', {
            'form': form,
            'messages': messages,
        })
        
        # Set session cookie if needed
        if not request.COOKIES.get('chat_session_id'):
            response.set_cookie('chat_session_id', session_id, max_age=60*60*24*30)  # 30 days
            
        return response

    def post(self, request):
        form = QueryForm(request.POST)
        if form.is_valid():
            query = form.cleaned_data['query']
            session_id = request.COOKIES.get('chat_session_id', str(uuid.uuid4()))
            
            # Process query
            llm_client = LLMClient()
            response = process_query(query, session_id, llm_client)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON for AJAX requests
                
                return JsonResponse({'response': response})
            else:
                # Redirect for regular form submissions
                return redirect('chat')
        else:
            messages.error(request, "Invalid query")
            return redirect('chat')
