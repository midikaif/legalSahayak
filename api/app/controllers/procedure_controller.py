from app.services.ai_service import get_ai_analysis

async def get_legal_procedure(case_type: str):
    procedure_prompt = f"""Provide a detailed step-by-step legal procedure for a {case_type} case in India.

Write in an engaging, easy-to-understand way. Use **bold** for important terms.

Respond ONLY with valid JSON (no markdown code blocks) with these exact keys:
{{
  "steps": [
    {{"step_number": 1, "description": "Step description with **bold** key terms", "timeline": "1-2 weeks"}},
    {{"step_number": 2, "description": "Next step...", "timeline": "2-4 weeks"}}
  ],
  "required_documents": ["Document 1", "Document 2"],
  "court_hierarchy": ["Court 1 handles X", "Court 2 handles Y"],
  "estimated_timeline": "6 months to 2 years overall",
  "important_acts": ["Act 1 - what it covers", "Act 2"]
}}"""
    
    procedure_result = await get_ai_analysis(procedure_prompt)
    
    return {
        "case_type": case_type,
        "procedure": procedure_result
    }
