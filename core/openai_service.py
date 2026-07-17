import json
from openai import OpenAI
from django.conf import settings


def get_openai_client():
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def generate_professional_summary(name, job_title, experience, skills):
    client = get_openai_client()
    prompt = f"""Write a compelling professional resume summary for:
    Name: {name}
    Target Job Title: {job_title}
    Experience: {experience}
    Key Skills: {skills}

    Write a 3-4 sentence professional summary that is:
    - Concise and impactful
    - Highlights key achievements
    - Uses industry-relevant keywords
    - Tailored for ATS (Applicant Tracking Systems)
    - Professional and confident tone

    Return ONLY the summary text, no extra formatting."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume writer and career coach."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def generate_experience_bullets(job_title, company, responsibilities):
    client = get_openai_client()
    prompt = f"""Transform these job responsibilities into powerful resume bullet points:
    Position: {job_title} at {company}
    Responsibilities: {responsibilities}

    Create 4-5 bullet points that:
    - Start with strong action verbs
    - Include quantifiable achievements where possible
    - Follow the STAR method (Situation, Task, Action, Result)
    - Are concise (one line each)
    - Use relevant industry keywords

    Return as a JSON array of strings, e.g.: ["Bullet 1", "Bullet 2"]
    Return ONLY the JSON array."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert resume writer. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        result = response.choices[0].message.content.strip()
        return json.loads(result)
    except Exception as e:
        return {"error": str(e)}


def generate_skills_suggestions(job_title, current_skills=""):
    client = get_openai_client()
    prompt = f"""Suggest relevant skills for a {job_title} position.
    Current skills: {current_skills}

    Suggest 10-15 skills organized by category:
    - Technical Skills
    - Soft Skills
    - Tools & Technologies
    - Certifications (if relevant)

    Return as JSON: {{"technical": [...], "soft": [...], "tools": [...], "certifications": [...]}}
    Return ONLY the JSON."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a career advisor. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        result = response.choices[0].message.content.strip()
        return json.loads(result)
    except Exception as e:
        return {"error": str(e)}


def optimize_resume_content(resume_data):
    client = get_openai_client()
    prompt = f"""Review and optimize this resume content:
    {json.dumps(resume_data, indent=2)}

    Provide optimized versions of:
    1. Professional Summary
    2. Key Skills to highlight
    3. Improved experience bullet points

    Return as JSON:
    {{"summary": "...", "skills": [...], "experience_bullets": ["..."]}}
    Return ONLY the JSON."""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert ATS-optimized resume writer. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        result = response.choices[0].message.content.strip()
        return json.loads(result)
    except Exception as e:
        return {"error": str(e)}
