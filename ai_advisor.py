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
        return (
            "⚠️ AI recommendation is unavailable because the "
            "GEMINI_API_KEY is not configured."
        )


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
    # TRY GEMINI UP TO 3 TIMES
    # --------------------------------------------------------

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )


            # ------------------------------------------------
            # SUCCESSFUL RESPONSE
            # ------------------------------------------------

            if response and response.text:
                return response.text


            # Empty response
            return ""


        except Exception as e:

            error_message = str(e)


            # ------------------------------------------------
            # GEMINI TEMPORARILY UNAVAILABLE / 503
            # ------------------------------------------------

            if "503" in error_message or "UNAVAILABLE" in error_message:

                # Retry twice
                if attempt < 2:
                    time.sleep(3)
                    continue

                # Return empty so app.py uses fallback
                return ""


            # ------------------------------------------------
            # OTHER GEMINI ERRORS
            # ------------------------------------------------

            return (
                f"⚠️ AI recommendation could not be generated: "
                f"{error_message}"
            )