from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from gemini_service import GeminiService
from theirstack_service import TheirStackJobSearchService  # Updated import
from typing import Optional, List, Dict, Any
import os

app = FastAPI(
    title="Gemini Chatbot API with TheirStack Integration for NextHorizon",
    description="A chatbot API using Google's Gemini AI, enhanced with job data from TheirStack for NextHorizon",
    version="0.6.0"  # Updated version
)

# Initialize services
gemini_service = GeminiService(config_filepath="config.yaml")
theirstack_job_service = TheirStackJobSearchService(config_filepath="config.yaml")  # Updated instantiation

# --- Data Models ---

# Input data model for basic chat (with chat_id)
class ChatPromptRequest(BaseModel):
    chat_id: str
    prompt: str

# Error model
class ErrorResponse(BaseModel):
    detail: str

# --- API Endpoints ---

@app.get("/")
async def root():
    """
    Simple root endpoint to verify that the API is running.
    """
    return {"message": "Welcome to the theirStack Job Search API! Use /jobs/search to find jobs."}

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

@app.get("/jobs/search")
async def jobs_search_endpoint(
    page: int = Query(0, description="Page index (0-based)."),
    limit: int = Query(7, description="Number of results per page."),
    posted_at_max_age_days: int = Query(14, description="Max age of job postings in days."),
    order_desc: bool = Query(True, description="Sort descending if True."),
    order_field: str = Query("date_posted", description="Field to sort on."),
    blur_company_data: bool = Query(False, description="Obfuscate company details."),
    include_total_results: bool = Query(False, description="Include total result count."),
    job_title_search: Optional[str] = Query(None, description="Search by job title."),
    job_description_search: Optional[str] = Query(None, description="Search by job description."),
    job_company_name_search: Optional[str] = Query(None, description="Search by company name."),
    job_location_search: Optional[str] = Query(None, description="Search by job location."),
    job_country_code_or: Optional[List[str]] = Query(["CA"], description="List of country codes (e.g., CA, US)."),
    job_category_ids_or: Optional[List[str]] = Query(None, description="Filter by job category IDs."),
    job_type_ids_or: Optional[List[str]] = Query(None, description="Filter by job type IDs."),
    job_tag_ids_or: Optional[List[str]] = Query(None, description="Filter by job tag IDs."),
    job_must_not_have_tag_ids: Optional[List[str]] = Query(None, description="Exclude jobs with these tag IDs."),
    job_must_have_tag_ids: Optional[List[str]] = Query(None, description="Include only jobs with these tag IDs."),
    job_location_radius_miles: Optional[int] = Query(None, description="Radius for location-based search (in miles)."),
):
    """
    GET endpoint for job search.

    Accepts search parameters as query parameters, uses the service function to
    fetch results from theirStack's API, and returns the search results.
    """
    try:
        results = await theirstack_job_service.search_jobs(  # Call the method on the instance
            page=page,
            limit=limit,
            posted_at_max_age_days=posted_at_max_age_days,
            order_desc=order_desc,
            order_field=order_field,
            blur_company_data=blur_company_data,
            include_total_results=include_total_results,
            job_title_search=job_title_search,
            job_description_search=job_description_search,
            job_company_name_search=job_company_name_search,
            job_location_search=job_location_search,
            job_country_code_or=job_country_code_or,
            job_category_ids_or=job_category_ids_or,
            job_type_ids_or=job_type_ids_or,
            job_tag_ids_or=job_tag_ids_or,
            job_must_not_have_tag_ids=job_must_not_have_tag_ids,
            job_must_have_tag_ids=job_must_have_tag_ids,
            job_location_radius_miles=job_location_radius_miles
        )
        return results
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc))