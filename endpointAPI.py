from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Import the Gemini service
from genAIService import generate_text

app = FastAPI(
    title="Gemini API",
    description="An API to interact with Google's Gemini AI",
    version="0.1.0"
)

# Input data model
class PromptRequest(BaseModel):
    prompt: str

# Error model
class ErrorResponse(BaseModel):
    detail: str

@app.post("/generate", response_model=str, responses={500: {"model": ErrorResponse}})
async def generate_content(request: PromptRequest):
    """
    Generates content using Gemini based on the provided prompt.
    """
    try:
        generated_text = generate_text(request.prompt)
        return generated_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {e}")