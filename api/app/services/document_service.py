import base64
from io import BytesIO
from PIL import Image
import PyPDF2
import pytesseract
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF"""
    try:
        pdf_file = BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"PDF extraction error: {str(e)}")
        return ""

def extract_text_from_image(image_base64: str) -> str:
    """Extract text from image using OCR"""
    try:
        if 'base64,' in image_base64:
            image_base64 = image_base64.split('base64,')[1]
        
        image_data = base64.b64decode(image_base64)
        image = Image.open(BytesIO(image_data))
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        logger.error(f"Image OCR error: {str(e)}")
        return ""
