import ast
import asyncio
import logging
from fastapi import APIRouter, HTTPException
from app.schemas.requests import DetectSmellRequest
from app.schemas.responses import DetectSmellResponse
from app.utils.model import Model


router = APIRouter()

# Initialize the AI model instance
model_instance = Model()
# model_instance.load_fine_tuned_model()

logger = logging.getLogger("ModelLoader")
logging.basicConfig(level=logging.INFO)


async def async_detect_code_smell(code_snippet: str) -> dict:
    """
    Asynchronous detection of code smells.
    """
    return await asyncio.to_thread(
        model_instance.detect_code_smell,
        code_snippet,
    )


@router.post("/detect_smell_ai", response_model=DetectSmellResponse)
async def detect_smell_ai(payload: DetectSmellRequest):
    """
    Endpoint for detecting code smells using AI-based analysis.
    """
    code_snippet = payload.code_snippet
    if not code_snippet:
        raise HTTPException(
            status_code=400, detail="Code snippet cannot be empty."
        )

    if not validate_code_snippet(code_snippet):
        raise HTTPException(
            status_code=400,
            detail="Invalid Python syntax in the code snippet.",
        )

    # Perform AI-based analysis
    analysis_result = await async_detect_code_smell(code_snippet)

    if not analysis_result["success"]:
        raise HTTPException(
            status_code=500,
            detail=f"Error during AI analysis: {analysis_result['message']}",
        )

    return DetectSmellResponse(
        code_snippet=code_snippet,
        analysis=analysis_result["analysis"],
        label=analysis_result["label"],
    )


def validate_code_snippet(code_snippet: str) -> bool:
    """
    Validate the input code snippet for syntax correctness.
    """
    try:
        ast.parse(code_snippet)
        return True
    except SyntaxError as e:
        logger.error(f"Syntax error in the code snippet: {e}")
        return False
