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
# CUSTOM CSS — CYPhora PROFESSIONAL CYBERSECURITY THEME
# =========================================================

st.markdown(
    """
    <style>

    /* =====================================================
       GLOBAL APPLICATION
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 15% 10%,
                rgba(37, 99, 235, 0.10),
                transparent 28%
            ),
            radial-gradient(
                circle at 85% 20%,
                rgba(6, 182, 212, 0.08),
                transparent 25%
            ),
            #07111f;
        color: #e5edf7;
    }

    [data-testid="stAppViewContainer"] {
        background: transparent;
    }

    [data-testid="stHeader"] {
        background: rgba(7, 17, 31, 0.80);
    }

    [data-testid="stToolbar"] {
        background: transparent;
    }

    .main {
        padding-top: 0.5rem;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }


    /* =====================================================
       SIDEBAR
       ===================================================== */

    [data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                #081525 0%,
                #0b1728 50%,
                #07111f 100%
            );
        border-right: 1px solid rgba(56, 189, 248, 0.14);
    }

    [data-testid="stSidebar"] * {
        color: #dbeafe;
    }


    /* =====================================================
       TAB NAVIGATION
       ===================================================== */

    [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(10, 25, 43, 0.72);
        padding: 7px;
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.14);
        margin-bottom: 24px;
    }

    [data-baseweb="tab"] {
        height: 48px;
        padding: 0 22px;
        border-radius: 10px;
        color: #94a3b8;
        font-weight: 650;
        background: transparent;
    }

    [data-baseweb="tab"]:hover {
        color: #e0f2fe;
        background: rgba(14, 165, 233, 0.08);
    }

    [aria-selected="true"] {
        color: #ffffff !important;
        background:
            linear-gradient(
                135deg,
                rgba(37, 99, 235, 0.32),
                rgba(6, 182, 212, 0.18)
            ) !important;
        border: 1px solid rgba(56, 189, 248, 0.30);
    }


    /* =====================================================
       HEADINGS
       ===================================================== */

    h1, h2, h3, h4 {
        color: #f8fafc !important;
        letter-spacing: -0.3px;
    }

    h3 {
        margin-top: 20px;
    }

    p {
        color: #cbd5e1;
    }


    /* =====================================================
       MAIN HERO
       ===================================================== */

    .hero {
        padding: 30px;
        border-radius: 20px;
        background:
            radial-gradient(
                circle at 85% 20%,
                rgba(34, 211, 238, 0.18),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #071426 0%,
                #0b1e3a 48%,
                #0f3b66 100%
            );
        color: white;
        margin-bottom: 25px;
        border: 1px solid rgba(56, 189, 248, 0.25);
        box-shadow:
            0 15px 45px rgba(0, 0, 0, 0.28),
            inset 0 1px 0 rgba(255,255,255,0.04);
    }

    .hero-title {
        font-size: 44px;
        font-weight: 850;
        margin-bottom: 5px;
        letter-spacing: -1px;
    }

    .hero-subtitle {
        font-size: 18px;
        color: #bfdbfe;
        margin-bottom: 12px;
    }

    .hero-tag {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: rgba(14, 165, 233, 0.13);
        border: 1px solid rgba(56, 189, 248, 0.28);
        color: #dff6ff;
        font-size: 13px;
        margin-right: 6px;
    }


    /* =====================================================
       DASHBOARD HERO
       ===================================================== */

    .dashboard-hero {
        position: relative;
        overflow: hidden;
        padding: 38px 40px;
        border-radius: 24px;
        background:
            radial-gradient(
                circle at 88% 18%,
                rgba(34, 211, 238, 0.20),
                transparent 25%
            ),
            radial-gradient(
                circle at 65% 100%,
                rgba(59, 130, 246, 0.15),
                transparent 30%
            ),
            linear-gradient(
                135deg,
                #06111f 0%,
                #0a1e38 50%,
                #0c3154 100%
            );
        color: white;
        margin-bottom: 28px;
        border: 1px solid rgba(56, 189, 248, 0.28);
        box-shadow:
            0 20px 55px rgba(0, 0, 0, 0.30),
            inset 0 1px 0 rgba(255,255,255,0.05);
    }

    .dashboard-hero::after {
        content: "";
        position: absolute;
        width: 220px;
        height: 220px;
        right: -70px;
        top: -80px;
        border-radius: 50%;
        border: 1px solid rgba(56, 189, 248, 0.12);
        box-shadow:
            0 0 0 30px rgba(56, 189, 248, 0.025),
            0 0 0 60px rgba(56, 189, 248, 0.018);
    }

    .dashboard-hero-title {
        font-size: 42px;
        font-weight: 850;
        letter-spacing: -1px;
        margin-bottom: 7px;
        position: relative;
        z-index: 1;
    }

    .dashboard-hero-text {
        color: #bfdbfe;
        font-size: 16px;
        margin-bottom: 18px;
        position: relative;
        z-index: 1;
    }

    .dashboard-badge {
        display: inline-block;
        padding: 7px 13px;
        border-radius: 999px;
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(125, 211, 252, 0.22);
        color: #dbeafe;
        font-size: 12px;
        margin-right: 7px;
        position: relative;
        z-index: 1;
    }


    /* =====================================================
       DASHBOARD CARDS
       ===================================================== */

    .dashboard-card {
        padding: 22px;
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.13);
        background:
            linear-gradient(
                145deg,
                rgba(15, 31, 50, 0.94),
                rgba(9, 23, 39, 0.92)
            );
        min-height: 125px;
        box-shadow:
            0 10px 28px rgba(0, 0, 0, 0.20),
            inset 0 1px 0 rgba(255,255,255,0.025);
        transition:
            transform 0.18s ease,
            border-color 0.18s ease,
            box-shadow 0.18s ease;
    }

    .dashboard-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.28);
        box-shadow:
            0 15px 35px rgba(0, 0, 0, 0.28),
            0 0 25px rgba(14, 165, 233, 0.06);
    }

    .dashboard-card-title {
        font-size: 13px;
        color: #94a3b8;
        margin-bottom: 8px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .dashboard-card-value {
        font-size: 29px;
        font-weight: 850;
        color: #f8fafc;
        line-height: 1.1;
    }

    .dashboard-card-subtitle {
        font-size: 12px;
        color: #64748b;
        margin-top: 7px;
        line-height: 1.4;
    }


    /* =====================================================
       WORKFLOW CARDS
       ===================================================== */

    .workflow-card {
        padding: 21px 15px;
        border-radius: 17px;
        border: 1px solid rgba(148, 163, 184, 0.13);
        background:
            linear-gradient(
                145deg,
                rgba(14, 30, 49, 0.96),
                rgba(8, 21, 36, 0.96)
            );
        min-height: 155px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.20);
        transition:
            transform 0.18s ease,
            border-color 0.18s ease;
    }

    .workflow-card:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.30);
    }

    .workflow-number {
        font-size: 29px;
        margin-bottom: 9px;
    }

    .workflow-title {
        font-weight: 750;
        color: #f1f5f9;
        margin-bottom: 7px;
    }

    .workflow-text {
        font-size: 12px;
        color: #94a3b8;
        line-height: 1.45;
    }


    /* =====================================================
       VENDOR CARDS
       ===================================================== */

    .vendor-card {
        padding: 22px;
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.14);
        background:
            linear-gradient(
                145deg,
                rgba(16, 34, 55, 0.96),
                rgba(8, 22, 38, 0.96)
            );
        text-align: center;
        min-height: 140px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.20);
        transition:
            transform 0.18s ease,
            border-color 0.18s ease,
            box-shadow 0.18s ease;
    }

    .vendor-card:hover {
        transform: translateY(-4px);
        border-color: rgba(56, 189, 248, 0.35);
        box-shadow:
            0 14px 32px rgba(0, 0, 0, 0.28),
            0 0 22px rgba(14, 165, 233, 0.06);
    }

    .vendor-name {
        font-size: 19px;
        font-weight: 750;
        color: #f8fafc;
        margin-top: 8px;
    }

    .vendor-type {
        color: #7dd3fc;
        font-size: 12px;
        margin-top: 5px;
    }


    /* =====================================================
       FRAMEWORK CARDS
       ===================================================== */

    .framework-card {
        padding: 20px;
        border-radius: 17px;
        border: 1px solid rgba(148, 163, 184, 0.13);
        background:
            linear-gradient(
                145deg,
                rgba(14, 30, 49, 0.96),
                rgba(8, 21, 36, 0.96)
            );
        min-height: 112px;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18);
        transition:
            transform 0.18s ease,
            border-color 0.18s ease;
    }

    .framework-card:hover {
        transform: translateY(-3px);
        border-color: rgba(56, 189, 248, 0.28);
    }

    .framework-title {
        font-weight: 750;
        color: #f8fafc;
        margin-bottom: 7px;
    }

    .framework-text {
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.45;
    }


    /* =====================================================
       SECTION LABEL
       ===================================================== */

    .section-label {
        color: #94a3b8;
        font-size: 13px;
        margin-top: -8px;
        margin-bottom: 17px;
    }


    /* =====================================================
       GENERAL SECTION CARD
       ===================================================== */

    .section-card {
        padding: 22px;
        border-radius: 18px;
        border: 1px solid rgba(148, 163, 184, 0.13);
        background: rgba(10, 25, 42, 0.75);
        margin-bottom: 18px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }


    /* =====================================================
       METRIC CARDS
       ===================================================== */

    .metric-card {
        padding: 19px;
        border-radius: 16px;
        border: 1px solid rgba(148, 163, 184, 0.14);
        background:
            linear-gradient(
                145deg,
                rgba(15, 32, 52, 0.94),
                rgba(8, 21, 36, 0.94)
            );
        text-align: center;
        min-height: 120px;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.18);
    }

    .metric-number {
        font-size: 30px;
        font-weight: 850;
        color: #f8fafc;
    }

    .metric-label {
        color: #94a3b8;
        font-size: 14px;
    }


    /* =====================================================
       STREAMLIT METRICS
       ===================================================== */

    [data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(15, 32, 52, 0.95),
                rgba(8, 21, 36, 0.95)
            );
        border: 1px solid rgba(148, 163, 184, 0.14);
        padding: 17px;
        border-radius: 16px;
        box-shadow: 0 7px 22px rgba(0, 0, 0, 0.18);
    }

    [data-testid="stMetricLabel"] {
        color: #94a3b8 !important;
    }

    [data-testid="stMetricValue"] {
        color: #f8fafc !important;
        font-weight: 800;
    }

    [data-testid="stMetricDelta"] {
        font-weight: 650;
    }


    /* =====================================================
       FILE UPLOADER
       ===================================================== */

    [data-testid="stFileUploader"] {
        background:
            linear-gradient(
                145deg,
                rgba(12, 29, 48, 0.95),
                rgba(7, 20, 34, 0.95)
            );
        border: 1px dashed rgba(56, 189, 248, 0.32);
        border-radius: 18px;
        padding: 8px;
    }

    [data-testid="stFileUploader"]:hover {
        border-color: rgba(56, 189, 248, 0.55);
    }

    [data-testid="stFileUploader"] section {
        border: none;
    }


    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 11px;
        border: 1px solid rgba(56, 189, 248, 0.30);
        background:
            linear-gradient(
                135deg,
                #1261a0,
                #087ea4
            );
        color: white;
        font-weight: 700;
        min-height: 42px;
        transition:
            transform 0.15s ease,
            box-shadow 0.15s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        transform: translateY(-1px);
        box-shadow:
            0 8px 22px rgba(6, 182, 212, 0.18);
        border-color: rgba(125, 211, 252, 0.55);
    }


    /* =====================================================
       INPUTS / TEXT AREAS
       ===================================================== */

    input,
    textarea {
        background-color: #0b1a2c !important;
        color: #e2e8f0 !important;
        border-color: rgba(148, 163, 184, 0.20) !important;
    }


    /* =====================================================
       EXPANDERS
       ===================================================== */

    [data-testid="stExpander"] {
        background:
            rgba(10, 25, 42, 0.75);
        border: 1px solid rgba(148, 163, 184, 0.14);
        border-radius: 15px;
    }

    [data-testid="stExpander"] summary {
        color: #dbeafe;
        font-weight: 650;
    }


    /* =====================================================
       INFO / SUCCESS / WARNING / ERROR
       ===================================================== */

    [data-testid="stAlert"] {
        border-radius: 14px;
        border-width: 1px;
    }

    .status-good {
        padding: 15px;
        border-radius: 12px;
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.35);
    }

    .status-warning {
        padding: 15px;
        border-radius: 12px;
        background: rgba(234, 179, 8, 0.10);
        border: 1px solid rgba(234, 179, 8, 0.35);
    }

    .status-danger {
        padding: 15px;
        border-radius: 12px;
        background: rgba(239, 68, 68, 0.10);
        border: 1px solid rgba(239, 68, 68, 0.35);
    }


    /* =====================================================
       AI SECURITY CARD
       ===================================================== */

    .ai-card {
        padding: 25px;
        border-radius: 19px;
        border: 1px solid rgba(129, 140, 248, 0.38);
        background:
            radial-gradient(
                circle at 90% 10%,
                rgba(129, 140, 248, 0.12),
                transparent 28%
            ),
            linear-gradient(
                145deg,
                rgba(30, 27, 75, 0.78),
                rgba(12, 24, 48, 0.90)
            );
        box-shadow:
            0 12px 35px rgba(0, 0, 0, 0.22),
            0 0 30px rgba(99, 102, 241, 0.05);
    }

    .ai-card h3 {
        color: #e0e7ff !important;
    }


    /* =====================================================
       PROGRESS BAR
       ===================================================== */

    [data-testid="stProgress"] > div {
        background-color: rgba(148, 163, 184, 0.15);
        border-radius: 999px;
    }

    [data-testid="stProgress"] > div > div {
        background:
            linear-gradient(
                90deg,
                #2563eb,
                #06b6d4
            );
        border-radius: 999px;
    }


    /* =====================================================
       DATAFRAMES / TABLES
       ===================================================== */

    [data-testid="stDataFrame"] {
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 14px;
        overflow: hidden;
    }


    /* =====================================================
       CODE BLOCKS
       ===================================================== */

    [data-testid="stCode"] {
        border-radius: 14px;
        border: 1px solid rgba(56, 189, 248, 0.12);
    }


    /* =====================================================
       DIVIDERS
       ===================================================== */

    hr {
        border-color: rgba(148, 163, 184, 0.10);
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;
        color: #64748b;
        padding-top: 40px;
        padding-bottom: 12px;
        font-size: 13px;
        border-top: 1px solid rgba(148, 163, 184, 0.08);
        margin-top: 40px;
    }

    .footer b {
        color: #7dd3fc;
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
                f"{status_icon} **{status_text}** — "
                "all configured security checks passed."
            )

        elif score >= 70:

            st.warning(
                f"{status_icon} **{status_text}** — "
                "some security controls require attention."
            )

        else:

            st.error(
                f"{status_icon} **{status_text}** — "
                "significant security gaps were detected."
            )

    st.write("")

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
                    <div class="dashboard-card-subtitle">
                        {subtitle}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

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

        for column, (icon, name, vendor_type) in zip(
            cols,
            row
        ):

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

                # =================================================
                # CYPhora AI SECURITY ANALYSIS
                # =================================================

                st.subheader("🤖 AI Security Analysis")

                failed_results = [
                    result
                    for result in results
                    if result.get("status") == "FAIL"
                ]

                if failed_results:

                    # -------------------------------------------------
                    # GENERATE SECURITY RECOMMENDATIONS
                    # -------------------------------------------------

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
                            "Configuration issue detected."
                        )

                        if severity == "HIGH":

                            recommendation = (
                                f"**{check_name}** "
                                f"({severity} severity): "
                                f"Immediate review is recommended. "
                                f"{message} "
                                f"Remediate this control and re-run "
                                f"the audit to verify that the security "
                                f"risk has been reduced."
                            )

                        elif severity == "MEDIUM":

                            recommendation = (
                                f"**{check_name}** "
                                f"({severity} severity): "
                                f"Review and remediate this configuration "
                                f"issue. {message} "
                                f"Re-run the audit after applying the "
                                f"recommended configuration change."
                            )

                        else:

                            recommendation = (
                                f"**{check_name}** "
                                f"({severity} severity): "
                                f"Review this configuration setting. "
                                f"{message} "
                                f"Apply the appropriate security hardening "
                                f"and verify the result with another audit."
                            )

                        fallback_recommendations.append(
                            recommendation
                        )

                    # -------------------------------------------------
                    # BUILD AI ANALYSIS
                    # -------------------------------------------------

                    ai_result = (
                        "### 🧠 CYPhora AI Recommendations\n\n"
                        "CYPhora analyzed the detected compliance "
                        "findings and generated security remediation "
                        "recommendations.\n\n"
                    )

                    for index, recommendation in enumerate(
                        fallback_recommendations,
                        start=1
                    ):

                        ai_result += (
                            f"**{index}.** "
                            f"{recommendation}\n\n"
                        )

                    ai_result += (
                        "---\n\n"
                        "💡 **Overall Recommendation:** "
                        "Remediate the failed security controls "
                        "and run the audit again to verify improvement."
                    )

                    # -------------------------------------------------
                    # SAVE AI RESULT
                    # -------------------------------------------------

                    st.session_state.ai_result = ai_result

                    # -------------------------------------------------
                    # DISPLAY AI RESULT
                    # -------------------------------------------------

                    st.markdown(
                        '<div class="ai-card">',
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        ai_result
                    )

                    st.markdown(
                        "</div>",
                        unsafe_allow_html=True
                    )

                    st.success(
                        "✅ CYPhora AI-assisted security analysis "
                        "completed successfully."
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
            "Compare an earlier configuration with an improved "
            "configuration and measure the security posture change."
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

                if (
                    before_vendor == "Unknown"
                    or after_vendor == "Unknown"
                ):

                    st.warning(
                        "⚠️ CYPhora could not detect the vendor in both files. "
                        "Please upload supported network configurations."
                    )

                elif before_vendor != after_vendor:

                    st.warning(
                        f"⚠️ The files belong to different vendors "
                        f"({before_vendor} vs {after_vendor}). "
                        "Use configurations from the same vendor for a "
                        "meaningful comparison."
                    )

                else:

                    def run_vendor_audit(
                        vendor_name,
                        config
                    ):

                        if vendor_name == "Cisco":

                            return check_cisco_compliance(
                                config
                            )

                        elif vendor_name == "Fortinet":

                            return check_fortinet_compliance(
                                config
                            )

                        elif vendor_name == "Palo Alto":

                            return check_paloalto_compliance(
                                config
                            )

                        elif vendor_name == "Juniper":

                            return check_juniper_compliance(
                                config
                            )

                        elif vendor_name == "Arista":

                            return check_arista_compliance(
                                config
                            )

                        elif vendor_name == "Check Point":

                            return check_checkpoint_compliance(
                                config
                            )

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

                    score_change = (
                        after_score - before_score
                    )

                    finding_change = (
                        before_failed - after_failed
                    )

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

                    st.markdown(
                        "##### 🔎 Finding Changes"
                    )

                    before_checks = {
                        r.get(
                            "check",
                            "Security Check"
                        ): r
                        for r in before_results
                    }

                    after_checks = {
                        r.get(
                            "check",
                            "Security Check"
                        ): r
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
                        pd.DataFrame(
                            comparison_rows
                        ),
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
                '<div class="ai-card">',
                unsafe_allow_html=True
            )

            st.markdown(
                st.session_state.ai_result
            )

            st.markdown(
                "</div>",
                unsafe_allow_html=True
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
            [
                "High Severity",
                str(report.get("high", 0))
            ],
            [
                "Medium Severity",
                str(report.get("medium", 0))
            ],
            [
                "Low Severity",
                str(report.get("low", 0))
            ]
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
        # PDF AI RECOMMENDATIONS
        # -------------------------------------------------

        if st.session_state.ai_result:

            story.append(
                Paragraph(
                    "AI Security Recommendations",
                    heading_style
                )
            )

            ai_text = str(
                st.session_state.ai_result
            )

            for line in ai_text.split("\n"):

                line = line.strip()

                if line:

                    # Remove markdown symbols for PDF readability
                    clean_line = (
                        line
                        .replace("**", "")
                        .replace("### ", "")
                        .replace("---", "")
                    )

                    story.append(
                        Paragraph(
                            escape(clean_line),
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