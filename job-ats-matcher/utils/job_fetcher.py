"""
Job Fetcher - Fetches jobs from JSearch API
"""
import requests
import pandas as pd
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_jobs_from_api(query="Data Analyst", location="Remote", num_jobs=20):
    """
    Fetch jobs from JSearch API
    
    Args:
        query: Job search query
        location: Location filter
        num_jobs: Number of jobs to fetch (max 10 per page)
    
    Returns:
        DataFrame with job data
    """
    url = "https://jsearch.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": os.getenv("RAPIDAPI_HOST", "jsearch.p.rapidapi.com")
    }
    
    # Calculate number of pages needed (API returns max 10 per page)
    num_pages = (num_jobs + 9) // 10  # Round up
    
    all_jobs = []
    
    for page in range(1, num_pages + 1):
        querystring = {
            "query": f"{query} in {location}",
            "page": str(page),
            "num_pages": "1"
        }
        
        try:
            logger.info(f"Fetching page {page}...")
            response = requests.get(url, headers=headers, params=querystring, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            jobs = data.get('data', [])
            
            if not jobs:
                logger.warning(f"No jobs found on page {page}")
                break
            
            all_jobs.extend(jobs)
            logger.info(f"Fetched {len(jobs)} jobs from page {page}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            break
        except Exception as e:
            logger.error(f"Error processing response: {e}")
            break
    
    if not all_jobs:
        logger.warning("No jobs fetched, returning empty DataFrame")
        return pd.DataFrame()
    
    # Convert to DataFrame with relevant fields
    jobs_df = pd.DataFrame([
        {
            'job_id': job.get('job_id', ''),
            'job_title': job.get('job_title', ''),
            'company': job.get('employer_name', ''),
            'location': f"{job.get('job_city') or ''}, {job.get('job_country') or ''}".strip(', '),
            'description': job.get('job_description', ''),
            'job_url': job.get('job_apply_link', ''),
            'posted_date': job.get('job_posted_at_datetime_utc', ''),
        }
        for job in all_jobs
    ])
    
    logger.info(f"Total jobs fetched: {len(jobs_df)}")
    return jobs_df[:num_jobs]  # Limit to requested number


def save_jobs_to_csv(df, filepath='data/jobs.csv'):
    """Save jobs DataFrame to CSV"""
    try:
        df.to_csv(filepath, index=False)
        logger.info(f"Saved {len(df)} jobs to {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error saving to CSV: {e}")
        return False


def load_jobs_from_csv(filepath='data/jobs.csv'):
    """Load jobs from CSV"""
    try:
        df = pd.read_csv(filepath)
        logger.info(f"Loaded {len(df)} jobs from {filepath}")
        return df
    except FileNotFoundError:
        logger.warning(f"File not found: {filepath}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error loading CSV: {e}")
        return pd.DataFrame()


if __name__ == "__main__":
    # Test the API
    print("Testing JSearch API...")
    jobs_df = fetch_jobs_from_api(query="Data Analyst", location="Remote", num_jobs=5)
    
    if not jobs_df.empty:
        print(f"\nFetched {len(jobs_df)} jobs!")
        print("\nFirst job:")
        print(jobs_df.iloc[0])
        
        # Test saving
        save_jobs_to_csv(jobs_df)
    else:
        print("Failed to fetch jobs. Check your API key in .env")