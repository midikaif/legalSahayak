from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import io
import base64
import logging
try:
    from xhtml2pdf import pisa
except ImportError:
    pisa = None
    logging.warning("xhtml2pdf not installed. PDF generation will be unavailable.")
from services.document_service import extract_text_from_pdf, extract_text_from_image
from services.draft_service import generate_formatted_draft_pdf
import os
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger("uvicorn.error")

# Register Devanagari Fonts Globally for xhtml2pdf and ReportLab
base_dir = os.path.dirname(os.path.abspath(__file__))
font_regular_path = os.path.join(base_dir, 'assets', 'fonts', 'Mukta-Regular.ttf')
font_bold_path = os.path.join(base_dir, 'assets', 'fonts', 'Mukta-Bold.ttf')

if os.path.exists(font_regular_path):
    pdfmetrics.registerFont(TTFont('Mukta', font_regular_path))
    pdfmetrics.registerFont(TTFont('Mukta-Bold', font_bold_path))
    logger.info("Mukta fonts registered globally for PDF generation.")
else:
    logger.error("Mukta fonts not found at " + font_regular_path)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BytesIO = io.BytesIO

class PDFRequest(BaseModel):
    html_content: str

class DraftPDFRequest(BaseModel):
    content: str

class OCRRequest(BaseModel):
    image_base64: str

class ExtractTextRequest(BaseModel):
    pdf_base64: str

import os

def link_callback(uri, rel):
    """Resolve local paths for xhtml2pdf"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if uri.startswith('/assets/') or uri.startswith('assets/'):
        path = os.path.join(base_dir, uri.lstrip('/'))
        path = os.path.normpath(path)
        if os.path.exists(path):
            return path
    return uri

@app.post("/generate-pdf")
async def generate_pdf(request: PDFRequest):
    if not pisa:
        raise HTTPException(status_code=501, detail="PDF generation with xhtml2pdf is not available on this server.")
    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(request.html_content, dest=pdf_buffer)

    logger.info(f"request.html_content: {request.html_content}")
    logger.info(f"xhtml2pdf status: {pisa_status}")
    logger.info(f"pisa_status.err: {pisa_status.err}")


    if pisa_status.err:
        logger.error(f"xhtml2pdf error: {pisa_status.err}")
        if hasattr(pisa_status, 'log'):
            for log_entry in pisa_status.log:
                logger.error(f"pisa log: {log_entry}")
        raise HTTPException(status_code=500, detail=f"PDF Generation Failed: {pisa_status.err}")
    logger.info(f"PDF generated successfully {pdf_buffer.getvalue()}")
    pdf_base64 = base64.b64encode(pdf_buffer.getvalue()).decode('utf-8')
    logger.info(f"PDF base64 encoded successfully {pdf_base64}")
    return {"pdf_base64": pdf_base64}

@app.post("/generate-draft-pdf")
async def generate_draft_pdf(request: DraftPDFRequest):
    pdf_bytes = generate_formatted_draft_pdf(request.content)
    if not pdf_bytes:
        raise HTTPException(status_code=500, detail="Draft PDF Generation Failed.")
    
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    return {"pdf_base64": pdf_base64}

@app.post("/ocr")
async def perform_ocr(request: OCRRequest):
    text = extract_text_from_image(request.image_base64)
    if not text:
        raise HTTPException(status_code=500, detail="OCR processing failed")
    return {"text": text}

@app.post("/extract-text")
async def extract_text(request: ExtractTextRequest):
    try:
        pdf_bytes = base64.b64decode(request.pdf_base64)
        text = extract_text_from_pdf(pdf_bytes)
        return {"text": text}
    except Exception as e:
        logger.error(f"Text extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Text extraction failed")