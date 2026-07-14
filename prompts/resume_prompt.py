# Resume prompt template for IBM Granite

RESUME_PROMPT = """You are an advanced resume parsing engine. Your job is to extract structural entities from the provided plain text representation of a candidate's resume.

Resume Text:
{resume_text}

Extract the following information and output it ONLY as a valid JSON object matching the schema below.
Ensure you clean up strings and don't make up details not present in the text.
Do not include markdown tags, backticks, or any conversational text.

JSON Structure:
{{
  "candidate_name": "Full Name or 'Unknown' if not found",
  "skills": ["skill1", "skill2"],
  "programming_languages": ["language1", "language2"],
  "frameworks": ["framework1", "framework2"],
  "projects": [
    {{
      "title": "Project Title",
      "description": "Short description of project accomplishments."
    }}
  ],
  "work_experience": [
    {{
      "role": "Job Title",
      "company": "Company Name",
      "duration": "Duration (e.g. June 2022 - Aug 2024)",
      "description": "Key responsibilities and achievements."
    }}
  ],
  "education": [
    {{
      "degree": "Degree (e.g. B.S. in Computer Science)",
      "institution": "University / College Name",
      "graduation_year": "Year"
    }}
  ],
  "certifications": ["cert1", "cert2"],
  "achievements": ["achievement1", "achievement2"],
  "tools": ["tool1", "tool2"],
  "technologies": ["tech1", "tech2"],
  "soft_skills": ["soft_skill1", "soft_skill2"]
}}
"""
