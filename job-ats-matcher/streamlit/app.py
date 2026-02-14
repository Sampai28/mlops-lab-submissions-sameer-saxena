
import streamlit as st
import pandas as pd
import json
import os
import sys

# Add parent directory to Python path so we can import our utility modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.job_fetcher import fetch_jobs_from_api, save_jobs_to_csv, load_jobs_from_csv
from utils.keyword_extractor import extract_keywords, calculate_match_score
from utils.pdf_parser import extract_text_from_pdf, clean_text

# Configure the page
st.set_page_config(
    page_title="Job ATS Matcher",
    layout="wide"
)

# Main title
st.title("Job ATS Matcher")
st.markdown("Upload your resume and find jobs that match your skills")

# Sidebar - Job Fetching Section
st.sidebar.header("Fetch Jobs")

# Get search parameters from user
job_query = st.sidebar.text_input("Job Search Query", value="Data Analyst")
job_location = st.sidebar.text_input("Location", value="Remote")
number_of_jobs = st.sidebar.slider("Number of Jobs", min_value=5, max_value=50, value=20)

# Button to fetch jobs from API
if st.sidebar.button("Fetch Jobs from API"):
    with st.spinner("Fetching jobs from API"):
        try:
            # Call the API to get jobs
            jobs_data = fetch_jobs_from_api(query=job_query, location=job_location, num_jobs=number_of_jobs)
            
            if not jobs_data.empty:
                # Extract keywords from each job description
                jobs_data['keywords'] = jobs_data['description'].apply(
                    lambda description: list(extract_keywords(description)) if pd.notna(description) else []
                )
                
                # Save to CSV file
                save_jobs_to_csv(jobs_data)
                st.sidebar.success("Successfully fetched " + str(len(jobs_data)) + " jobs!")
            else:
                st.sidebar.error("No jobs found. Try different search terms.")
        except Exception as error:
            st.sidebar.error("Error: " + str(error))

# Load existing jobs from file
jobs_data = load_jobs_from_csv()

# Show job database info in sidebar
if not jobs_data.empty:
    st.sidebar.info(str(len(jobs_data)) + " jobs in database")
    
    # Show when jobs were last updated
    if os.path.exists('data/jobs.csv'):
        import time
        file_modified_time = os.path.getmtime('data/jobs.csv')
        last_update = time.strftime('%Y-%m-%d %H:%M', time.localtime(file_modified_time))
        st.sidebar.caption("Last updated: " + last_update)

# Create three tabs for different sections
tab1, tab2, tab3 = st.tabs(["Upload Resume", "Match Results", "Job Database"])

# TAB 1: Resume Upload
with tab1:
    st.header("Upload Your Resume")
    
    # File uploader for PDF resumes
    resume_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if resume_file is not None:
        # Save the uploaded file
        with open('data/resume.pdf', 'wb') as file:
            file.write(resume_file.getbuffer())
        
        st.success("Resume uploaded successfully!")
        
        # Button to analyze the resume
        if st.button("Analyze My Resume"):
            if jobs_data.empty:
                st.error("No jobs in database")
            else:
                with st.spinner("Analyzing your resume..."):
                    try:
                        # Extract text from the PDF
                        resume_text = extract_text_from_pdf('data/resume.pdf')
                        cleaned_resume_text = clean_text(resume_text)
                        
                        if not cleaned_resume_text:
                            st.error("Could not extract text from PDF")
                        else:
                            # Extract skills from resume
                            resume_skills = extract_keywords(cleaned_resume_text)
                            
                            st.success("Extracted " + str(len(resume_skills)))
                            
                            # Show the extracted skills
                            with st.expander("Your Skills"):
                                st.write(", ".join(sorted(resume_skills)))
                            
                            # Compare resume against all jobs
                            all_matches = []
                            
                            for index, job_row in jobs_data.iterrows():
                                job_skills = set(job_row.get('keywords', []))
                                
                                # Handle case where keywords might be stored as string
                                if isinstance(job_row.get('keywords'), str):
                                    import ast
                                    try:
                                        job_skills = set(ast.literal_eval(job_row['keywords']))
                                    except:
                                        job_skills = set()
                                
                                # Calculate how well this job matches the resume
                                match_score, matched_skills, missing_skills = calculate_match_score(resume_skills, job_skills)
                                
                                # Store the match results
                                match_result = {
                                    'job_title': job_row['job_title'],
                                    'company': job_row['company'],
                                    'location': job_row['location'],
                                    'match_score': match_score,
                                    'matched_keywords': list(matched_skills),
                                    'missing_keywords': list(missing_skills),
                                    'job_url': job_row['job_url'],
                                    'description': job_row['description']
                                }
                                all_matches.append(match_result)
                            
                            # Sort jobs by match score (best matches first)
                            all_matches.sort(key=lambda x: x['match_score'], reverse=True)
                            
                            # Save results to file
                            with open('data/results.json', 'w') as results_file:
                                json.dump(all_matches, results_file, indent=2)
                            
                            st.success("Matched against " + str(len(all_matches)) + " jobs!")
                            st.info("Go to 'Match Results' tab to see your matches")
                    
                    except Exception as error:
                        st.error("Error: " + str(error))

