"""
Keyword Extractor - Extracts technical skills from text
"""
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined technical skills list
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
    """
    Extract keywords from text based on predefined skills list
    
    Args:
        text: Input text (job description or resume)
        skills_list: Optional custom skills list, defaults to TECHNICAL_SKILLS
    
    Returns:
        set: Set of matched keywords
    """
    if not text:
        return set()
    
    if skills_list is None:
        skills_list = TECHNICAL_SKILLS
    
    # Convert text to lowercase for matching
    text_lower = text.lower()
    
    # Find matching skills
    matched_keywords = set()
    
    for skill in skills_list:
        # Use word boundaries to match whole words
        # e.g., 'r' should match ' R ' or 'R,' but not 'for' 
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            matched_keywords.add(skill)
    
    return matched_keywords


def calculate_match_score(resume_keywords, job_keywords):
    """
    Calculate match percentage between resume and job keywords
    
    Args:
        resume_keywords: set of keywords from resume
        job_keywords: set of keywords from job description
    
    Returns:
        tuple: (match_score, matched_keywords, missing_keywords)
    """
    if not job_keywords:
        return 0, set(), set()
    
    matched = resume_keywords & job_keywords  # Intersection
    missing = job_keywords - resume_keywords  # In job but not in resume
    
    score = (len(matched) / len(job_keywords)) * 100
    
    return round(score, 2), matched, missing


if __name__ == "__main__":
    # Test keyword extraction
    sample_text = """
    We are looking for a Data Analyst with strong Python and SQL skills.
    Experience with Tableau and AWS is a plus. Strong communication skills required.
    """
    
    keywords = extract_keywords(sample_text)
    print(f"Extracted keywords: {keywords}")
    
    # Test matching
    resume_keywords = {'python', 'sql', 'excel', 'tableau'}
    job_keywords = {'python', 'sql', 'aws', 'tableau', 'communication'}
    
    score, matched, missing = calculate_match_score(resume_keywords, job_keywords)
    print(f"\nMatch Score: {score}%")
    print(f"Matched: {matched}")
    print(f"Missing: {missing}")