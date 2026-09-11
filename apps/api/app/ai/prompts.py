JOB_ANALYSIS_PROMPT = """
Analyze the following job description and extract structured information.

Return only information that is explicitly present in the job description.
Do not invent, infer, or assume requirements.

Rules:
- required_skills: individual technical/professional skills as separate strings
- preferred_skills: individual preferred skills as separate strings
- responsibilities: individual responsibilities as separate strings
- keywords: important individual keywords or phrases as separate strings
- Do not concatenate multiple keywords into one string
- Do not use Markdown formatting
- Do not add bullet points, prefixes, numbering, or special formatting inside strings
- Keep each string concise and readable
- salary_information should contain only salary-related information explicitly stated
- If information is not available, return an empty list or null as appropriate

Job description:
{job_description}
"""

RESUME_ANALYSIS_PROMPT = """
Analyze the following resume and extract structured information.

Return only information that is explicitly present in the resume.
Do not invent, infer, or assume information.

Rules:
- skills: individual skills as separate strings
- Do not concatenate multiple skills into one string
- Do not use Markdown formatting
- Do not add bullet points, prefixes, numbering, or special formatting inside strings
- Keep summaries concise and professional
- Preserve the meaning of the original resume

Resume:
{resume_text}
"""