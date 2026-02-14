
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.job_fetcher import fetch_jobs_from_api, save_jobs_to_csv, load_jobs_from_csv
from utils.keyword_extractor import extract_keywords, calculate_match_score
from utils.pdf_parser import extract_text_from_pdf, clean_text
import pandas as pd
import json


# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def fetch_and_save_jobs(**context):
    # Get parameters from DAG run config or use defaults
    query = context['dag_run'].conf.get('query', 'Data Analyst')
    location = context['dag_run'].conf.get('location', 'Remote')
    num_jobs = context['dag_run'].conf.get('num_jobs', 20)
    
    print("Fetching jobs:", query, "in", location, "limit:", num_jobs)
    
    jobs_df = fetch_jobs_from_api(query=query, location=location, num_jobs=num_jobs)
    
    if jobs_df.empty:
        raise ValueError("No jobs fetched from API")
    
    save_jobs_to_csv(jobs_df)
    print("Successfully fetched", len(jobs_df), "jobs")
    
    return len(jobs_df)


def extract_job_keywords(**context):
    jobs_df = load_jobs_from_csv()
    
    if jobs_df.empty:
        raise ValueError("No jobs found in CSV")
    
    # Extract keywords for each job
    jobs_df['keywords'] = jobs_df['description'].apply(
        lambda desc: list(extract_keywords(desc)) if pd.notna(desc) else []
    )
    
    # Save updated dataframe
    save_jobs_to_csv(jobs_df)
    print("Extracted keywords for", len(jobs_df), "jobs")
    
    return len(jobs_df)


def process_resume(**context):
    resume_path = 'data/resume.pdf'
    
    if not os.path.exists(resume_path):
        raise FileNotFoundError("Resume not found)
    
    # Extract text from PDF
    text = extract_text_from_pdf(resume_path)
    cleaned_text = clean_text(text)
    
    if not cleaned_text:
        raise ValueError("Could not extract text from resume")
    
    # Extract keywords
    resume_keywords = extract_keywords(cleaned_text)
    
    print("Extracted", len(resume_keywords), "keywords from resume")
    print("Keywords:", resume_keywords)
    
    # Push to XCom for next task
    context['task_instance'].xcom_push(key='resume_keywords', value=list(resume_keywords))
    
    return len(resume_keywords)


def calculate_matches(**context):
    # Get resume keywords from previous task
    resume_keywords = set(context['task_instance'].xcom_pull(
        task_ids='process_resume', 
        key='resume_keywords'
    ))
    
    # Load jobs with keywords
    jobs_df = load_jobs_from_csv()
    
    if jobs_df.empty:
        raise ValueError("No jobs found")
    
    # Calculate match score for each job
    results = []
    
    for idx, row in jobs_df.iterrows():
        job_keywords = set(row.get('keywords', []))
        
        if isinstance(row.get('keywords'), str):
            # Handle case where keywords might be stored as string
            import ast
            try:
                job_keywords = set(ast.literal_eval(row['keywords']))
            except:
                job_keywords = set()
        
        score, matched, missing = calculate_match_score(resume_keywords, job_keywords)
        
        results.append({
            'rank': 0,
            'job_title': row['job_title'],
            'company': row['company'],
            'location': row['location'],
            'match_score': score,
            'matched_keywords': list(matched),
            'missing_keywords': list(missing),
            'job_url': row['job_url'],
            'description': row['description'][:500]
        })
    
    # Sort by match score
    results.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Add ranks
    for idx, result in enumerate(results, 1):
        result['rank'] = idx
    
    # Save results to JSON
    results_path = 'data/results.json'
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("Calculated matches for", len(results), "jobs")
    print("Top match:", results[0]['job_title'], "with score", results[0]['match_score'], "%")
    
    return len(results)


# Define the DAG
with DAG(
    'job_matcher_pipeline',
    default_args=default_args,
    description='Job matching pipeline with resume ATS scoring',
    schedule_interval=None, 
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['job-matching', 'ats'],
) as dag:
    
    # Task 1: Fetch jobs
    task_fetch_jobs = PythonOperator(
        task_id='fetch_jobs',
        python_callable=fetch_and_save_jobs,
    )
    
    # Task 2: Extract keywords from jobs
    task_extract_job_keywords = PythonOperator(
        task_id='extract_job_keywords',
        python_callable=extract_job_keywords,
    )
    
    # Task 3: Process resume
    task_process_resume = PythonOperator(
        task_id='process_resume',
        python_callable=process_resume,
    )
    
    # Task 4: Calculate matches
    task_calculate_matches = PythonOperator(
        task_id='calculate_matches',
        python_callable=calculate_matches,
    )
    
    # Define task dependencies
    task_fetch_jobs >> task_extract_job_keywords >> task_process_resume >> task_calculate_matches