import httpx
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# API configuration
API_URL = "https://api.theirstack.com/v1/jobs/search"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzeWVkaDc0NkBnbWFpbC5jb20iLCJwZXJtaXNzaW9ucyI6InVzZXIifQ.cJtZSwPE-3i9haqTB45BZ4tmU8Jg0UXypUgjHysiDY0"

# Request body model for the job search
class JobSearchRequest(BaseModel):
    page: int = 0
    limit: int = 10
    posted_at_max_age_days: int = 14
    order_by: List[Dict[str, Any]] = [{"desc": True, "field": "date_posted"}]
    job_country_code_or: List[str] = ["CA"]
    include_total_results: bool = False
    blur_company_data: bool = False
    job_title_search: Optional[str] = None

async def search_jobs_service(search_params: JobSearchRequest) -> dict:

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, json=search_params.dict(), headers=headers)
        response.raise_for_status()
        return response.json()
