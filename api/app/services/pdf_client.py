import httpx
import os
import base64

PDF_WORKER_URL = os.getenv("PDF_WORKER_URL", "http://localhost:8001")

async def call_pdf_worker(html: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PDF_WORKER_URL}/generate-pdf",
            json={"html_content": html},
            timeout=30.0
        )
        if response.status_code == 200:
            return response.json().get("pdf_base64")
        raise Exception(f"PDF worker error: {response.status_code} - {response.text}")

async def call_draft_pdf_worker(content: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PDF_WORKER_URL}/generate-draft-pdf",
            json={"content": content},
            timeout=30.0
        )
        if response.status_code == 200:
            return response.json().get("pdf_base64")
        raise Exception(f"Draft PDF worker error: {response.status_code} - {response.text}")

async def extract_text_from_pdf_worker(file_content: bytes) -> str:
    pdf_base64 = base64.b64encode(file_content).decode('utf-8')
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PDF_WORKER_URL}/extract-text",
            json={"pdf_base64": pdf_base64},
            timeout=30.0
        )
        if response.status_code == 200:
            return response.json().get("text", "")
        return ""

async def extract_text_from_image_worker(image_base64: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{PDF_WORKER_URL}/ocr",
            json={"image_base64": image_base64},
            timeout=30.0
        )
        if response.status_code == 200:
            return response.json().get("text", "")
        return ""