"""
Job ATS Matcher - Streamlit App
"""
import streamlit as st
import pandas as pd
import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.job_fetcher import fetch_jobs_from_api, save_jobs_to_csv, load_jobs_from_csv
from utils.keyword_extractor import extract_keywords, calculate_match_score
from utils.pdf_parser import extract_text_from_pdf, clean_text

# Page config
st.set_page_config(
    page_title="Job ATS Matcher",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Job ATS Matcher")
st.markdown("Upload your resume and match it against job postings!")

# Sidebar for job fetching
st.sidebar.header("🔍 Fetch Jobs")

query = st.sidebar.text_input("Job Search Query", value="Data Analyst")
location = st.sidebar.text_input("Location", value="Remote")
num_jobs = st.sidebar.slider("Number of Jobs", min_value=5, max_value=50, value=20)

if st.sidebar.button("🚀 Fetch Jobs from API"):
    with st.spinner("Fetching jobs from API..."):
        try:
            jobs_df = fetch_jobs_from_api(query=query, location=location, num_jobs=num_jobs)
            
            if not jobs_df.empty:
                # Extract keywords for each job
                jobs_df['keywords'] = jobs_df['description'].apply(
                    lambda desc: list(extract_keywords(desc)) if pd.notna(desc) else []
                )
                
                save_jobs_to_csv(jobs_df)
                st.sidebar.success(f"✅ Fetched {len(jobs_df)} jobs!")
            else:
                st.sidebar.error("❌ No jobs found. Try different search terms.")
        except Exception as e:
            st.sidebar.error(f"❌ Error: {str(e)}")

# Check if jobs exist
jobs_df = load_jobs_from_csv()

if not jobs_df.empty:
    st.sidebar.info(f"📊 {len(jobs_df)} jobs in database")
    
    # Show last updated time if file exists
    if os.path.exists('data/jobs.csv'):
        import time
        mtime = os.path.getmtime('data/jobs.csv')
        last_updated = time.strftime('%Y-%m-%d %H:%M', time.localtime(mtime))
        st.sidebar.caption(f"Last updated: {last_updated}")

# Main area - Tabs
tab1, tab2, tab3 = st.tabs(["📤 Upload Resume", "🎯 Match Results", "📋 Job Database"])

# Tab 1: Upload Resume
with tab1:
    st.header("Upload Your Resume")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file is not None:
        # Save uploaded file
        with open('data/resume.pdf', 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        st.success("✅ Resume uploaded successfully!")
        
        if st.button("🔍 Analyze My Resume"):
            if jobs_df.empty:
                st.error("❌ No jobs in database. Please fetch jobs first!")
            else:
                with st.spinner("Analyzing your resume..."):
                    try:
                        # Extract text from resume
                        resume_text = extract_text_from_pdf('data/resume.pdf')
                        cleaned_text = clean_text(resume_text)
                        
                        if not cleaned_text:
                            st.error("❌ Could not extract text from PDF. Make sure it's not an image-based PDF.")
                        else:
                            # Extract keywords
                            resume_keywords = extract_keywords(cleaned_text)
                            
                            st.success(f"✅ Extracted {len(resume_keywords)} skills from your resume")
                            
                            with st.expander("📝 Your Skills"):
                                st.write(", ".join(sorted(resume_keywords)))
                            
                            # Calculate matches
                            results = []
                            
                            for idx, row in jobs_df.iterrows():
                                job_keywords = set(row.get('keywords', []))
                                
                                if isinstance(row.get('keywords'), str):
                                    import ast
                                    try:
                                        job_keywords = set(ast.literal_eval(row['keywords']))
                                    except:
                                        job_keywords = set()
                                
                                score, matched, missing = calculate_match_score(resume_keywords, job_keywords)
                                
                                results.append({
                                    'job_title': row['job_title'],
                                    'company': row['company'],
                                    'location': row['location'],
                                    'match_score': score,
                                    'matched_keywords': list(matched),
                                    'missing_keywords': list(missing),
                                    'job_url': row['job_url'],
                                    'description': row['description']
                                })
                            
                            # Sort by match score
                            results.sort(key=lambda x: x['match_score'], reverse=True)
                            
                            # Save results
                            with open('data/results.json', 'w') as f:
                                json.dump(results, f, indent=2)
                            
                            st.success(f"✅ Matched against {len(results)} jobs!")
                            st.info("👉 Go to 'Match Results' tab to see your matches")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Tab 2: Match Results
with tab2:
    st.header("Your Job Matches")
    
    if os.path.exists('data/results.json'):
        try:
            with open('data/results.json', 'r') as f:
                content = f.read()
                if content.strip():  # Check if file is not empty
                    results = json.loads(content)
                else:
                    results = []
        except (json.JSONDecodeError, Exception) as e:
            st.warning(f"Could not load results: {e}")
            results = []
        
        if results:
            st.markdown(f"### Top {min(10, len(results))} Matches")
            
            # Display top matches
            for i, result in enumerate(results[:10], 1):
                score = result['match_score']
                
                # Color code based on score
                if score >= 70:
                    color = "🟢"
                elif score >= 50:
                    color = "🟡"
                else:
                    color = "🔴"
                
                with st.expander(f"{color} #{i} - {result['job_title']} at {result['company']} ({score}%)"):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write(f"**Company:** {result['company']}")
                        st.write(f"**Location:** {result['location']}")
                        st.write(f"**Match Score:** {score}%")
                        
                        if result.get('job_url'):
                            st.markdown(f"[🔗 Apply Here]({result['job_url']})")
                    
                    with col2:
                        st.metric("ATS Score", f"{score}%")
                    
                    st.write("**✅ Matched Skills:**")
                    if result['matched_keywords']:
                        st.write(", ".join(result['matched_keywords']))
                    else:
                        st.write("None")
                    
                    st.write("**❌ Missing Skills:**")
                    if result['missing_keywords']:
                        st.write(", ".join(result['missing_keywords']))
                    else:
                        st.write("None")
                    
                    st.write("**📄 Job Description (preview):**")
                    st.write(result['description'][:300] + "...")
        else:
            st.info("No results yet. Upload a resume and analyze it first!")
    else:
        st.info("No results yet. Upload a resume and analyze it first!")

# Tab 3: Job Database
with tab3:
    st.header("Job Database")
    
    if not jobs_df.empty:
        st.write(f"Total jobs: {len(jobs_df)}")
        
        # Display jobs table
        display_df = jobs_df[['job_title', 'company', 'location']].copy()
        st.dataframe(display_df, use_container_width=True)
        
        # Show sample job
        if st.checkbox("Show sample job details"):
            sample_idx = st.selectbox("Select job index", range(len(jobs_df)))
            sample_job = jobs_df.iloc[sample_idx]
            
            st.subheader(sample_job['job_title'])
            st.write(f"**Company:** {sample_job['company']}")
            st.write(f"**Location:** {sample_job['location']}")
            st.write(f"**Description:**")
            st.write(sample_job['description'][:500] + "...")
    else:
        st.info("No jobs in database. Fetch jobs using the sidebar!")