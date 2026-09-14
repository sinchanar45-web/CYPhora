import os

from google import genai

try:
    import streamlit as st
except Exception:
    st = None


# Get Gemini API key
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key and st is not None:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None


# Create Gemini client only when a key is available
client = genai.Client(api_key=api_key) if api_key else None


def get_ai_recommendation(vendor, findings):

    if client is None:
        return (
            "AI recommendation is unavailable because the "
            "GEMINI_API_KEY is not configured."
        )

    prompt = f"""
You are CYPhora, an AI-driven network security compliance assistant.

Vendor: {vendor}

Failed security checks:
{findings}

For EACH failed check, provide only:

Issue:
- One short sentence explaining the problem.

Risk:
- One short sentence explaining why it matters.

Recommendation:
- One or two short sentences explaining how to fix it.

IMPORTANT RULES:
- Be VERY concise.
- Do not write long paragraphs.
- Maximum 80 words per failed check.
- Use simple professional language.
- Do not repeat information.
- Do not suggest attacking, accessing, or modifying real systems.
- Give defensive security recommendations only.
- Format the response using clear headings and bullet points.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        return f"AI recommendation could not be generated: {str(e)}"