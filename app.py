import streamlit as st
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from xml.sax.saxutils import escape

from vendor_detector import detect_vendor
from compliance_engine import check_cisco_compliance
from compliance_fortinet import check_fortinet_compliance
from compliance_paloalto import check_paloalto_compliance
from compliance_juniper import check_juniper_compliance
from compliance_arista import check_arista_compliance
from compliance_checkpoint import check_checkpoint_compliance
from ai_advisor import get_ai_recommendation


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="CYPhora | Security Compliance Auditor",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "audit_report" not in st.session_state:
    st.session_state.audit_report = None

if "audit_results" not in st.session_state:
    st.session_state.audit_results = []

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None

if "before_audit" not in st.session_state:
    st.session_state.before_audit = None

if "after_audit" not in st.session_state:
    st.session_state.after_audit = None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main {
        padding-top: 1rem;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .hero {
        padding: 28px;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #0f172a 0%,
            #172554 55%,
            #1e3a8a 100%
        );
        color: white;
        margin-bottom: 25px;
        border: 1px solid #334155;
    }

    .hero-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 5px;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #cbd5e1;
        margin-bottom: 12px;
    }

    .hero-tag {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background: #1e40af;
        color: white;
        font-size: 13px;
        margin-right: 6px;
    }

    .section-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #334155;
        background: rgba(15, 23, 42, 0.55);
        margin-bottom: 18px;
    }

    .metric-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #334155;
        text-align: center;
        min-height: 115px;
    }

    .metric-number {
        font-size: 30px;
        font-weight: 800;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 14px;
    }

    .vendor-card {
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #334155;
        text-align: center;
        min-height: 130px;
    }

    .vendor-name {
        font-size: 20px;
        font-weight: 700;
        margin-top: 8px;
    }

    .vendor-type {
        color: #94a3b8;
        font-size: 13px;
    }

    .status-good {
        padding: 15px;
        border-radius: 12px;
        background: rgba(22, 163, 74, 0.15);
        border: 1px solid #16a34a;
    }

    .status-warning {
        padding: 15px;
        border-radius: 12px;
        background: rgba(234, 179, 8, 0.12);
        border: 1px solid #ca8a04;
    }

    .status-danger {
        padding: 15px;
        border-radius: 12px;
        background: rgba(220, 38, 38, 0.12);
        border: 1px solid #dc2626;
    }

    .ai-card {
        padding: 22px;
        border-radius: 15px;
        border: 1px solid #6366f1;
        background: rgba(79, 70, 229, 0.08);
    }

    .footer {
        text-align: center;
        color: #64748b;
        padding-top: 35px;
        padding-bottom: 10px;
        font-size: 13px;
    }

    .dashboard-hero {
        padding: 30px 34px;
        border-radius: 20px;
        background: linear-gradient(135deg, #0f172a, #172554 55%, #1d4ed8);
        color: white;
        margin-bottom: 24px;
        border: 1px solid #334155;
        box-shadow: 0 10px 30px rgba(15, 23, 42, 0.16);
    }

    .dashboard-hero-title {
        font-size: 38px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-bottom: 6px;
    }

    .dashboard-hero-text {
        color: #cbd5e1;
        font-size: 16px;
        margin-bottom: 16px;
    }

    .dashboard-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,0.12);
        border: 1px solid rgba(255,255,255,0.20);
        color: #e2e8f0;
        font-size: 13px;
        margin-right: 7px;
    }

    .dashboard-card {
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        background: white;
        min-height: 120px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.06);
    }

    .dashboard-card-title {
        font-size: 14px;
        color: #64748b;
        margin-bottom: 7px;
    }

    .dashboard-card-value {
        font-size: 28px;
        font-weight: 800;
        color: #0f172a;
    }

    .dashboard-card-subtitle {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }

    .workflow-card {
        padding: 18px 14px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        background: white;
        min-height: 150px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
    }

    .workflow-number {
        font-size: 27px;
        margin-bottom: 8px;
    }

    .workflow-title {
        font-weight: 750;
        color: #0f172a;
        margin-bottom: 5px;
    }

    .workflow-text {
        font-size: 12px;
        color: #64748b;
    }

    .vendor-card {
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        background: white;
        text-align: center;
        min-height: 135px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }

    .vendor-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 22px rgba(15, 23, 42, 0.09);
    }

    .vendor-name {
        font-size: 19px;
        font-weight: 750;
        color: #0f172a;
        margin-top: 8px;
    }

    .vendor-type {
        color: #64748b;
        font-size: 12px;
        margin-top: 4px;
    }

    .framework-card {
        padding: 18px;
        border-radius: 15px;
        border: 1px solid #e2e8f0;
        background: white;
        min-height: 105px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.05);
    }

    .framework-title {
        font-weight: 750;
        color: #0f172a;
        margin-bottom: 6px;
    }

    .framework-text {
        color: #64748b;
        font-size: 12px;
    }

    .section-label {
        color: #64748b;
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 15px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# NAVIGATION TABS
# =========================================================

tab1, tab2, tab3 = st.tabs(
    [
        "🏠 Dashboard",
        "🔍 Security Audit",
        "📊 Reports"
    ]
)


# =========================================================
# DASHBOARD
# =========================================================

with tab1:

    # -----------------------------------------------------
    # HERO
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="dashboard-hero">
            <div class="dashboard-hero-title">🛡️ CYPhora</div>
            <div class="dashboard-hero-text">
                AI-driven multi-vendor network security compliance auditor
            </div>
            <span class="dashboard-badge">SIH 2026</span>
            <span class="dashboard-badge">Defensive Security</span>
            <span class="dashboard-badge">AI-Assisted Analysis</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        "### Security Compliance Dashboard"
    )

    st.markdown(
        '<div class="section-label">'
        'Monitor configuration security, compliance status and audit insights.'
        '</div>',
        unsafe_allow_html=True
    )

    # -----------------------------------------------------
    # LATEST AUDIT
    # -----------------------------------------------------

    latest_report = st.session_state.audit_report

    if latest_report is None:

        st.info(
            "📁 **Ready for your first audit** — open **Security Audit** "
            "and upload a Cisco, Fortinet, Palo Alto, Juniper, Arista "
            "or Check Point configuration."
        )

    else:

        st.markdown("#### 📌 Latest Audit")

        score = latest_report["score"]

        if score == 100:
            status_text = "Excellent"
            status_icon = "🟢"
        elif score >= 70:
            status_text = "Needs Attention"
            status_icon = "🟠"
        else:
            status_text = "Critical"
            status_icon = "🔴"

        a1, a2, a3, a4 = st.columns(4)

        with a1:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="dashboard-card-title">Vendor</div>
                    <div class="dashboard-card-value">
                        {latest_report["vendor"]}
                    </div>
                    <div class="dashboard-card-subtitle">
                        Detected automatically
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with a2:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="dashboard-card-title">Compliance Score</div>
                    <div class="dashboard-card-value">
                        {score}%
                    </div>
                    <div class="dashboard-card-subtitle">
                        Overall configuration score
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with a3:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="dashboard-card-title">Checks Passed</div>
                    <div class="dashboard-card-value">
                        {latest_report["passed"]}
                    </div>
                    <div class="dashboard-card-subtitle">
                        Security controls satisfied
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with a4:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="dashboard-card-title">Checks Failed</div>
                    <div class="dashboard-card-value">
                        {latest_report["failed"]}
                    </div>
                    <div class="dashboard-card-subtitle">
                        Findings requiring review
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        if score == 100:
            st.success(
                f"{status_icon} **{status_text}** — all configured security checks passed."
            )
        elif score >= 70:
            st.warning(
                f"{status_icon} **{status_text}** — some security controls require attention."
            )
        else:
            st.error(
                f"{status_icon} **{status_text}** — significant security gaps were detected."
            )

    st.write("")

    # -----------------------------------------------------
    # PLATFORM OVERVIEW
    # -----------------------------------------------------

    st.markdown("#### 📊 Platform Overview")

    p1, p2, p3, p4 = st.columns(4)

    platform_cards = [
        (
            "6",
            "Supported Vendors",
            "Cisco • Fortinet • Palo Alto • Juniper • Arista • Check Point"
        ),
        (
            "15+",
            "Security Checks",
            "Automated configuration checks"
        ),
        (
            "5",
            "Compliance Areas",
            "Security hardening and control areas"
        ),
        (
            "ACTIVE",
            "AI Assistant",
            "AI-assisted findings and remediation"
        )
    ]

    for column, (value, title, subtitle) in zip(
        [p1, p2, p3, p4],
        platform_cards
    ):
        with column:
            st.markdown(
                f"""
                <div class="dashboard-card">
                    <div class="dashboard-card-title">{title}</div>
                    <div class="dashboard-card-value">{value}</div>
                    <div class="dashboard-card-subtitle">{subtitle}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # -----------------------------------------------------
    # HOW CYPhora WORKS
    # -----------------------------------------------------

    st.markdown("#### ⚙️ How CYPhora Works")

    workflow = [
        ("1️⃣", "Upload", "Upload a network configuration file."),
        ("2️⃣", "Detect", "Automatically identify the vendor."),
        ("3️⃣", "Audit", "Run vendor-specific security checks."),
        ("4️⃣", "Analyze", "Explain failed controls with AI."),
        ("5️⃣", "Report", "Review and download the audit report.")
    ]

    wcols = st.columns(5)

    for column, (number, title, description) in zip(
        wcols,
        workflow
    ):
        with column:
            st.markdown(
                f"""
                <div class="workflow-card">
                    <div class="workflow-number">{number}</div>
                    <div class="workflow-title">{title}</div>
                    <div class="workflow-text">{description}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # -----------------------------------------------------
    # SUPPORTED VENDORS
    # -----------------------------------------------------

    st.markdown("#### 🌐 Supported Network Vendors")

    vendors = [
        ("🌐", "Cisco", "Network Infrastructure"),
        ("🔥", "Fortinet", "Firewall & Security"),
        ("🛡️", "Palo Alto", "Next-Generation Firewall"),
        ("🔷", "Juniper", "Network Infrastructure"),
        ("🔶", "Arista", "Data Center Networking"),
        ("🟦", "Check Point", "Network Security")
    ]

    vendor_rows = [
        vendors[:3],
        vendors[3:]
    ]

    for row in vendor_rows:

        cols = st.columns(3)

        for column, (icon, name, vendor_type) in zip(cols, row):

            with column:
                st.markdown(
                    f"""
                    <div class="vendor-card">
                        <div style="font-size:34px;">{icon}</div>
                        <div class="vendor-name">{name}</div>
                        <div class="vendor-type">{vendor_type}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.write("")

    # -----------------------------------------------------
    # COMPLIANCE FRAMEWORKS
    # -----------------------------------------------------

    st.markdown("#### 📋 Compliance Framework Alignment")

    frameworks = [
        ("CIS Benchmarks", "Configuration hardening"),
        ("NIST SP 800-53", "Security controls"),
        ("ISO/IEC 27001", "Information security"),
        ("DISA STIGs", "Security hardening")
    ]

    fcols = st.columns(4)

    for column, (title, description) in zip(
        fcols,
        frameworks
    ):

        with column:

            st.markdown(
                f"""
                <div class="framework-card">
                    <div class="framework-title">{title}</div>
                    <div class="framework-text">{description}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    # -----------------------------------------------------
    # ARCHITECTURE
    # -----------------------------------------------------

    with st.expander("🧠 View CYPhora Architecture"):

        st.code(
            """
User
  │
  ▼
CYPhora Dashboard
  │
  ▼
Configuration Upload
  │
  ▼
Automatic Vendor Detection
  │
  ▼
Vendor-Specific Compliance Engine
  │
  ├── Cisco
  ├── Fortinet
  ├── Palo Alto
  ├── Juniper
  ├── Arista
  └── Check Point
  │
  ▼
PASS / FAIL + Severity
  │
  ▼
AI Security Analysis
  │
  ▼
Audit Report + PDF
            """,
            language="text"
        )

    st.success(
        "🛡️ CYPhora combines automated compliance checks "
        "with AI-assisted security explanations and remediation guidance."
    )


# =========================================================
# SECURITY AUDIT
# =========================================================

with tab2:

    st.header("🔍 Security Audit")

    st.write(
        "Upload a network configuration and CYPhora will "
        "automatically detect the vendor and evaluate security controls."
    )

    st.write("")

    # -----------------------------------------------------
    # UPLOAD AREA
    # -----------------------------------------------------

    st.subheader("📁 Configuration Upload")

    uploaded_file = st.file_uploader(
        "Upload network configuration",
        type=["txt", "cfg", "conf"],
        help="Supported formats: TXT, CFG and CONF"
    )

    if uploaded_file is None:

        st.info(
            "💡 Upload a Cisco, Fortinet, Palo Alto, Juniper, "
            "Arista or Check Point configuration file to start the audit."
        )

        st.write("")

        st.subheader("Supported Configuration Examples")

        e1, e2, e3 = st.columns(3)

        with e1:
            st.write("🌐 **Cisco IOS**")
            st.caption("Router / switch configuration")

        with e2:
            st.write("🔥 **FortiGate**")
            st.caption("Firewall configuration")

        with e3:
            st.write("🛡️ **Palo Alto**")
            st.caption("PAN-OS configuration")

        e4, e5, e6 = st.columns(3)

        with e4:
            st.write("🔷 **Juniper Junos**")
            st.caption("Router / switch configuration")

        with e5:
            st.write("🔶 **Arista EOS**")
            st.caption("Data center switch configuration")

        with e6:
            st.write("🟦 **Check Point**")
            st.caption("Firewall / security configuration")

    else:

        st.success(
            f"📄 Configuration uploaded: **{uploaded_file.name}**"
        )

        try:

            config_text = uploaded_file.read().decode("utf-8")

        except UnicodeDecodeError:

            st.error(
                "Unable to read the configuration file. "
                "Please upload a UTF-8 text configuration file."
            )

            st.stop()

        # -------------------------------------------------
        # VENDOR DETECTION
        # -------------------------------------------------

        st.subheader("🔎 Vendor Detection")

        vendor = detect_vendor(config_text)

        if vendor == "Unknown":

            st.warning(
                "⚠️ CYPhora could not confidently detect the vendor."
            )

            st.info(
                "Please upload a Cisco, Fortinet, Palo Alto, Juniper, "
                "Arista or Check Point configuration file."
            )

        else:

            st.success(
                f"✅ Vendor Detected: **{vendor}**"
            )

            # -------------------------------------------------
            # CLEAR OLD AI RESULT
            # -------------------------------------------------

            st.session_state.ai_result = None

            # -------------------------------------------------
            # COMPLIANCE ENGINE
            # -------------------------------------------------

            with st.spinner(
                "Running security compliance checks..."
            ):

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

                elif vendor == "Juniper":

                    results = check_juniper_compliance(
                        config_text
                    )

                elif vendor == "Arista":

                    results = check_arista_compliance(
                        config_text
                    )

                elif vendor == "Check Point":

                    results = check_checkpoint_compliance(
                        config_text
                    )

                else:

                    results = []

            # -------------------------------------------------
            # RESULTS
            # -------------------------------------------------

            if results:

                passed = sum(
                    1
                    for result in results
                    if result.get("status") == "PASS"
                )

                failed = sum(
                    1
                    for result in results
                    if result.get("status") == "FAIL"
                )

                high = sum(
                    1
                    for result in results
                    if result.get("severity") == "HIGH"
                    and result.get("status") == "FAIL"
                )

                medium = sum(
                    1
                    for result in results
                    if result.get("severity") == "MEDIUM"
                    and result.get("status") == "FAIL"
                )

                low = sum(
                    1
                    for result in results
                    if result.get("severity") == "LOW"
                    and result.get("status") == "FAIL"
                )

                total = len(results)

                score = int(
                    (passed / total) * 100
                ) if total > 0 else 0

                if score == 100:

                    report_status = "Excellent"

                elif score >= 70:

                    report_status = "Needs Attention"

                else:

                    report_status = "Critical"

                # -------------------------------------------------
                # SAVE REPORT
                # -------------------------------------------------

                st.session_state.audit_report = {
                    "vendor": vendor,
                    "filename": uploaded_file.name,
                    "score": score,
                    "passed": passed,
                    "failed": failed,
                    "high": high,
                    "medium": medium,
                    "low": low,
                    "status": report_status
                }

                st.session_state.audit_results = results

                # -------------------------------------------------
                # SECURITY SCORE
                # -------------------------------------------------

                st.subheader("🛡️ Security Compliance Score")

                col1, col2, col3, col4 = st.columns(4)

                with col1:

                    st.metric(
                        "Compliance Score",
                        f"{score}%"
                    )

                with col2:

                    st.metric(
                        "Passed",
                        passed
                    )

                with col3:

                    st.metric(
                        "Failed",
                        failed
                    )

                with col4:

                    st.metric(
                        "High Severity",
                        high
                    )

                st.progress(
                    score / 100
                )

                # -------------------------------------------------
                # STATUS
                # -------------------------------------------------

                if score == 100:

                    st.success(
                        "🟢 Excellent — all security checks passed."
                    )

                elif score >= 70:

                    st.warning(
                        "🟠 Needs Attention — some security controls failed."
                    )

                else:

                    st.error(
                        "🔴 Critical — multiple security controls failed."
                    )

                st.write("")

                # -------------------------------------------------
                # COMPLIANCE CHART
                # -------------------------------------------------

                st.subheader("📊 Compliance Overview")

                chart_data = pd.DataFrame(
                    {
                        "Status": [
                            "Passed",
                            "Failed"
                        ],
                        "Count": [
                            passed,
                            failed
                        ]
                    }
                )

                st.bar_chart(
                    chart_data.set_index("Status")
                )

                # -------------------------------------------------
                # SEVERITY OVERVIEW
                # -------------------------------------------------

                st.subheader("🚨 Risk Severity Overview")

                severity_data = pd.DataFrame(
                    {
                        "Severity": [
                            "HIGH",
                            "MEDIUM",
                            "LOW"
                        ],
                        "Count": [
                            high,
                            medium,
                            low
                        ]
                    }
                )

                st.bar_chart(
                    severity_data.set_index("Severity")
                )

                st.write("")

                # -------------------------------------------------
                # DETAILED FINDINGS
                # -------------------------------------------------

                st.subheader("🔎 Detailed Security Findings")

                for result in results:

                    severity = result.get(
                        "severity",
                        "MEDIUM"
                    )

                    check_name = result.get(
                        "check",
                        "Security Check"
                    )

                    message = result.get(
                        "message",
                        "No additional information."
                    )

                    status = result.get(
                        "status",
                        "FAIL"
                    )

                    if status == "PASS":

                        st.success(
                            f"✅ **{check_name}**\n\n"
                            f"{message}\n\n"
                            f"Severity: **{severity}**"
                        )

                    else:

                        if severity == "HIGH":

                            st.error(
                                f"🔴 **HIGH — {check_name}**\n\n"
                                f"{message}"
                            )

                        elif severity == "MEDIUM":

                            st.warning(
                                f"🟠 **MEDIUM — {check_name}**\n\n"
                                f"{message}"
                            )

                        else:

                            st.info(
                                f"🟢 **LOW — {check_name}**\n\n"
                                f"{message}"
                            )

                st.write("")

                # -------------------------------------------------
                # AI SECURITY ANALYSIS
                # -------------------------------------------------

                st.subheader("🤖 AI Security Analysis")

                failed_results = [
                    result
                    for result in results
                    if result.get("status") == "FAIL"
                ]

                if failed_results:

                    findings_text = ""

                    for result in failed_results:

                        severity = result.get(
                            "severity",
                            "MEDIUM"
                        )

                        findings_text += (
                            f"- {result.get('check', 'Security Check')} "
                            f"(Severity: {severity}): "
                            f"{result.get('message', '')}\n"
                        )

                    # -------------------------------------------------
                    # TRY GEMINI AI
                    # -------------------------------------------------

                    with st.spinner(
                        "🤖 CYPhora AI is analyzing the findings..."
                    ):

                        try:

                            ai_result = get_ai_recommendation(
                                vendor,
                                findings_text
                            )

                            if ai_result and str(ai_result).strip():

                                st.session_state.ai_result = ai_result

                                st.markdown(
                                    '<div class="ai-card">',
                                    unsafe_allow_html=True
                                )

                                st.markdown(
                                    "### 🧠 CYPhora AI Recommendations"
                                )

                                st.markdown(
                                    ai_result
                                )

                                st.markdown(
                                    "</div>",
                                    unsafe_allow_html=True
                                )

                                st.success(
                                    "✅ AI-assisted security recommendations generated successfully."
                                )

                            else:

                                raise Exception(
                                    "AI service unavailable"
                                )

                        # -------------------------------------------------
                        # AI UNAVAILABLE → AUTOMATED CYPhora ANALYSIS
                        # -------------------------------------------------

                        except Exception:

                            fallback_recommendations = []

                            for result in failed_results:

                                check_name = result.get(
                                    "check",
                                    "Security Check"
                                )

                                severity = result.get(
                                    "severity",
                                    "MEDIUM"
                                )

                                message = result.get(
                                    "message",
                                    ""
                                )

                                recommendation = (
                                    f"**{check_name}** "
                                    f"({severity} severity): "
                                    f"Review and remediate this configuration issue. "
                                    f"{message}"
                                )

                                fallback_recommendations.append(
                                    recommendation
                                )

                            # -------------------------------------------------
                            # PRESENTATION-READY FALLBACK
                            # -------------------------------------------------

                            fallback_text = (
                                "### 🛡️ CYPhora Automated Security Recommendations\n\n"
                                "Recommendations generated from the detected "
                                "compliance findings.\n\n"
                            )

                            for index, recommendation in enumerate(
                                fallback_recommendations,
                                start=1
                            ):

                                fallback_text += (
                                    f"**{index}.** {recommendation}\n\n"
                                )

                            fallback_text += (
                                "---\n\n"
                                "💡 **Next Step:** "
                                "Remediate the failed security controls "
                                "and run the audit again to verify the "
                                "security improvement."
                            )

                            st.session_state.ai_result = fallback_text

                            st.markdown(
                                '<div class="ai-card">',
                                unsafe_allow_html=True
                            )

                            st.markdown(
                                fallback_text
                            )

                            st.markdown(
                                "</div>",
                                unsafe_allow_html=True
                            )

                            st.info(
                                "ℹ️ Recommendations generated using "
                                "CYPhora's automated compliance analysis engine."
                            )

                else:

                    st.session_state.ai_result = (
                        "🤖 **All security checks passed.** "
                        "No remediation analysis is required."
                    )

                    st.success(
                        "🤖 All checks passed. "
                        "No remediation analysis is required."
                    )

                st.write("")

                # -------------------------------------------------
                # CONFIGURATION PREVIEW
                # -------------------------------------------------

                st.subheader("📄 Configuration Preview")

                with st.expander(
                    "View uploaded configuration"
                ):

                    st.code(
                        config_text,
                        language="text"
                    )

                # -------------------------------------------------
                # AUDIT INFORMATION
                # -------------------------------------------------

                st.subheader("ℹ️ Audit Information")

                info1, info2, info3 = st.columns(3)

                with info1:

                    st.write("**Vendor**")
                    st.write(vendor)

                with info2:

                    st.write("**Configuration**")
                    st.write(uploaded_file.name)

                with info3:

                    st.write("**Audit Status**")
                    st.write(report_status)

            else:

                st.warning(
                    "⚠️ No compliance checks were returned for this vendor."
                )


# =========================================================
# REPORTS
# =========================================================

with tab3:

    st.header("📊 Security Audit Reports")

    report = st.session_state.audit_report
    report_results = st.session_state.audit_results

    if report is None:

        st.info(
            "🟡 No audit report is available yet. "
            "Perform a security audit first."
        )

    else:

        # -------------------------------------------------
        # REPORT HEADER
        # -------------------------------------------------

        st.subheader("📋 Audit Summary")

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Vendor",
                report["vendor"]
            )

        with col2:

            st.metric(
                "Compliance Score",
                f"{report['score']}%"
            )

        with col3:

            st.metric(
                "Passed",
                report["passed"]
            )

        with col4:

            st.metric(
                "Failed",
                report["failed"]
            )

        st.write("")

        st.write(
            f"**Configuration File:** `{report['filename']}`"
        )

        st.write(
            f"**Overall Status:** **{report['status']}**"
        )

        # -------------------------------------------------
        # REPORT STATUS
        # -------------------------------------------------

        if report["score"] == 100:

            st.success(
                "🟢 All security checks passed."
            )

        elif report["score"] >= 70:

            st.warning(
                "🟠 Some security checks require attention."
            )

        else:

            st.error(
                "🔴 Critical security gaps were detected."
            )

        st.write("")

        # -------------------------------------------------
        # BEFORE / AFTER SECURITY IMPROVEMENT
        # -------------------------------------------------

        st.subheader("🔄 Security Improvement Lab")

        st.caption(
            "Compare an earlier configuration with an improved configuration "
            "and measure the security posture change."
        )

        before_file = st.file_uploader(
            "Upload the earlier configuration",
            type=["txt", "cfg", "conf"],
            key="before_after_before"
        )

        after_file = st.file_uploader(
            "Upload the improved configuration",
            type=["txt", "cfg", "conf"],
            key="before_after_after"
        )

        if before_file is not None and after_file is not None:

            try:

                before_text = before_file.read().decode("utf-8")
                after_text = after_file.read().decode("utf-8")

                before_vendor = detect_vendor(before_text)
                after_vendor = detect_vendor(after_text)

                if before_vendor == "Unknown" or after_vendor == "Unknown":

                    st.warning(
                        "⚠️ CYPhora could not detect the vendor in both files. "
                        "Please upload supported network configurations."
                    )

                elif before_vendor != after_vendor:

                    st.warning(
                        f"⚠️ The files belong to different vendors "
                        f"({before_vendor} vs {after_vendor}). "
                        "Use configurations from the same vendor for a meaningful comparison."
                    )

                else:

                    def run_vendor_audit(vendor_name, config):

                        if vendor_name == "Cisco":

                            return check_cisco_compliance(config)

                        elif vendor_name == "Fortinet":

                            return check_fortinet_compliance(config)

                        elif vendor_name == "Palo Alto":

                            return check_paloalto_compliance(config)

                        elif vendor_name == "Juniper":

                            return check_juniper_compliance(config)

                        elif vendor_name == "Arista":

                            return check_arista_compliance(config)

                        elif vendor_name == "Check Point":

                            return check_checkpoint_compliance(config)

                        return []

                    before_results = run_vendor_audit(
                        before_vendor,
                        before_text
                    )

                    after_results = run_vendor_audit(
                        after_vendor,
                        after_text
                    )

                    before_passed = sum(
                        1
                        for r in before_results
                        if r.get("status") == "PASS"
                    )

                    after_passed = sum(
                        1
                        for r in after_results
                        if r.get("status") == "PASS"
                    )

                    before_failed = sum(
                        1
                        for r in before_results
                        if r.get("status") == "FAIL"
                    )

                    after_failed = sum(
                        1
                        for r in after_results
                        if r.get("status") == "FAIL"
                    )

                    before_total = len(before_results)
                    after_total = len(after_results)

                    before_score = int(
                        (before_passed / before_total) * 100
                    ) if before_total else 0

                    after_score = int(
                        (after_passed / after_total) * 100
                    ) if after_total else 0

                    score_change = after_score - before_score
                    finding_change = before_failed - after_failed

                    b1, b2, b3, b4 = st.columns(4)

                    with b1:

                        st.metric(
                            "Before Score",
                            f"{before_score}%"
                        )

                    with b2:

                        st.metric(
                            "After Score",
                            f"{after_score}%",
                            delta=f"{score_change:+d}%"
                        )

                    with b3:

                        st.metric(
                            "Findings Before",
                            before_failed
                        )

                    with b4:

                        st.metric(
                            "Findings After",
                            after_failed,
                            delta=f"{-finding_change:+d}"
                        )

                    st.write("")

                    if score_change > 0:

                        st.success(
                            f"📈 Security posture improved by "
                            f"**{score_change} percentage points**."
                        )

                    elif score_change == 0:

                        st.info(
                            "ℹ️ The compliance score did not change."
                        )

                    else:

                        st.warning(
                            f"📉 Security posture decreased by "
                            f"**{abs(score_change)} percentage points**."
                        )

                    comparison_df = pd.DataFrame(
                        {
                            "Stage": [
                                "Before",
                                "After"
                            ],
                            "Compliance Score": [
                                before_score,
                                after_score
                            ],
                            "Passed": [
                                before_passed,
                                after_passed
                            ],
                            "Failed": [
                                before_failed,
                                after_failed
                            ]
                        }
                    )

                    st.bar_chart(
                        comparison_df.set_index("Stage")[
                            ["Compliance Score"]
                        ]
                    )

                    st.markdown("##### 🔎 Finding Changes")

                    before_checks = {
                        r.get("check", "Security Check"): r
                        for r in before_results
                    }

                    after_checks = {
                        r.get("check", "Security Check"): r
                        for r in after_results
                    }

                    all_checks = list(
                        dict.fromkeys(
                            list(before_checks.keys())
                            + list(after_checks.keys())
                        )
                    )

                    comparison_rows = []

                    for check in all_checks:

                        before_status = before_checks.get(
                            check,
                            {}
                        ).get(
                            "status",
                            "—"
                        )

                        after_status = after_checks.get(
                            check,
                            {}
                        ).get(
                            "status",
                            "—"
                        )

                        if (
                            before_status == "FAIL"
                            and after_status == "PASS"
                        ):

                            change = "🟢 Resolved"

                        elif (
                            before_status == "PASS"
                            and after_status == "FAIL"
                        ):

                            change = "🔴 Regressed"

                        elif before_status == after_status:

                            change = "⚪ Unchanged"

                        else:

                            change = "🟡 Changed"

                        comparison_rows.append(
                            {
                                "Security Check": check,
                                "Before": before_status,
                                "After": after_status,
                                "Change": change
                            }
                        )

                    st.dataframe(
                        pd.DataFrame(comparison_rows),
                        use_container_width=True,
                        hide_index=True
                    )

                    st.info(
                        f"🎯 **Demo flow:** Detect → Audit → Fix → "
                        f"Re-audit → Verify improvement. "
                        f"Vendor detected: **{before_vendor}**."
                    )

            except UnicodeDecodeError:

                st.error(
                    "❌ One of the files could not be read. "
                    "Please use UTF-8 text configuration files."
                )

        else:

            st.info(
                "💡 Upload both an earlier and improved configuration "
                "to demonstrate measurable security improvement."
            )

        st.write("")

        # -------------------------------------------------
        # RISK SUMMARY
        # -------------------------------------------------

        st.subheader("🚨 Risk Summary")

        c1, c2, c3 = st.columns(3)

        with c1:

            st.metric(
                "HIGH",
                report.get("high", 0)
            )

        with c2:

            st.metric(
                "MEDIUM",
                report.get("medium", 0)
            )

        with c3:

            st.metric(
                "LOW",
                report.get("low", 0)
            )

        st.write("")

        # -------------------------------------------------
        # FINDINGS TABLE
        # -------------------------------------------------

        st.subheader("🔎 Audit Findings")

        if report_results:

            table_data = []

            for result in report_results:

                table_data.append(
                    {
                        "Check": result.get(
                            "check",
                            "Security Check"
                        ),

                        "Status": result.get(
                            "status",
                            "FAIL"
                        ),

                        "Severity": result.get(
                            "severity",
                            "MEDIUM"
                        ),

                        "Details": result.get(
                            "message",
                            ""
                        )
                    }
                )

            findings_df = pd.DataFrame(
                table_data
            )

            st.dataframe(
                findings_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info(
                "No detailed findings available."
            )

        st.write("")

        # -------------------------------------------------
        # AI REPORT
        # -------------------------------------------------

        if st.session_state.ai_result:

            st.subheader(
                "🤖 AI Security Recommendations"
            )

            st.markdown(
                st.session_state.ai_result
            )

        st.write("")

        # -------------------------------------------------
        # DOWNLOAD PDF REPORT
        # -------------------------------------------------

        st.subheader("⬇️ Download Audit Report")

        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        title_style = styles["Title"]
        title_style.alignment = TA_CENTER

        heading_style = styles["Heading2"]
        normal_style = styles["BodyText"]

        story = []

        # -------------------------------------------------
        # PDF TITLE
        # -------------------------------------------------

        story.append(
            Paragraph(
                "CYPhora Security Compliance Audit Report",
                title_style
            )
        )

        story.append(
            Spacer(1, 15)
        )

        # -------------------------------------------------
        # PDF AUDIT INFORMATION
        # -------------------------------------------------

        story.append(
            Paragraph(
                f"<b>Vendor:</b> "
                f"{escape(str(report['vendor']))}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Configuration File:</b> "
                f"{escape(str(report['filename']))}",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Compliance Score:</b> "
                f"{report['score']}%",
                normal_style
            )
        )

        story.append(
            Paragraph(
                f"<b>Overall Status:</b> "
                f"{escape(str(report['status']))}",
                normal_style
            )
        )

        story.append(
            Spacer(1, 15)
        )

        # -------------------------------------------------
        # PDF AUDIT SUMMARY
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Audit Summary",
                heading_style
            )
        )

        summary_data = [
            ["Metric", "Count"],
            ["Passed", str(report["passed"])],
            ["Failed", str(report["failed"])],
            ["High Severity", str(report.get("high", 0))],
            ["Medium Severity", str(report.get("medium", 0))],
            ["Low Severity", str(report.get("low", 0))]
        ]

        summary_table = Table(
            summary_data,
            colWidths=[250, 100]
        )

        summary_table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.grey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "ALIGN",
                        (1, 1),
                        (1, -1),
                        "CENTER"
                    ),
                    (
                        "VALIGN",
                        (0, 0),
                        (-1, -1),
                        "MIDDLE"
                    ),
                    (
                        "PADDING",
                        (0, 0),
                        (-1, -1),
                        7
                    )
                ]
            )
        )

        story.append(
            summary_table
        )

        story.append(
            Spacer(1, 20)
        )

        # -------------------------------------------------
        # PDF DETAILED FINDINGS
        # -------------------------------------------------

        story.append(
            Paragraph(
                "Detailed Security Findings",
                heading_style
            )
        )

        for result in report_results:

            check_name = result.get(
                "check",
                "Security Check"
            )

            status = result.get(
                "status",
                "FAIL"
            )

            severity = result.get(
                "severity",
                "MEDIUM"
            )

            message = result.get(
                "message",
                ""
            )

            story.append(
                Paragraph(
                    f"<b>{escape(str(status))} — "
                    f"{escape(str(check_name))}</b>",
                    normal_style
                )
            )

            story.append(
                Paragraph(
                    f"<b>Severity:</b> "
                    f"{escape(str(severity))}",
                    normal_style
                )
            )

            story.append(
                Paragraph(
                    f"<b>Details:</b> "
                    f"{escape(str(message))}",
                    normal_style
                )
            )

            story.append(
                Spacer(1, 10)
            )

        # -------------------------------------------------
        # PDF AI / AUTOMATED RECOMMENDATIONS
        # -------------------------------------------------

        if st.session_state.ai_result:

            story.append(
                Paragraph(
                    "Security Recommendations",
                    heading_style
                )
            )

            ai_text = str(
                st.session_state.ai_result
            )

            for line in ai_text.split("\n"):

                line = line.strip()

                if line:

                    story.append(
                        Paragraph(
                            escape(line),
                            normal_style
                        )
                    )

                    story.append(
                        Spacer(1, 5)
                    )

        # -------------------------------------------------
        # BUILD PDF
        # -------------------------------------------------

        doc.build(story)

        pdf_data = buffer.getvalue()

        st.download_button(
            label="📥 Download CYPhora Audit Report as PDF",
            data=pdf_data,
            file_name="CYPhora_Audit_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        🛡️ <b>CYPhora</b> — AI-Driven Multi-Vendor Network Security
        Compliance Auditor<br>
        SIH 2026 Project • Defensive Security & Compliance
    </div>
    """,
    unsafe_allow_html=True
)