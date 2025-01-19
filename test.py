from fastapi import FastAPI, HTTPException, Query
from typing import Optional, List, Dict, Any
import httpx

# ===== Replace with your actual theirStack API key =====
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzeWVkaDc0NkBnbWFpbC5jb20iLCJwZXJtaXNzaW9ucyI6InVzZXIifQ.cJtZSwPE-3i9haqTB45BZ4tmU8Jg0UXypUgjHysiDY0"
API_URL = "https://api.theirstack.com/v1/jobs/search"

app = FastAPI()

@app.get("/")
async def root():
    """
    Simple root endpoint to verify that the API is running.
    """
    return {"message": "Welcome to the theirStack Job Search API! Use /jobs/search to find jobs."}

@app.get("/jobs/search")
async def search_jobs(
    page: int = Query(0, description="Page index (0-based)."),
    limit: int = Query(10, description="Number of results per page."),
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
    
    Accepts search parameters as query parameters, constructs a payload, forwards the request to theirStack's API,
    and returns the search results.

    **Example Request:**
    ```
    GET /jobs/search?job_title_search=Developer&job_location_search=Toronto&limit=5
    ```
    """
    # Build the payload as per theirStack API requirements
    payload: Dict[str, Any] = {
        "page": page,
        "limit": limit,
        "posted_at_max_age_days": posted_at_max_age_days,
        "order_by": [{"desc": order_desc, "field": order_field}],
        "blur_company_data": blur_company_data,
        "include_total_results": include_total_results,
        "job_country_code_or": job_country_code_or,
    }

    # Conditionally add optional parameters if they are provided
    if job_title_search:
        payload["job_title_search"] = job_title_search
    if job_description_search:
        payload["job_description_search"] = job_description_search
    if job_company_name_search:
        payload["job_company_name_search"] = job_company_name_search
    if job_location_search:
        payload["job_location_search"] = job_location_search
    if job_category_ids_or:
        payload["job_category_ids_or"] = job_category_ids_or
    if job_type_ids_or:
        payload["job_type_ids_or"] = job_type_ids_or
    if job_tag_ids_or:
        payload["job_tag_ids_or"] = job_tag_ids_or
    if job_must_not_have_tag_ids:
        payload["job_must_not_have_tag_ids"] = job_must_not_have_tag_ids
    if job_must_have_tag_ids:
        payload["job_must_have_tag_ids"] = job_must_have_tag_ids
    if job_location_radius_miles is not None:
        payload["job_location_radius_miles"] = job_location_radius_miles

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
            return response.json()
    except httpx.RequestError as exc:
        # Handle network or connection errors
        raise HTTPException(status_code=500, detail=f"Request error: {exc}") from exc
    except httpx.HTTPStatusError as exc:
        # Handle HTTP errors returned by theirStack API
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text) from exc
