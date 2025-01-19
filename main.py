from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from gemini_service import GeminiService
import os

app = FastAPI(
    title="Gemini Chatbot API",
    description="A chatbot API using Google's Gemini AI with in-memory context handling",
    version="0.1.0"
)

# Initialize GeminiService (with in-memory context)
gemini_service = GeminiService()

# Input data model (with chat_id)
class ChatPromptRequest(BaseModel):
    chat_id: str
    prompt: str

# Error model
class ErrorResponse(BaseModel):
    detail: str

@app.get("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"

@app.post("/generate", response_model=str, responses={500: {"model": ErrorResponse}})
async def generate_content(request: ChatPromptRequest):
    """
    Generates a conversational response using Gemini (with in-memory context).
    """
    try:
        generated_text = gemini_service.generate_response(request.chat_id, request.prompt)
        return generated_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {e}")