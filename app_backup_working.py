import streamlit as st

from vendor_detector import detect_vendor
from compliance_engine import check_cisco_compliance
from compliance_fortinet import check_fortinet_compliance
from compliance_paloalto import check_paloalto_compliance
from ai_advisor import get_ai_recommendation


# =========================
# PAGE SETTINGS
# =========================

st.set_page_config(
    page_title="CYPhora",
    page_icon="🛡️",
    layout="wide"
)


# =========================
# HEADER
# =========================

st.title("🛡️ CYPhora")

st.subheader(
    "AI-Driven Multi-Vendor Network Security Compliance Auditor"
)

st.caption(
    "Detect • Audit • Analyze • Recommend"
)

st.write("")


# =========================
# NAVIGATION
# =========================

tab1, tab2, tab3 = st.tabs([
    "🏠 Dashboard",
    "🔍 Security Audit",
    "📊 Reports"
])


# =========================
# DASHBOARD
# =========================

with tab1:

    st.header("Security Compliance Dashboard")

    st.write(
        "CYPhora analyzes network device configurations "
        "and evaluates them against security compliance checks."
    )

    st.write("")

    # Main metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Supported Vendors",
            "3"
        )

    with col2:
        st.metric(
            "Compliance Frameworks",
            "4"
        )

    with col3:
        st.metric(
            "Security Checks",
            "10+"
        )

    st.write("")

    # Vendors
    st.subheader("🔐 Supported Vendors")

    v1, v2, v3 = st.columns(3)

    with v1:
        st.info(
            "🌐 **Cisco**\n\n"
            "Network Security"
        )

    with v2:
        st.info(
            "🔥 **Fortinet**\n\n"
            "Network Security"
        )

    with v3:
        st.info(
            "🛡️ **Palo Alto**\n\n"
            "Network Security"
        )

    st.write("")

    # Frameworks
    st.subheader("📋 Compliance Frameworks")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        st.info("CIS Benchmarks")

    with f2:
        st.info("NIST SP 800-53")

    with f3:
        st.info("ISO/IEC 27001")

    with f4:
        st.info("DISA STIGs")

    st.write("")

    st.success(
        "🛡️ CYPhora uses a vendor-specific compliance engine "
        "combined with AI-powered security explanations."
    )


# =========================
# SECURITY AUDIT
# =========================

with tab2:

    st.header("🔍 Security Audit")

    st.write(
        "Upload a network device configuration file "
        "to begin the compliance assessment."
    )

    uploaded_file = st.file_uploader(
        "Upload Configuration",
        type=["txt", "cfg", "conf"]
    )

    if uploaded_file is not None:

        st.success(
            f"Configuration uploaded: {uploaded_file.name}"
        )

        config_text = uploaded_file.read().decode(
            "utf-8"
        )

        # =========================
        # VENDOR DETECTION
        # =========================

        vendor = detect_vendor(config_text)

        st.success(
            f"🔍 Vendor Detected: {vendor}"
        )


        # =========================
        # COMPLIANCE ENGINE
        # =========================

        if vendor == "Cisco":

            results = check_cisco_compliance(
                config_text
            )

        elif vendor == "Fortinet":

            results = check_fortinet_compliance(
                config_text
            )

        elif vendor == "Palo Alto":

            results = check_paloalto_compliance(
                config_text
            )

        else:

            results = []

            st.warning(
                "⚠️ Vendor could not be detected."
            )


        # =========================
        # RESULTS
        # =========================

        if results:

            st.subheader(
                "🔐 Security Compliance Results"
            )

            passed = sum(
                1
                for result in results
                if result["status"] == "PASS"
            )

            failed = sum(
                1
                for result in results
                if result["status"] == "FAIL"
            )

            total = len(results)

            score = int(
                (passed / total) * 100
            )


            # Metrics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "🛡️ Compliance Score",
                    f"{score}%"
                )

            with col2:
                st.metric(
                    "✅ Passed",
                    passed
                )

            with col3:
                st.metric(
                    "❌ Failed",
                    failed
                )

            st.write("")


            # =========================
            # STATUS
            # =========================

            if score == 100:

                st.success(
                    "🎉 Excellent! All security checks passed."
                )

            elif score >= 70:

                st.warning(
                    "⚠️ Configuration has some security gaps."
                )

            else:

                st.error(
                    "🚨 Critical security gaps detected."
                )


            st.write("")


            # =========================
            # INDIVIDUAL CHECKS
            # =========================

            st.subheader(
                "📋 Detailed Findings"
            )

            for result in results:

                if result["status"] == "PASS":

                    st.success(
                        f"✅ **{result['check']}** — "
                        f"{result['message']}"
                    )

                else:

                    st.error(
                        f"❌ **{result['check']}** — "
                        f"{result['message']}"
                    )


            # =========================
            # AI ANALYSIS
            # =========================

            failed_results = [
                result
                for result in results
                if result["status"] == "FAIL"
            ]


            if failed_results:

                st.subheader(
                    "🤖 AI Security Analysis"
                )

                findings_text = ""

                for result in failed_results:

                    findings_text += (
                        f"- {result['check']}: "
                        f"{result['message']}\n"
                    )


                with st.spinner(
                    "🤖 CYPhora AI is analyzing the findings..."
                ):

                    try:

                        recommendation = (
                            get_ai_recommendation(
                                vendor,
                                findings_text
                            )
                        )

                        st.info(
                            recommendation
                        )

                    except Exception as e:

                        st.warning(
                            "⚠️ AI analysis could not be generated."
                        )

                        st.caption(
                            f"Gemini Error: {e}"
                        )


            else:

                st.success(
                    "🎉 No security issues detected. "
                    "AI analysis is not required."
                )


            # =========================
            # CONFIGURATION PREVIEW
            # =========================

            st.subheader(
                "📄 Configuration Preview"
            )

            st.code(
                config_text,
                language="text"
            )


# =========================
# REPORTS
# =========================

with tab3:

    st.header("📊 Audit Reports")

    st.write(
        "CYPhora audit summary and compliance status."
    )

    st.info(
        "Upload a configuration in the Security Audit tab "
        "to generate an audit summary."
    )

    st.write("")

    st.subheader(
        "📌 Report Contents"
    )

    r1, r2, r3 = st.columns(3)

    with r1:
        st.info(
            "🔍 **Vendor Detection**\n\n"
            "Identify the network device vendor."
        )

    with r2:
        st.info(
            "🛡️ **Compliance Assessment**\n\n"
            "Evaluate security configuration settings."
        )

    with r3:
        st.info(
            "🤖 **AI Analysis**\n\n"
            "Explain security gaps and recommend remediation."
        )

    st.write("")

    st.success(
        "📄 CYPhora generates an audit-ready assessment "
        "containing vendor information, compliance findings, "
        "security score, and AI recommendations."
    )