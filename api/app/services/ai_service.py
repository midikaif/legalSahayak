import logging
import asyncio
from fastapi import HTTPException
from google.genai import types
import google.genai as genai
from app.core.config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

async def get_ai_analysis(prompt: str, context: str = "") -> str:
    """Get AI analysis using Gemini Flash (fast + affordable)"""
    max_retries = 3
    base_delay = 2

    for attempt in range(max_retries):
        try:
            client = genai.Client(api_key=GOOGLE_API_KEY)
            
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    client.models.generate_content,
                    model="gemini-2.5-flash",
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction="You are a senior Indian attorney with 25+ years of experience in criminal, civil, and corporate law. You specialize in IPC, CrPC, Indian Contract Act 1872, and landmark Supreme Court & High Court judgements. Always cite exact sections and relevant case precedents. Be precise, structured, and formal in legal drafting. When simplifying, use plain Indian English without losing legal accuracy."
                    )
                ),
                timeout=45
            )
            
            return response.text
            
        except asyncio.TimeoutError:
            if attempt == max_retries - 1:
                raise HTTPException(status_code=504, detail="AI analysis timed out. Please try again.")
        except Exception as e:
            error_str = str(e)
            
            if "503" in error_str or "429" in error_str or "UNAVAILABLE" in error_str or "high demand" in error_str.lower():
                if attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                else:
                    raise HTTPException(status_code=503, detail="The AI model is currently experiencing high demand. Please try again in a few minutes.")
            
            logger.error(f"❌ AI analysis error: {error_str}", exc_info=True)
            
            if "Budget" in error_str or "quota" in error_str.lower():
                raise HTTPException(status_code=402, detail="AI budget exceeded. Please check your API quota.")
            
            if "API key" in error_str or "authentication" in error_str.lower():
                raise HTTPException(status_code=401, detail="Google API key configuration error. Check your credentials.")
            
            raise HTTPException(status_code=500, detail=f"AI analysis failed: {error_str}")
