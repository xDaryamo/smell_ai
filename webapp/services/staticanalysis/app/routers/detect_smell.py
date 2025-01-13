from fastapi import APIRouter, HTTPException
# when running locally/testing
# from webapp.services.staticanalysis.app.schemas.requests import (
#   DetectSmellRequest,
# )
# from webapp.services.staticanalysis.app.schemas.responses import (
#   DetectSmellStaticResponse,
# )
# from webapp.services.staticanalysis.app.utils.static_analysis import (
#   detect_static,
# )

# when deploying in docker
from app.schemas.requests import (
    DetectSmellRequest,
)
from app.schemas.responses import (
    DetectSmellStaticResponse,
)
from app.utils.static_analysis import (
    detect_static,
)


router = APIRouter()


@router.post("/detect_smell_static", response_model=DetectSmellStaticResponse)
async def detect_smell_static(payload: DetectSmellRequest):
    code_snippet = payload.code_snippet
    if not code_snippet:
        raise HTTPException(
            status_code=400, detail="Code snippet cannot be empty."
        )

    analysis_result = detect_static(code_snippet)
    return DetectSmellStaticResponse(smells=analysis_result["response"])
