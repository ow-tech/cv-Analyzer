import os
import time
import openai
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from dotenv import load_dotenv  # Ensure you have python-dotenv installed

# Load environment variables
load_dotenv()

class LLMClient:
    def __init__(self, provider='openai', model="gpt-4o-mini", api_key=None):
        self.provider = provider
        self.model = model
        self.api_key =os.getenv("OPENAI_API_KEY")  # Securely load API key
        self.last_request_time = 0

        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Set it in the .env file or environment variables.")

        if provider == 'openai':
            self.client = OpenAI(api_key=self.api_key)  # OpenAI only

    def _respect_rate_limit(self, min_interval=1.0):
        """Rate limiting to prevent excessive API calls"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
    def generate_text(self, prompt):
        self._respect_rate_limit()
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            return response.choices[0].message.content.strip()
        except openai.RateLimitError as e:
            print(f"Rate limit reached: {str(e)}. Retrying...")
            raise
        except Exception as e:
            print(f"LLM API error: {str(e)}")
            raise

