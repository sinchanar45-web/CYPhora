import os
import time

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
            "⚠️ AI recommendation is unavailable because the "
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

    # Try Gemini up to 3 times if the service is temporarily unavailable
    for attempt in range(3):

        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt
            )

            if response and response.text:
                return response.text

            return "⚠️ Gemini returned an empty response."

        except Exception as e:

            error_message = str(e)

            # Retry temporary 503/high-demand errors
            if "503" in error_message or "UNAVAILABLE" in error_message:

                if attempt < 2:
                    time.sleep(3)
                    continue

                return (
                    "⚠️ CYPhora AI is temporarily unavailable because "
                    "the Gemini service is experiencing high demand. "
                    "Please try the audit again in a few moments."
                )

            # Other errors should be shown normally
            return (
                f"⚠️ AI recommendation could not be generated: "
                f"{error_message}"
            )