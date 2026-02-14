"""
Job Fetcher - Gets job listings from JSearch API
"""
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()


def fetch_jobs_from_api(query="Data Analyst", location="Remote", num_jobs=20):
    """
    Fetch jobs from the JSearch API based on search criteria
    """
    url = "https://jsearch.p.rapidapi.com/search"
    
    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
    }
    
    # JSearch API returns 10 jobs per page, so we need to calculate pages
    pages_needed = num_jobs // 10
    
    all_jobs = []
    
    for page_num in range(1, pages_needed + 1):
        search_params = {
            "query": query + " in " + location,
            "page": str(page_num),
            "num_pages": "1"
        }
        
        try:
            print("Fetching page " + str(page_num) + "...")
            api_response = requests.get(url, headers=headers, params=search_params, timeout=10)
            api_response.raise_for_status()
            
            response_data = api_response.json()
            job_listings = response_data.get('data', [])
            
            if job_listings:
                all_jobs.extend(job_listings)
                print("Got " + str(len(job_listings)) + " jobs")
            else:
                print("No more jobs found")
                break
                
        except Exception as error:
            print("Error: " + str(error))
            break
    
    if len(all_jobs) == 0:
        print("Couldn't find any jobs")
        return pd.DataFrame()
    
    # Process the job data into a clean format
    processed_jobs = []
    for job in all_jobs:
        city = job.get('job_city') or ''
        country = job.get('job_country') or ''
        full_location = city + ', ' + country if city else country
        
        job_data = {
            'job_id': job.get('job_id', ''),
            'job_title': job.get('job_title', ''),
            'company': job.get('employer_name', ''),
            'location': full_location,
            'description': job.get('job_description', ''),
            'job_url': job.get('job_apply_link', ''),
            'posted_date': job.get('job_posted_at_datetime_utc', ''),
        }
        processed_jobs.append(job_data)
    
    df = pd.DataFrame(processed_jobs)
    print("Total jobs collected: " + str(len(df)))
    
    # Return only the number of jobs requested
    return df.head(num_jobs)


def save_jobs_to_csv(df, filepath='data/jobs.csv'):

    try:
        df.to_csv(filepath, index=False)
        print("Successfully saved " + str(len(df)) + " jobs to " + filepath)
        return True
    except Exception as error:
        print("Couldn't save file: " + str(error))
        return False


def load_jobs_from_csv(filepath='data/jobs.csv'):
    """Load jobs from a CSV file"""
    try:
        df = pd.read_csv(filepath)
        print("Loaded " + str(len(df)) + " jobs from file")
        return df
    except FileNotFoundError:
        print("File doesn't exist: " + filepath)
        return pd.DataFrame()
    except Exception as error:
        print("Error reading file: " + str(error))
        return pd.DataFrame()


if __name__ == "__main__":
    print("Testing the JSearch API connection")
    print("")
    
    # Try fetching 5 jobs as a test
    test_jobs = fetch_jobs_from_api(query="Data Analyst", location="Remote", num_jobs=5)
    
    if not test_jobs.empty:
        print("Here's the first job we found:")
        first_job = test_jobs.iloc[0]
        print("Job Title: " + first_job['job_title'])
        print("Company: " + first_job['company'])
        print("Location: " + first_job['location'])
        
        save_jobs_to_csv(test_jobs)
    else:
        print("Test failed - check your API key in the .env file")