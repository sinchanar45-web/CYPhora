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
# GEMINI AI SECURITY ANALYSIS
# ============================================================

def get_ai_recommendation(vendor, findings):

    # --------------------------------------------------------
    # API KEY CHECK
    # --------------------------------------------------------

    if client is None:
        return ""


    # --------------------------------------------------------
    # CYPhora AI PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are CYPhora, an AI-driven Multi-Vendor Network Security Compliance Auditor.

Your job is to analyze the results of a network device security compliance audit.

Vendor:
{vendor}

Audit Findings:
{findings}


IMPORTANT:
The audit findings above are produced by CYPhora's security compliance engine.

Analyze the ACTUAL findings provided.

Do NOT invent vulnerabilities that are not present in the findings.

Do NOT give the same recommendation for every failed check.

Each failed security control may represent a different security issue.

Understand the check name, severity, and message before recommending remediation.

Your response must be a professional security assessment suitable for a cybersecurity audit report and hackathon demonstration.


FORMAT YOUR RESPONSE LIKE THIS:


### 🧠 Overall Security Analysis

Write 2–4 sentences summarizing the overall security posture.

Mention:
- the vendor
- the general compliance condition
- the most important security concern
- whether immediate attention is required


### 🚨 Key Security Risks

Identify the most important failed controls.

For each important issue use:

**1. [Actual Check Name] — [Severity]**

**Issue:** Explain what is actually wrong based on the audit finding.

**Risk:** Explain the realistic security impact of this specific issue.

**Why it matters:** Briefly explain why this control is important.


### 🛠️ Recommended Actions

Give specific and DIFFERENT remediation advice for each failed control.

For example:

**1. [Actual Check Name]**

- Give a practical defensive remediation specific to this control.
- Give another relevant recommendation if useful.

**2. [Actual Check Name]**

- Give remediation specific to this control.
- Do NOT copy the recommendation from another control unless it genuinely applies.


### 🎯 Priority

End with:

**Immediate Priority:** [most important failed control]

Explain in 1–2 sentences why this should be addressed first.


IMPORTANT RULES:

- Base everything on the supplied audit findings.
- Do not invent vulnerabilities.
- Do not invent configuration commands unless they are clearly supported by the finding.
- Give defensive cybersecurity recommendations only.
- Use vendor-aware language.
- Do not give the same recommendation for different failed controls.
- Avoid generic statements such as "review and remediate this issue" when a specific recommendation can be provided.
- Explain why each issue matters.
- Keep the response concise but useful.
- Prefer bullet points over long paragraphs.
- Do not mention that you are an AI model.
- If there are only one or two failed checks, analyze those checks properly.
- If all checks passed, provide a positive security assessment instead of remediation recommendations.
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
    # --------------------------------------------------------

    except Exception:
        return ""