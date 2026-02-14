
import re

TECHNICAL_SKILLS = {
    # Programming Languages
    'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'ruby', 'php', 
    'swift', 'kotlin', 'go', 'rust', 'scala', 'r', 'matlab', 'sql', 'html', 'css',
    
    # Data Science & ML
    'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'keras', 
    'scikit-learn', 'sklearn', 'numpy', 'pandas', 'scipy', 'matplotlib', 
    'seaborn', 'plotly', 'jupyter',
    
    # Big Data
    'spark', 'hadoop', 'hive', 'kafka', 'flink', 'airflow', 'databricks',
    
    # Cloud & DevOps
    'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform', 
    'ansible', 'git', 'github', 'gitlab', 'ci/cd', 'mlops',
    
    # Databases
    'mysql', 'postgresql', 'mongodb', 'redis', 'cassandra', 'dynamodb', 
    'sqlite', 'oracle', 'sql server', 'nosql',
    
    # BI & Visualization
    'tableau', 'power bi', 'powerbi', 'looker', 'qlik', 'excel', 'google sheets',
    
    # Analytics & Statistics
    'statistics', 'statistical analysis', 'a/b testing', 'hypothesis testing',
    'regression', 'classification', 'clustering', 'time series',
    
    # Soft Skills
    'communication', 'leadership', 'problem solving', 'teamwork', 
    'collaboration', 'analytical', 'critical thinking',
}


def extract_keywords(text, skills_list=None):

    # Handle empty text
    if not text:
        return set()
    
    # Use default skills list if none provided
    if skills_list is None:
        skills_list = TECHNICAL_SKILLS
    
    # Convert text to lowercase for case-insensitive matching
    text_lower = text.lower()
    
    # Find which skills appear in the text
    found_skills = set()
    
    for skill in skills_list:
        # Use regex to match whole words only
        # This prevents matching 'r' in 'for' or 'go' in 'good'
        pattern = r'\b' + re.escape(skill) + r'\b'
        
        if re.search(pattern, text_lower):
            found_skills.add(skill)
    
    return found_skills


def calculate_match_score(resume_keywords, job_keywords):

    # Handle case where job has no keywords
    if not job_keywords:
        return 0, set(), set()
    
    # Find skills that match
    matched = resume_keywords & job_keywords
    
    # Find skills the job wants but resume doesn't have
    missing = job_keywords - resume_keywords
    
    # Calculate percentage: (matched skills / total job skills) * 100
    score = (len(matched) / len(job_keywords)) * 100
    
    return round(score, 2), matched, missing