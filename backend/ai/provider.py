import json
import logging
from config import settings

logger = logging.getLogger(__name__)

class LLMProvider:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER
        self.api_key = settings.LLM_API_KEY
        self.model_name = settings.LLM_MODEL
        self.client = None
        
        if self.is_available():
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model_name)
            except Exception as e:
                logger.error(f"Failed to initialize LLM provider: {e}")
    
    def is_available(self):
        return bool(self.api_key)
        
    async def generate(self, prompt: str, system_prompt: str = None, json_mode: bool = False) -> str:
        if not self.is_available() or not self.client:
            raise Exception("LLM Provider is not available. Please configure API Key.")
            
        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"System: {system_prompt}\n\nUser: {prompt}"
                
            if json_mode:
                full_prompt += "\n\nIMPORTANT: Return ONLY valid JSON. Do not include markdown code blocks."
                
            response = self.client.generate_content(full_prompt)
            
            text = response.text
            if json_mode:
                # Basic cleanup in case LLM added markdown formatting
                text = text.strip()
                if text.startswith("```json"):
                    text = text[7:]
                if text.startswith("```"):
                    text = text[3:]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()
                
            return text
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
