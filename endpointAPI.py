from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

# Import the Gemini service
from genAIService import generate_text
from JobBoardService import JobSearchRequest, search_jobs_service 


app = FastAPI(
    title="Gemini API",
    description="An API to interact with Google's Gemini AI",
    version="0.1.0"
)
@app.get("/jobs")
async def search_jobs(
    page: int = Query(0, description="Page number of results"),
    limit: int = Query(10, description="Number of results per page"),
    max_age_days: int = Query(14, description="Max age of job postings in days"),
    country_code: str = Query("CA", description="Country code for job search"),
    keyword: str = Query(None, description="Keyword for job search")
):

# Build the request payload using your separate Pydantic model
    search_request = JobSearchRequest(
        page=page,
        limit=limit,
        posted_at_max_age_days=max_age_days,
        job_country_code_or=[country_code],
        job_title_search=keyword
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