# TAB 2: Match Results
with tab2:
    st.header("Your Job Matches")
    
    # Try to load previous results
    if os.path.exists('data/results.json'):
        try:
            with open('data/results.json', 'r') as results_file:
                file_content = results_file.read()
                if file_content.strip():
                    match_results = json.loads(file_content)
                else:
                    match_results = []
        except (json.JSONDecodeError, Exception) as error:
            st.warning("Could not load results: " + str(error))
            match_results = []
        
        if match_results:
            # Show top 10 matches
            top_matches = min(10, len(match_results))
            st.markdown("### Top " + str(top_matches) + " Matches")
            
            # Display each match
            for rank, match in enumerate(match_results[:10], 1):
                match_percentage = match['match_score']
                
                # Choose color based on score
                if match_percentage >= 70:
                    score_color = "🟢"
                elif match_percentage >= 50:
                    score_color = "🟡"
                else:
                    score_color = "🔴"
                
                # Create expandable section for each job
                match_title = score_color + " #" + str(rank) + " - " + match['job_title'] + " at " + match['company'] + " (" + str(match_percentage) + "%)"
                
                with st.expander(match_title):
                    # Split into two columns
                    left_column, right_column = st.columns([2, 1])
                    
                    with left_column:
                        st.write("**Company:** " + match['company'])
                        st.write("**Location:** " + match['location'])
                        st.write("**Match Score:** " + str(match_percentage) + "%")
                        
                        if match.get('job_url'):
                            st.markdown("[Apply Here](" + match['job_url'] + ")")
                    
                    with right_column:
                        st.metric("ATS Score", str(match_percentage) + "%")
                    
                    # Show matched skills
                    st.write("**Matched Skills:**")
                    if match['matched_keywords']:
                        st.write(", ".join(match['matched_keywords']))
                    else:
                        st.write("None")
                    
                    # Show missing skills
                    st.write("**Missing Skills:**")
                    if match['missing_keywords']:
                        st.write(", ".join(match['missing_keywords']))
                    else:
                        st.write("None")
                    
                    # Show job description preview
                    st.write("**Job Description (preview):**")
                    description_preview = match['description'][:300] + "..."
                    st.write(description_preview)
        else:
            st.info("No results yet. Upload a resume and analyze it")
    else:
        st.info("No results yet. Upload a resume and analyze it")

# TAB 3: Job Database
with tab3:
    st.header("Job Database")
    
    if not jobs_data.empty:
        st.write("Total jobs: " + str(len(jobs_data)))
        
        # Show jobs in a table
        table_data = jobs_data[['job_title', 'company', 'location']].copy()
        st.dataframe(table_data, use_container_width=True)
        
        # Option to view individual job details
        if st.checkbox("Show sample job details"):
            job_index = st.selectbox("Select job index", range(len(jobs_data)))
            selected_job = jobs_data.iloc[job_index]
            
            st.subheader(selected_job['job_title'])
            st.write("**Company:** " + selected_job['company'])
            st.write("**Location:** " + selected_job['location'])
            st.write("**Description:**")
            job_description = selected_job['description'][:500] + "..."
            st.write(job_description)
    else:
        st.info("No jobs in database. Fetch jobs using the sidebar")