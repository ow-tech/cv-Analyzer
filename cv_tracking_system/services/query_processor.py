# import json

# from django.db.models import Q
# from .llm_client import LLMClient
# from cv_tracking_system.models import Candidate, ChatSession, ChatMessage

# def process_query(query, session_id, llm_client=None):
#     if not session_id:
#         raise ValueError("Session ID cannot be None or empty")

#     if llm_client is None:
#         llm_client = LLMClient()
    
#     session, _ = ChatSession.objects.get_or_create(session_id=session_id)
    
#     # Save user message
#     ChatMessage.objects.create(session=session, role='user', content=query)
    
#     # Get conversation history
#     # history = ChatMessage.objects.filter(session=session).order_by('timestamp')
#     # conversation_context = "\n".join([f"{msg.role}: {msg.content}" for msg in history[-5:]])
    
#     # Get conversation history, ordered by timestamp
#     history = list(ChatMessage.objects.filter(session=session).order_by('timestamp'))  # Convert QuerySet to list ✅

#     # Get the last 5 messages safely
#     recent_messages = history[-5:] if len(history) >= 5 else history

#     # Format the conversation context
#     conversation_context = "\n".join([f"{msg.role}: {msg.content}" for msg in recent_messages])
    
#     # Extract query intent and parameters
#     query_analysis_prompt = f"..."
#     query_analysis = llm_client.generate_text(query_analysis_prompt)

#     try:
#         query_params = json.loads(query_analysis)
#     except json.JSONDecodeError:
#         query_params = {
#             "intent": "other",
#             "parameters": {},
#             "is_followup": False,
#             "django_filter": f"raw_text__icontains='{query}'"
#         }

#     # Execute query
#     filters = query_params.get('django_filter', "").split(' & ')
#     q_objects = Q()

#     for condition in filters:
#         try:
#             field, value = condition.split('=')
#             q_objects &= Q(**{field.strip(): value.strip("'")})
#         except ValueError:
#             continue  # Skip invalid conditions

#     results = Candidate.objects.filter(q_objects) if q_objects else Candidate.objects.filter(raw_text__icontains=query)

#     # Format results
#     result_data = [
#         {
#             "name": candidate.name,
#             "email": candidate.email,
#             "skills": candidate.get_skills(),
#             "education": candidate.get_education(),
#             "experience": candidate.get_experience()
#         }
#         for candidate in results[:10]
#     ]
    
#     if not result_data:
#         response = "No matching candidates found. Try refining your search criteria."
#     else:
#         result_prompt = f"..."
#         response = llm_client.generate_text(result_prompt)

#     ChatMessage.objects.create(session=session, role='assistant', content=response)

#     return response
# core/services/query_processor.py
import re
import json
from .llm_client import LLMClient
from cv_tracking_system.models import Candidate, ChatSession, ChatMessage

def process_query(query, session_id, llm_client=None):
    """Process natural language queries about candidate information"""
    if llm_client is None:
        llm_client = LLMClient()
    
    # Get or create chat session
    session, created = ChatSession.objects.get_or_create(session_id=session_id)
    
#    session, _ = ChatSession.objects.get_or_create(session_id=session_id)

    # Save user message
    ChatMessage.objects.create(session=session, role='user', content=query)

# Get conversation history, ordered by timestamp
    history = list(ChatMessage.objects.filter(session=session).order_by('timestamp'))  # Convert QuerySet to list ✅

# Get the last 5 messages safely
    recent_messages = history[-5:] if len(history) >= 5 else history

# Format the conversation context
    conversation_context = "\n".join([f"{msg.role}: {msg.content}" for msg in recent_messages])

    
    # Extract query intent and parameters using the LLM
    query_analysis_prompt = f"""
    Given this conversation history:
    {conversation_context}
    
    Analyze the following query about job candidates and extract the search intent and parameters:
    
    Query: "{query}"
    
    Determine if this is a query about:
    1. Specific skills (which skills?)
    2. Education level (what level or field?)
    3. Work experience (what industry, role, or years?)
    4. Comparing candidates (on what criteria?)
    5. Other (specify)
    
    Output in JSON format:
    {{
        "intent": "skills|education|experience|comparison|other",
        "parameters": {{relevant parameters based on intent}},
        "is_followup": true/false,
        "django_filter": "field__contains='value'" or "field1__contains='value1' & field2__contains='value2'"
    }}
    """
    
    query_analysis = llm_client.generate_text(query_analysis_prompt)
    
    # Extract JSON from the response
    try:
        json_match = re.search(r'{.*}', query_analysis, re.DOTALL)
        if json_match:
            query_params = json.loads(json_match.group())
        else:
            raise ValueError("Could not extract JSON from response")
    except:
        # Fallback if JSON parsing fails
        query_params = {
            "intent": "other",
            "parameters": {},
            "is_followup": False,
            "django_filter": f"raw_text__icontains='{query}'"
        }
    
    # Execute query against our database
    try:
        if 'django_filter' in query_params and query_params['django_filter']:
            filter_expr = query_params['django_filter']
            
            # Simple parsing to handle basic AND conditions
            if ' & ' in filter_expr:
                conditions = filter_expr.split(' & ')
                q_objects = None
                for condition in conditions:
                    field, value = condition.split('=')
                    if q_objects is None:
                        q_objects = Q(**{field: value.strip("'")})
                    else:
                        q_objects &= Q(**{field: value.strip("'")})
                results = Candidate.objects.filter(q_objects)
            else:
                field, value = filter_expr.split('=')
                results = Candidate.objects.filter(**{field: value.strip("'")})
        else:
            # Fallback to simple text search
            results = Candidate.objects.filter(raw_text__icontains=query)
    except:
        # Ultimate fallback - search all candidates
        results = Candidate.objects.all()
    
    # Format results using LLM
    result_data = []
    for candidate in results[:10]:  # Limit to 10 results for performance
        result_data.append({
            "name": candidate.name,
            "email": candidate.email,
            "skills": candidate.get_skills(),
            "education": candidate.get_education(),
            "experience": candidate.get_experience()
        })
    
    result_prompt = f"""
    Based on the query "{query}" and conversation history:
    {conversation_context}
    
    Here are the candidate results:
    {json.dumps(result_data, indent=2)}
    
    Provide a natural language summary of these results.
    If no results were found, suggest alternative search criteria.
    """
    
    response = llm_client.generate_text(result_prompt)
    
    # Save assistant message
    ChatMessage.objects.create(session=session, role='assistant', content=response)
    
    return response