from typing import Optional, List, Dict, Any
import httpx
import yaml
import logging

# Configure logging
logger = logging.getLogger(__name__)

class TheirStackJobSearchService:
    def __init__(self, config_filepath: str = "config.yaml"):
        self.config = self.load_config(config_filepath)
        self.api_key = self.config["theirstack"]["api_key"]
        self.base_url = "https://api.theirstack.com/v1/jobs/search"  # Moved base URL here
        if not self.api_key:
            raise ValueError("Missing theirstack api_key in config file.")

    def load_config(self, filepath: str) -> Dict:
        """Loads configuration from a YAML file."""
        try:
            with open(filepath, "r") as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            logger.exception(f"Error: Config file not found at {filepath}")
            raise
        except yaml.YAMLError as e:
            logger.exception(f"Error parsing config file: {e}")
            raise

    async def search_jobs(
        self,
        page: int = 0,
        limit: int = 5,
        posted_at_max_age_days: int = 14,
        order_desc: bool = True,
        order_field: str = "date_posted",
        blur_company_data: bool = False,
        include_total_results: bool = False,
        job_title_search: Optional[str] = None,
        job_description_search: Optional[str] = None,
        job_company_name_search: Optional[str] = None,
        job_location_search: Optional[str] = None,
        job_country_code_or: Optional[List[str]] = ["CA"],
        job_category_ids_or: Optional[List[str]] = None,
        job_type_ids_or: Optional[List[str]] = None,
        job_tag_ids_or: Optional[List[str]] = None,
        job_must_not_have_tag_ids: Optional[List[str]] = None,
        job_must_have_tag_ids: Optional[List[str]] = None,
        job_location_radius_miles: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Service function to search jobs via theirStack API

        Args:
            Various job search parameters as per theirStack API requirements

        Returns:
            dict: Job search results
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
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.base_url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.RequestError as exc:
            logger.exception(f"Request error: {exc}")
            raise RuntimeError(f"Request error: {exc}") from exc
        except httpx.HTTPStatusError as exc:
            logger.exception(f"HTTP error: {exc.response.text}")
            raise RuntimeError(f"HTTP error: {exc.response.text}") from exc