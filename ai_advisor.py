import os
import streamlit as st
from google import genai


def get_ai_recommendation(vendor, findings):

    # Get Gemini API key
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("CYPhora Gemini Error: API key not found", flush=True)
        return ""

    try:
        # Create Gemini client
        client = genai.Client(api_key=api_key)

        prompt = f"""
You are CYPhora, an AI-driven network security compliance auditor.

Vendor:
{vendor}

Failed Security Checks:
{findings}

Analyze these security findings and provide a useful, specific security assessment.

Use exactly these sections:

### Overall Security Analysis
Give a short overall assessment based only on the supplied findings.

### Key Security Risks
List the important risks found.

### Recommended Actions
For EACH failed security check:
- Name the check
- Explain the specific issue
- Explain the security risk
- Give a specific defensive recommendation

Do NOT give the same generic recommendation for every check.

### Priority
Identify which issue should be fixed first and explain why.

Rules:
- Base everything only on the supplied findings.
- Do not invent vulnerabilities.
- Do not invent configuration details.
- Make recommendations specific to each finding.
- Use simple professional language.
- Be concise.
- Defensive security guidance only.
- Do not provide attack or exploitation instructions.
"""

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )

        if response is None:
            print("CYPhora Gemini Error: Empty response", flush=True)
            return ""

        response_text = getattr(response, "text", None)

        if response_text:
            response_text = str(response_text).strip()

            if response_text:
                print("CYPhora Gemini: AI response received", flush=True)
                return response_text

        print("CYPhora Gemini Error: No text returned", flush=True)
        return ""

    except Exception as e:
        print("CYPhora Gemini Error:", repr(e), flush=True)
        return ""