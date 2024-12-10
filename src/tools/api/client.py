from typing import Optional
import os
import requests
from functools import lru_cache

class FinancialDatasetsClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FINANCIAL_DATASETS_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided")
        
        self.base_url = "https://api.financialdatasets.ai"
        self.session = self._init_session()
    
    def _init_session(self) -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        })
        return session

    @lru_cache(maxsize=100)
    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make GET request to API with caching"""
        response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

client = FinancialDatasetsClient() 