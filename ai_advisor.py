import os

from google import genai

try:
    import streamlit as st
except Exception:
    st = None


# ============================================================
# GET GEMINI API KEY
# ============================================================

api_key = os.environ.get("GEMINI_API_KEY")

if not api_key and st is not None:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None


# ============================================================
# CREATE GEMINI CLIENT
# ============================================================

client = genai.Client(api_key=api_key) if api_key else None


# ============================================================
# GEMINI AI RECOMMENDATION FUNCTION
# ============================================================

def get_ai_recommendation(vendor, findings):

    # --------------------------------------------------------
    # If API key is not available
    # Return empty text so app.py uses fallback
    # --------------------------------------------------------

    if client is None:
        return ""


    # --------------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # CALL GEMINI
    # --------------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt
        )


        # ----------------------------------------------------
        # CHECK RESPONSE
        # ----------------------------------------------------

        if response is None:
            return ""

        response_text = getattr(response, "text", None)

        if not response_text:
            return ""

        response_text = str(response_text).strip()

        if not response_text:
            return ""

        return response_text


    # --------------------------------------------------------
    # GEMINI ERROR
    # Let app.py activate the CYPhora fallback
    # Do NOT expose technical API errors to the user
    # --------------------------------------------------------

    except Exception:
        return ""