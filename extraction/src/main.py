import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from github_client import GitHubClient
from snowflake_loader import SnowflakeLoader

# Load environment variables
load_dotenv()

# Repos to track
# Format: (owner, repo)
REPOS_TO_TRACK = [
    ("pandas-dev", "pandas"),
    ("PrefectHQ", "prefect"),
    ("dbt-labs", "dbt-core"),
    ("streamlit", "streamlit"),
]

def run_pipeline():
    """
    Extraction and Loading pipeline:
    1. Setup GitHub and Snowflake clients
    2. Determine time window (Backfill vs Incremental)
    3. For each repo:
        A. Extract issues from GitHub
        B. Load issues into Snowflake
    4. Log summary
    """
    
    # Set up
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN not found in .env.")
        sys.exit(1)

    try:
        gh_client = GitHubClient(token)
        sn_loader = SnowflakeLoader()
    except Exception as e:
        print(f"Error initializing clients: {e}")
        sys.exit(1)

    # Determine time window
    # If FORCE_START_DATE exists, use it (HISTORICAL).
    # Otherwise, default to None (Client calculates "yesterday" automatically).
    force_date = os.getenv("FORCE_START_DATE")
    
    if force_date:
        print(f"HISTORICAL MODE ACTIVATED: Downloading from {force_date}")
    else:
        print(f"DAILY MODE: Downloading last 24h")

    # main loop
    total_issues = 0
    
    for owner, repo in REPOS_TO_TRACK:
        try:
            print(f"\n--- Processing: {owner}/{repo} ---")
            
            # Extract
            issues = gh_client.fetch_issues(owner, repo, start_date=force_date)
            
            if not issues:
                print(f"No issues found for {repo}.")
                continue
                
            # Load
            sn_loader.load_data(issues)
            total_issues += len(issues)
            
        except Exception as e:
            print(f"Failed to process {repo}: {e}")
            print("Continuing to next repository...\n")
            continue

    print("\n      --- PIPELINE COMPLETED ---")
    print(f"\nTotal issues processed: {total_issues}")

if __name__ == "__main__":
    run_pipeline()