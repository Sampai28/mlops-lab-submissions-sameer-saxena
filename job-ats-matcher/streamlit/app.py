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
jobQuery = st.sidebar.text_input("Job Search Query", value="Data Analyst")
jobLocation = st.sidebar.text_input("Location", value="Remote")
numberOfJobs = st.sidebar.slider("Number of Jobs", min_value=5, max_value=50, value=20)

# Button to fetch jobs from API
if st.sidebar.button("Fetch Jobs from API"):
    with st.spinner("Fetching jobs from API"):
        try:
            # Call the API to get jobs
            jobsData = fetch_jobs_from_api(query=jobQuery, location=jobLocation, num_jobs=numberOfJobs)
            
            if not jobsData.empty:
                # Extract keywords from each job description
                jobsData['keywords'] = jobsData['description'].apply(
                    lambda description: list(extract_keywords(description)) if pd.notna(description) else []
                )
                
                # Save to CSV file
                save_jobs_to_csv(jobsData)
                st.sidebar.success("Successfully fetched " + str(len(jobsData)) + " jobs!")
            else:
                st.sidebar.error("No jobs found. Try different search terms.")
        except Exception as error:
            st.sidebar.error("Error: " + str(error))

# Load existing jobs from file
jobsData = load_jobs_from_csv()

# Show job database info in sidebar
if not jobsData.empty:
    st.sidebar.info(str(len(jobsData)) + " jobs in database")
    
    # Show when jobs were last updated
    if os.path.exists('data/jobs.csv'):
        import time
        fileModifiedTime = os.path.getmtime('data/jobs.csv')
        lastUpdate = time.strftime('%Y-%m-%d %H:%M', time.localtime(fileModifiedTime))
        st.sidebar.caption("Last updated: " + lastUpdate)

# Create three tabs for different sections
tab1, tab2, tab3 = st.tabs(["Upload Resume", "Match Results", "Job Database"])

# TAB 1: Resume Upload
with tab1:
    st.header("Upload Your Resume")
    
    # File uploader for PDF resumes
    resumeFile = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if resumeFile is not None:
        # Save the uploaded file
        with open('data/resume.pdf', 'wb') as file:
            file.write(resumeFile.getbuffer())
        
        st.success("Resume uploaded successfully!")
        
        # Button to analyze the resume
        if st.button("Analyze My Resume"):
            if jobsData.empty:
                st.error("No jobs in database")
            else:
                with st.spinner("Analyzing your resume..."):
                    try:
                        # Extract text from the PDF
                        resumeText = extract_text_from_pdf('data/resume.pdf')
                        cleanedResumeText = clean_text(resumeText)
                        
                        if not cleanedResumeText:
                            st.error("Could not extract text from PDF")
                        else:
                            # Extract skills from resume
                            resumeSkills = extract_keywords(cleanedResumeText)
                            
                            st.success("Extracted " + str(len(resumeSkills)))
                            
                            # Show the extracted skills
                            with st.expander("Your Skills"):
                                st.write(", ".join(sorted(resumeSkills)))
                            
                            # Compare resume against all jobs
                            allMatches = []
                            
                            for index, jobRow in jobsData.iterrows():
                                jobSkills = set(jobRow.get('keywords', []))
                                
                                # Handle case where keywords might be stored as string
                                if isinstance(jobRow.get('keywords'), str):
                                    import ast
                                    try:
                                        jobSkills = set(ast.literal_eval(jobRow['keywords']))
                                    except:
                                        jobSkills = set()
                                
                                # Calculate how well this job matches the resume
                                matchScore, matchedSkills, missingSkills = calculate_match_score(resumeSkills, jobSkills)
                                
                                # Store the match results
                                matchResult = {
                                    'job_title': jobRow['job_title'],
                                    'company': jobRow['company'],
                                    'location': jobRow['location'],
                                    'match_score': matchScore,
                                    'matched_keywords': list(matchedSkills),
                                    'missing_keywords': list(missingSkills),
                                    'job_url': jobRow['job_url'],
                                    'description': jobRow['description']
                                }
                                allMatches.append(matchResult)
                            
                            # Sort jobs by match score (best matches first)
                            allMatches.sort(key=lambda x: x['match_score'], reverse=True)
                            
                            # Save results to file
                            with open('data/results.json', 'w') as resultsFile:
                                json.dump(allMatches, resultsFile, indent=2)
                            
                            st.success("Matched against " + str(len(allMatches)) + " jobs!")
                            st.info("Go to 'Match Results' tab to see your matches")
                    
                    except Exception as error:
                        st.error("Error: " + str(error))

# TAB 2: Match Results
with tab2:
    st.header("Your Job Matches")
    
    # Try to load previous results
    if os.path.exists('data/results.json'):
        try:
            with open('data/results.json', 'r') as resultsFile:
                fileContent = resultsFile.read()
                if fileContent.strip():
                    matchResults = json.loads(fileContent)
                else:
                    matchResults = []
        except (json.JSONDecodeError, Exception) as error:
            st.warning("Could not load results: " + str(error))
            matchResults = []
        
        if matchResults:
            # Show top 10 matches
            topMatches = min(10, len(matchResults))
            st.markdown("### Top " + str(topMatches) + " Matches")
            
            # Display each match
            for rank, match in enumerate(matchResults[:10], 1):
                matchPercentage = match['match_score']
                
                # Choose color based on score
                if matchPercentage >= 70:
                    scoreColor = "🟢"
                elif matchPercentage >= 50:
                    scoreColor = "🟡"
                else:
                    scoreColor = "🔴"
                
                # Create expandable section for each job
                matchTitle = scoreColor + " #" + str(rank) + " - " + match['job_title'] + " at " + match['company'] + " (" + str(matchPercentage) + "%)"
                
                with st.expander(matchTitle):
                    # Split into two columns
                    leftColumn, rightColumn = st.columns([2, 1])
                    
                    with leftColumn:
                        st.write("**Company:** " + str(match['company']))
                        st.write("**Location:** " + str(match['location']))
                        st.write("**Match Score:** " + str(matchPercentage) + "%")
                        
                        if match.get('job_url'):
                            st.markdown("[Apply Here](" + match['job_url'] + ")")
                    
                    with rightColumn:
                        st.metric("ATS Score", str(matchPercentage) + "%")
                    
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
                    descriptionPreview = match['description'][:300] + "..."
                    st.write(descriptionPreview)
        else:
            st.info("No results yet. Upload a resume and analyze it")
    else:
        st.info("No results yet. Upload a resume and analyze it")

# TAB 3: Job Database
with tab3:
    st.header("Job Database")
    
    if not jobsData.empty:
        st.write("Total jobs: " + str(len(jobsData)))
        
        # Show jobs in a table
        tableData = jobsData[['job_title', 'company', 'location']].copy()
        st.dataframe(tableData, use_container_width=True)
        
        # Option to view individual job details
        if st.checkbox("Show sample job details"):
            jobIndex = st.selectbox("Select job index", range(len(jobsData)))
            selectedJob = jobsData.iloc[jobIndex]
            
            st.subheader(selectedJob['job_title'])
            st.write("**Company:** " + str(selectedJob['company']))
            st.write("**Location:** " + str(selectedJob['location']))
            st.write("**Description:**")
            jobDescription = selectedJob['description'][:500] + "..."
            st.write(jobDescription)
    else:
        st.info("No jobs in database. Fetch jobs using the sidebar")