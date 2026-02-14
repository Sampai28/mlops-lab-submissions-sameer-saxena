# Job ATS Matcher

An MLOps pipeline that fetches job postings, analyzes resumes, and calculates ATS match scores using Docker, Airflow, and Streamlit.

## Overview

This project initially started with a static dataset from Kaggle ([Job Descriptions Dataset](https://www.kaggle.com/datasets/jayakishan225/job-descriptions-dataset)). However, to make the system more dynamic and practical, I integrated the JSearch API to fetch real-time job postings. This allows users to get fresh, current job listings instead of working with static historical data.

This system:
- Fetches real job postings from JSearch API
- Extracts keywords from job descriptions and resumes
- Calculates match scores (ATS scores)
- Shows ranked job matches in a web interface

**Technologies:** Docker, Apache Airflow, Streamlit, Python, Pandas

## Project Structure
```
job-ats-matcher/
├── dags/                   # Airflow pipeline
├── data/                   # Job data and results
├── streamlit/              # Web UI
├── utils/                  # Core logic (API, keywords, PDF parser)
├── docker-compose.yml      # Docker configuration
├── Dockerfile
├── requirements.txt
└── .env                    # API keys (create from .env.example)
```

## Setup & Installation

### 1. Get API Key
- Sign up at [JSearch API](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) and get the free API key


### 2. Configure Environment
```bash
# Copy template
cp .env.example .env

# Edit .env and add your API key
RAPIDAPI_KEY=your_key_here
RAPIDAPI_HOST=jsearch.p.rapidapi.com
```

### 3. Build & Run
```bash
# Build Docker image
docker-compose build

# Start containers
docker-compose up
```

Wait 30-60 seconds for services to start.

### 4. Access Applications
- **Streamlit UI**: http://localhost:8501
- **Airflow Dashboard**: http://localhost:8080 (admin/admin)

## How to Use

### Step 1: Fetch Jobs
1. Open http://localhost:8501
2. Enter job title (e.g., "Data Analyst") and location (e.g., "Remote")
3. Click "Fetch Jobs from API"

### Step 2: Upload Resume
1. Go to "Upload Resume" tab
2. Upload your PDF resume
3. Click "Analyze My Resume"

### Step 3: View Results
1. Go to "Match Results" tab
2. See ranked jobs with ATS scores
3. View matched skills and missing skills for each job

## Pipeline Flow
```
Fetch Jobs → Extract Keywords → Process Resume → Calculate Matches → Display Results
```

**Airflow orchestrates this 4-task pipeline:**
1. Fetch jobs from API
2. Extract skills from job descriptions
3. Extract skills from resume
4. Calculate match scores and rank jobs

## ATS Score Calculation
```
Score = (Matched Skills / Total Job Skills) × 100

Example:
Job needs: Python, SQL, AWS, Tableau (4 skills)
Resume has: Python, SQL, Tableau (3 skills)
Score = 75%
```

## Testing
```bash
# Test job fetcher
python utils/job_fetcher.py

# Test keyword extractor
python test_keyword_extractor.py

# Run Streamlit locally (without Docker)
streamlit run streamlit/app.py
```
## Acknowledgment of AI Usage

I acknowledge that AI tools (Claude) were used during the development of this project to:
- Assist with cleaning the code structure
- Debug issues
- Improve Streamlit UI
- Generate documentation and comments

Initially, my plan was to use a static dataset from Kaggle. However, Claude suggested I could make the project more dynamic and personalized by using the JSearch API to fetch real-time job postings, which I implemented.

All code was reviewed, tested, and understood before implementation. The core logic, architecture decisions, and final implementation choices were made by me.