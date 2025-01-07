from pydantic import BaseModel


class DetectSmellResponse(BaseModel):
    """
    Schema for the AI-based code smell detection response.
    """

    code_snippet: str
    analysis: str
    label: str

    class Config:
        schema_extra = {
            "example": {
                "code_snippet":
                "def example_function():\n    print('Hello, world!')",
                "analysis":
                "The code is overly simple and lacks exception handling.",
                "label": "Code Simplicity",
            }
        }
