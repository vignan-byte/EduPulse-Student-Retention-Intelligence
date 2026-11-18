"""Premium Enterprise SaaS Dark Theme & Design System for Student Retention Intelligence.
Inspired by Linear, Vercel, and Stripe dashboards.
"""

def inject_theme():
    import streamlit as st
    st.markdown("""
<style>
/* Base Dark Theme Overrides */
:root {
    --bg-primary: #0B1020;
    --bg-sidebar: #111827;
    --bg-card: #172033;
    --bg-card-hover: #1E2A42;
    --accent-blue: #3B82F6;
    --accent-cyan: #22D3EE;
    --success: #10B981;
    --warning: #F59E0B;
    --critical: #EF4444;
    --text-primary: #F8FAFC;
    --text-secondary: #94A3B8;
    --border-subtle: rgba(255, 255, 255, 0.08);
    --border-accent: rgba(59, 130, 246, 0.3);
}

/* Fix Streamlit Header & Toolbar White Strip */
[data-testid="stHeader"], header[data-testid="stHeader"], .stApp > header {
    background-color: #0B1020 !important;
    color: #F8FAFC !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}

[data-testid="stToolbar"] {
    color: #F8FAFC !important;
    background-color: transparent !important;
}

[data-testid="stDecoration"] {
    background-image: linear-gradient(90deg, #3B82F6, #22D3EE) !important;
    height: 3px !important;
}

/* App Background & Layout */
.stApp {
    background-color: #0B1020 !important;
    color: #F8FAFC !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

.block-container {
    max-width: 1400px !important;
    padding-top: 1.2rem !important;
    padding-bottom: 3rem !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #111827 !important;
    border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.5rem !important;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    color: #F8FAFC !important;
    font-weight: 600 !important;
    letter-spacing: -0.025em !important;
}

p, span, label, div {
    color: #F8FAFC;
}

/* Metrics Cards - Prevent Value & Label Clipping */
[data-testid="stMetric"] {
    background: #172033 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25) !important;
    transition: transform 0.15s ease, border-color 0.15s ease;
    min-height: 110px !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(59, 130, 246, 0.4) !important;
}

[data-testid="stMetricLabel"] p {
    color: #94A3B8 !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
    white-space: normal !important;
    word-break: break-word !important;
}

[data-testid="stMetricValue"] div {
    color: #F8FAFC !important;
    font-size: 1.55rem !important;
    font-weight: 700 !important;
    white-space: normal !important;
    word-break: break-word !important;
}

/* Custom Card Classes */
.saas-card {
    background: #172033;
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.25);
}

.saas-card-accent {
    background: linear-gradient(145deg, #172033 0%, #151D2E 100%);
    border: 1px solid rgba(34, 211, 238, 0.25);
    border-radius: 12px;
    padding: 22px;
    margin-bottom: 20px;
}

.saas-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-bottom: 12px;
    margin-bottom: 18px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

/* Status Badges & Pills */
.badge-critical {
    background: rgba(239, 68, 68, 0.18);
    color: #F87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-block;
}

.badge-moderate {
    background: rgba(245, 158, 11, 0.18);
    color: #FBBF24;
    border: 1px solid rgba(245, 158, 11, 0.4);
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-block;
}

.badge-success {
    background: rgba(16, 185, 129, 0.18);
    color: #34D399;
    border: 1px solid rgba(16, 185, 129, 0.4);
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-block;
}

.badge-info {
    background: rgba(59, 130, 246, 0.18);
    color: #60A5FA;
    border: 1px solid rgba(59, 130, 246, 0.4);
    padding: 4px 12px;
    border-radius: 9999px;
    font-weight: 600;
    font-size: 0.8rem;
    display: inline-block;
}

/* Custom Hero Bar */
.hero-banner {
    background: linear-gradient(135deg, #111827 0%, #172033 100%);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-left: 4px solid #3B82F6;
    padding: 20px 24px;
    border-radius: 12px;
    margin-bottom: 22px;
}

/* Button & Form Controls */
.stButton button {
    background: #1E293B !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255, 255, 255, 0.14) !important;
    border-radius: 8px !important;
    padding: 8px 18px !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
}

.stButton button:hover {
    background: #2563EB !important;
    border-color: #3B82F6 !important;
    color: white !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}

.stButton button[kind="primary"] {
    background: linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%) !important;
    border: 1px solid #3B82F6 !important;
}

/* Input boxes & dropdowns */
.stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
    background-color: #111827 !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255, 255, 255, 0.16) !important;
    border-radius: 8px !important;
}

.stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus, .stTextArea textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3) !important;
}

/* BaseWeb Select Popovers & Menus (Dark Theme Consistency) */
div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
    background-color: #111827 !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 8px !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5) !important;
}

li[role="option"] {
    color: #F8FAFC !important;
    background-color: #111827 !important;
    padding: 10px 14px !important;
}

li[role="option"]:hover, li[role="option"][aria-selected="true"] {
    background-color: #1E2A42 !important;
    color: #38BDF8 !important;
}

/* WCAG AA Accessible Alert Notifications */
[data-testid="stAlert"] {
    border-radius: 8px !important;
    padding: 14px 18px !important;
}

[data-testid="stAlert"] p, [data-testid="stAlert"] div {
    color: #F8FAFC !important;
    font-weight: 500 !important;
}

div[data-baseweb="notification"][kind="error"], div[data-testid="stAlert"]:has([data-testid="stNotificationContentError"]) {
    background-color: #450A0A !important;
    border: 1px solid #DC2626 !important;
}

div[data-baseweb="notification"][kind="warning"], div[data-testid="stAlert"]:has([data-testid="stNotificationContentWarning"]) {
    background-color: #451A03 !important;
    border: 1px solid #D97706 !important;
}

div[data-baseweb="notification"][kind="info"], div[data-testid="stAlert"]:has([data-testid="stNotificationContentInfo"]) {
    background-color: #172554 !important;
    border: 1px solid #2563EB !important;
}

div[data-baseweb="notification"][kind="success"], div[data-testid="stAlert"]:has([data-testid="stNotificationContentSuccess"]) {
    background-color: #064E3B !important;
    border: 1px solid #059669 !important;
}

/* Tooltips */
[data-testid="stTooltipContent"], div[role="tooltip"] {
    background-color: #1F2937 !important;
    color: #F8FAFC !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    font-size: 0.85rem !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
}

/* Dataframe & Tables */
[data-testid="stDataFrame"] {
    background-color: #172033 !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 10px !important;
}

/* Expanders */
.streamlit-expanderHeader {
    background-color: #172033 !important;
    color: #F8FAFC !important;
    border-radius: 8px !important;
}

/* Radio Navigation in Sidebar */
[data-testid="stSidebar"] .stRadio > div {
    gap: 4px;
}

[data-testid="stSidebar"] .stRadio label {
    padding: 8px 12px !important;
    border-radius: 8px !important;
    transition: background 0.15s ease;
    font-weight: 500 !important;
}

[data-testid="stSidebar"] .stRadio label:hover {
    background-color: rgba(255, 255, 255, 0.05) !important;
}
</style>
""", unsafe_allow_html=True)


def get_plotly_layout_defaults():
    """Return dark SaaS theme layout dictionary for Plotly charts."""
    return dict(
        paper_bgcolor="#172033",
        plot_bgcolor="#172033",
        font=dict(color="#94A3B8", family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"),
        xaxis=dict(gridcolor="rgba(255, 255, 255, 0.06)", zerolinecolor="rgba(255, 255, 255, 0.1)"),
        yaxis=dict(gridcolor="rgba(255, 255, 255, 0.06)", zerolinecolor="rgba(255, 255, 255, 0.1)"),
        margin=dict(l=15, r=15, t=35, b=25),
        legend=dict(font=dict(color="#F8FAFC"))
    )
