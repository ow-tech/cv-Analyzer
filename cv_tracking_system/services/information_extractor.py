import re
import json
from .llm_client import LLMClient

def extract_structured_info(text, llm_client=None):
    """Use LLM to extract structured information from CV text"""
    if not text.strip():
        return {"error": "Empty CV text provided"}

    if llm_client is None:
        llm_client = LLMClient()
    # print("LLMClient Instance:", llm_client)     
    prompt = f"""
    You are an AI that extracts structured JSON from resumes.
    
    Extract the following information:
    1. Personal Information (name, email, phone, location)
    2. Education History (institution, degree, field, years)
    3. Work Experience (company, role, duration, responsibilities)
    4. Skills (technical skills, soft skills)
    5. Projects (name, description, technologies used)
    6. Certifications (name, issuer, date)

    If the CV is too long, analyze only the first 4000 characters.

    Return JSON ONLY, without explanations, following this format:
    {{
        "personal_info": {{
            "name": "John Doe",
            "email": "johndoe@example.com",
            "phone": "+1-234-567-8901",
            "location": "New York, USA"
        }},
        "education": [
            {{
                "institution": "Harvard University",
                "degree": "BSc in Computer Science",
                "field": "Computer Science",
                "years": "2015-2019"
            }}
        ],
        "work_experience": [
            {{
                "company": "Google",
                "role": "Software Engineer",
                "duration": "2019-2023",
                "responsibilities": [
                    "Developed scalable backend systems",
                    "Led a team of 5 engineers"
                ]
            }}
        ],
        "skills": ["Python", "JavaScript", "Machine Learning"],
        "projects": [
            {{
                "name": "AI Chatbot",
                "description": "Built using OpenAI API and Flask",
                "technologies_used": ["Python", "Flask", "OpenAI API"]
            }}
        ],
        "certifications": [
            {{
                "name": "AWS Certified Solutions Architect",
                "issuer": "AWS",
                "date": "2021"
            }}
        ]
    }}
    
    CV Text:
    {text[:4000]}
    """
    
    try:
        response = llm_client.generate_text(prompt)
        # print('response responsere sponse response ', response)
        try:
          
            return json.loads(response.strip())  # Try parsing JSON directly
        except json.JSONDecodeError:
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    return {"error": "Failed to parse valid JSON from LLM response"}
            else:
                return {"error": "No JSON detected in LLM response"}
    except Exception as e:
        return {"error": f"LLM processing failed: {str(e)}"}
