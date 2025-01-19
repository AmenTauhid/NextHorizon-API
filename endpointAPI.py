from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx

# Import the Gemini service
from genAIService import generate_text
from JobBoardService import JobSearchRequest, search_jobs_service


app = FastAPI(
    title="NextHorizon API",
    description="An API to interact with Google's Gemini AI",
    version="0.1.0"
)

@app.get("/jobs")
async def search_jobs( page: int = Query(0, description="Page number of results"), limit: int = Query(10, description="Number of results per page"), max_age_days: int = Query(14, description="Max age of job postings in days"), country_code: str = Query("CA", description="Country code for job search"), keyword: str = Query(None, description="Keyword for job search") ):
    # Build the request payload using your separate Pydantic model
    search_request = JobSearchRequest(
        page=page,
        limit=limit,
        posted_at_max_age_days=max_age_days,
        job_country_code_or=[country_code],
        job_title_search=keyword
    )
    
    try:
        # Call the service function
        result = await search_jobs_service(search_request)
        return result
    except httpx.RequestError as exc:
    # Covers any error with making the request (network issues, etc.)
        raise HTTPException(
        status_code=500,
        detail=f"An error occurred while making the request: {exc}"
    )
    except httpx.HTTPStatusError as exc:
    # Covers non-200 responses
        raise HTTPException(
        status_code=exc.response.status_code,
        detail=f"Error response from API: {exc.response.json()}"
    )

@app.get("/")
async def root():
    return {"message": "Welcome to the Nexthorizan Job API! Use /jobs to search for jobs."}

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
    


    