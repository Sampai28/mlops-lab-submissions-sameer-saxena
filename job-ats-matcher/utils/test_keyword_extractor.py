
from keyword_extractor import extract_keywords, calculate_match_score


print("Testing Keyword Extractor")



# Test 1: Extract keywords from a job description
print("Test 1: Extracting keywords from job description")


job_description = """
We are looking for a Data Analyst with strong Python and SQL skills.
Experience with Tableau and AWS is a plus. 
Strong communication skills required.
Knowledge of pandas and numpy is preferred.
"""

job_keywords = extract_keywords(job_description)
print("Job description says:")
print(job_description)

print("Found these skills:", sorted(job_keywords))


# Test 2: Extract keywords from a resume
print("Test 2: Extracting keywords from resume")

resume_text = """
Data Analyst with 3 years of experience.
Expert in Python, SQL, Excel, and Tableau.
Built dashboards using Power BI.
Strong analytical and problem solving skills.
"""

resume_keywords = extract_keywords(resume_text)
print("Resume says:")
print(resume_text)

print("Found these skills:", sorted(resume_keywords))


# Test 3: Calculate match score
print("Test 3: Calculating match score")

score, matched, missing = calculate_match_score(resume_keywords, job_keywords)

print("Resume has:", sorted(resume_keywords))
print("Job needs:", sorted(job_keywords))
print("Match Score:", str(score) + "%")
print("Matched skills:", sorted(matched))
print("Missing skills:", sorted(missing))


# Test 4: Perfect match
print("Test 4: Testing perfect match (100%)")

perfect_resume = {'python', 'sql', 'aws'}
perfect_job = {'python', 'sql', 'aws'}

score, matched, missing = calculate_match_score(perfect_resume, perfect_job)
print("Resume:", sorted(perfect_resume))
print("Job:", sorted(perfect_job))
print("Score:", str(score) + "%")
print("Should be 100%")


# Test 5: No match
print("Test 5: Testing no match (0%)")

no_match_resume = {'python', 'sql'}
no_match_job = {'java', 'c++'}

score, matched, missing = calculate_match_score(no_match_resume, no_match_job)
print("Resume:", sorted(no_match_resume))
print("Job:", sorted(no_match_job))
print("Score:", str(score) + "%")
print("Should be 0%")


print("All tests completed!")