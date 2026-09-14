import os
import time

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
# AI RECOMMENDATION FUNCTION
# ============================================================

def get_ai_recommendation(vendor, findings):

    # --------------------------------------------------------
    # API KEY NOT AVAILABLE
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
    # TRY GEMINI
    # --------------------------------------------------------

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )


            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if response and response.text:
                return response.text

            return ""


        except Exception as e:

            error_message = str(e)


            # ------------------------------------------------
            # GEMINI QUOTA EXCEEDED / RATE LIMIT
            # 429 RESOURCE_EXHAUSTED
            # ------------------------------------------------

            if (
                "429" in error_message
                or "RESOURCE_EXHAUSTED" in error_message
                or "quota" in error_message.lower()
                or "rate limit" in error_message.lower()
            ):

                # Retry once after a short delay.
                # If quota is exhausted, the fallback in app.py
                # will automatically be displayed.
                if attempt < 2:
                    time.sleep(3)
                    continue

                return ""


            # ------------------------------------------------
            # GEMINI TEMPORARILY UNAVAILABLE
            # 503
            # ------------------------------------------------

            if (
                "503" in error_message
                or "UNAVAILABLE" in error_message
            ):

                if attempt < 2:
                    time.sleep(3)
                    continue

                return ""


            # ------------------------------------------------
            # OTHER ERRORS
            # ------------------------------------------------

            return ""