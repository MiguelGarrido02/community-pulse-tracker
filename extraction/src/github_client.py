import os
import requests
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
import pandas as pd

# Load environment variables (secrets)
load_dotenv()

class GitHubClient:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com"

    def fetch_issues(self, owner: str, repo: str, start_date: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetches issues from a GitHub repo incrementally.
        
        Args:
            owner: Repository owner (e.g., 'pandas-dev').
            repo: Repository name (e.g., 'pandas').
            start_date: 'YYYY-MM-DD' string. If None, defaults to trailing 24h (Delta Load).
        
        Returns:
            List of dictionaries containing issue data (Raw JSON).
        """
        
        # Default to 'yesterday' for daily automated runs if no date provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        
        # GitHub API requires ISO 8601 format with timestamp
        start_iso = f"{start_date}T00:00:00Z"

        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {
            "since": start_iso,
            "state": "all",      # Include open and closed issues
            "per_page": 100,     # Max allowed per page to minimize API calls
            "page": 1
        }

        all_issues = []
        print(f"Fetching {owner}/{repo} issues since {start_iso}...")

        while True:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status() 
            
            data = response.json()

            if not data:
                break

            all_issues.extend(data)
            print(f"   -> Page {params['page']}: {len(data)} items retrieved.")

            # Optimization: If page is not full, end of data reached
            if len(data) < 100:
                break   

            params['page'] += 1
            
        print(f"Total fetched: {len(all_issues)} issues.")
        return all_issues

if __name__ == "__main__":    
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN not found in .env")

    client = GitHubClient(token)
    
    # TEST 1: Historical Backfill Simulation (Explicit Date)
    print("--- TEST: Historical Load ---")
    issues = client.fetch_issues("pandas-dev", "pandas", start_date="2025-12-01")
    
    # TEST 2: Daily Incremental Simulation (No Date = Last 24h)
    #print("--- TEST: Daily Incremental Load ---")
    # Using a high-velocity repo like 'flutter' ensures we find data from today
    #issues = client.fetch_issues("flutter", "flutter") 
    
    if issues:
        df = pd.DataFrame(issues)
        print(f"\nPreview:\n{df[['title', 'created_at']].head()}")