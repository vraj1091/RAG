import ollama
import asyncio
from typing import Optional
import traceback
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class DeepSeekService:
    """
    Local Phi-3 Mini / DeepSeek service using Ollama
    Optimized for fast RAG responses with chart generation support
    """
    
    def __init__(self):
        self.client = ollama.Client(host=settings.ollama_base_url)
        self.model_name = settings.ollama_model_name
        self.timeout = settings.ollama_timeout
        
        # Test connection and model availability
        try:
            self._test_connection()
            print(f"✅ Model '{self.model_name}' initialized successfully")
        except Exception as e:
            print(f"⚠️ Model test warning: {e}")
            print("⚠️ Model will still work, but initial test failed")

    def _test_connection(self):
        """Test if Ollama server and model are available"""
        try:
            models = self.client.list()
            available_models = [model.model for model in models.models]
            
            if self.model_name not in available_models:
                raise Exception(f"Model '{self.model_name}' not found. Run: ollama pull {self.model_name}")
            
            logger.info(f"✅ Model '{self.model_name}' found in Ollama")
            
        except Exception as e:
            logger.error(f"Model connection test failed: {e}")
            raise

    async def generate_response(self, message: str, context: Optional[str] = None) -> str:
        """
        Generate response using local model with chart-aware prompts
        """
        if not self.client:
            logger.error("Model not initialized")
            return "❌ AI model not available - please ensure Ollama is running"

        try:
            # Check if user wants a chart
            chart_keywords = ['chart', 'graph', 'bar chart', 'pie chart', 'visualize', 'show me']
            wants_chart = any(kw in message.lower() for kw in chart_keywords)
            
            messages = []
            
            if context:
                # Limit context to prevent overload
                context = context[:1000]
                
                if wants_chart:
                    # EXPLICIT prompt for chart data extraction
                    system_prompt = """You are a data extraction assistant. Extract ONLY numerical totals.
DO NOT write code. DO NOT write explanations. ONLY provide data in the format shown."""
                    
                    user_prompt = f"""Data: {context}

Extract total revenue by region and output ONLY in this format:
East: 1990
Central: 2463
West: 927

DO NOT write Python code.
DO NOT provide explanations.
ONLY provide region name: number"""
                    
                    messages = [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': user_prompt}
                    ]
                else:
                    # Normal context-based question
                    system_prompt = """You are a helpful AI assistant. Answer based on the context provided.
Be concise and accurate."""
                    
                    messages = [
                        {'role': 'system', 'content': system_prompt},
                        {'role': 'user', 'content': f"Context: {context}\n\nQuestion: {message}"}
                    ]
            else:
                # General chat without context
                system_prompt = "You are a helpful, knowledgeable AI assistant."
                messages = [
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': message}
                ]

            logger.info(f"Sending request to {self.model_name}: {len(message)} chars")
            
            loop = asyncio.get_event_loop()
            
            # Set options based on chart vs normal query
            options = {
                'temperature': 0.1 if wants_chart else settings.model_temperature,
                'top_p': settings.model_top_p,
                'num_predict': 150 if wants_chart else settings.max_tokens,
                'num_ctx': 2048,
            }
            
            try:
                response = await asyncio.wait_for(
                    loop.run_in_executor(
                        None, 
                        lambda: self.client.chat(
                            model=self.model_name,
                            messages=messages,
                            options=options
                        )
                    ),
                    timeout=120.0
                )
            except asyncio.TimeoutError:
                logger.error("Model timeout after 120s")
                return "⏱️ The AI model took too long to respond. Please try a simpler question."

            if response and response.get('message', {}).get('content'):
                response_text = response['message']['content'].strip()
                if response_text:
                    logger.info(f"✅ Received response: {len(response_text)} chars")
                    return response_text
                else:
                    logger.warning("Empty response received")
                    return "❌ Empty response from model"
            else:
                logger.warning("No response from model")
                return "❌ No response from model"

        except Exception as e:
            logger.error(f"Model API error: {e}")
            traceback.print_exc()
            return f"❌ Sorry, I encountered an error: {str(e)}"

    def generate_content(self, prompt: str):
        """
        Synchronous wrapper for compatibility
        """
        class Response:
            def __init__(self, text):
                self.text = text
        
        try:
            if not self.client:
                return Response("❌ AI model not available")
                
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': prompt}],
                options={
                    'temperature': settings.model_temperature,
                    'top_p': settings.model_top_p,
                    'num_predict': settings.max_tokens,
                    'num_ctx': 2048,
                }
            )
            return Response(response['message']['content'])
        except Exception as e:
            logger.error(f"generate_content error: {e}")
            return Response(f"Error: {str(e)}")

    async def generate_general_response(self, message: str) -> str:
        """Generate response for general chat"""
        return await self.generate_response(message)

    async def generate_rag_response(self, message: str, context: str) -> str:
        """Generate response with RAG context"""
        return await self.generate_response(message, context)

# Create global instance
deepseek_service = DeepSeekService()
