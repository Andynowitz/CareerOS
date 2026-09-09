JOB_ANALYSIS_PROMPT = """
Analyze the following job description.

Extract the following information:

1. Required technical and soft skills
2. Preferred or nice-to-have skills
3. Main responsibilities
4. Required experience
5. Education requirements
6. Important keywords
7. Salary information, if explicitly mentioned

Do not invent information that is not present in the job description.

Return the information in the requested structured format.

Job description:
{job_description}
"""

RESUME_ANALYSIS_PROMPT = """
Analyze the following resume.

Extract the following information:

1. Technical and soft skills
2. Professional experience summary
3. Education summary
4. Projects summary

Do not invent information that is not present in the resume.

Keep the summaries concise but informative.

Return the information in the requested structured format.

Resume:
{resume_text}
"""