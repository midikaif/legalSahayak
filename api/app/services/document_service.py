import logging
from app.services.pdf_client import extract_text_from_pdf_worker, extract_text_from_image_worker

logger = logging.getLogger(__name__)

async def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF by delegating to PDF-Worker"""
    try:
        return await extract_text_from_pdf_worker(file_content)
    except Exception as e:
        logger.error(f"PDF extraction error (delegated): {str(e)}")
        return ""

async def extract_text_from_image(image_base64: str) -> str:
    """Extract text from image by delegating to PDF-Worker"""
    try:
        return await extract_text_from_image_worker(image_base64)
    except Exception as e:
        logger.error(f"Image OCR error (delegated): {str(e)}")
        return ""
