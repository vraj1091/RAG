import google.generativeai as genai
from app.core.config import settings
import asyncio
from typing import Optional
import traceback
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        try:
            self.gemini_model = genai.GenerativeModel("gemini-2.5-flash")
        except Exception as e:
            print(f"❌ Failed to initialize Gemini model: {e}")
            traceback.print_exc()
            self.gemini_model = None

    async def generate_response(self, message: str, context: Optional[str] = None) -> str:
        if not self.gemini_model:
            logger.error("Gemini model not initialized")
            return "❌ AI model not available"
        try:
            if context:
                prompt = f"Context: {context}\n\nQuestion: {message}\n\nPlease answer based on the provided context."
            else:
                prompt = message

            logger.info(f"Sending prompt to Gemini: {prompt}")

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, lambda: self.gemini_model.generate_content(prompt))

            if response and response.text:
                logger.info(f"Received response from Gemini with length {len(response.text)}")
                return response.text
            else:
                logger.warning("Received empty response text from Gemini API")
                return "❌ Empty response from Gemini API"

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            traceback.print_exc()
            return "Sorry, I couldn't generate a response at the moment."

    async def generate_general_response(self, message: str) -> str:
        return await self.generate_response(message)

    async def generate_rag_response(self, message: str, context: str) -> str:
        return await self.generate_response(message, context)
