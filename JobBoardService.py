from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import httpx

app = FastAPI()

# API configuration
API_URL = "https://api.theirstack.com/v1/jobs/search"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzeWVkaDc0NkBnbWFpbC5jb20iLCJwZXJtaXNzaW9ucyI6InVzZXIifQ.cJtZSwPE-3i9haqTB45BZ4tmU8Jg0UXypUgjHysiDY0"
# Request body model
class JobSearchRequest(BaseModel):
    page: int = 0
    limit: int = 10
    posted_at_max_age_days: int = 14
    order_by: list[dict] = [{"desc": True, "field": "date_posted"}]
    job_country_code_or: list[str] = ["CA"]
    include_total_results: bool = False
    blur_company_data: bool = False

@app.get("/jobs")
async def search_jobs(
    page: int = Query(0, description="Page number of results"),
    limit: int = Query(10, description="Number of results per page"),
    max_age_days: int = Query(14, description="Max age of job postings in days"),
    country_code: str = Query("CA", description="Country code for job search"),
    keyword: str = Query(None, description="Keyword for job search")
):
    """
    Search for jobs using the external API.
    """
    payload = {
        "page": page,
        "limit": limit,
        "posted_at_max_age_days": max_age_days,
        "order_by": [
            {"desc": True, "field": "date_posted"}
        ],
        "job_country_code_or": [country_code],
        "include_total_results": False,
        "blur_company_data": False
    }

    if keyword:
        payload["job_title_search"] = keyword

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(API_URL, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"An error occurred while making the request: {e}")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=f"Error response: {response.json()}")

@app.get("/")
async def root():
    return {"message": "Welcome to the Nexthorizan Job API! Use /jobs to search for jobs."}