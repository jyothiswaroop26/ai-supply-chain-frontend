import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from components.data_upload import render_data_upload
from components.data_view import render_data_view
from components.forecast_view import render_forecast_view
from components.kpi import render_kpi
from components.filters import render_filters

# Configuration values
USER_EMAIL = "pallajyothiswaroopkumar@gmail.com"
USER_NAME = "jyothiswaroop26"

# Initialize session state
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None

st.set_page_config(
    page_title="AI Supply Chain Dashboard",
    page_icon="📦",
    layout="wide",
)

# Load and inject custom CSS
def load_custom_css():
    """Load and inject custom CSS styling."""
    css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as css_file:
            css_content = css_file.read()
            st.markdown(
                f"<style>{css_content}</style>",
                unsafe_allow_html=True
            )

# Inject custom CSS at the beginning
load_custom_css()

st.markdown("""
<div class="app-hero">
  <div class="app-hero-inner">
    <div class="app-hero-icon">📦</div>
    <div>
      <div class="app-hero-title">AI Supply Chain Dashboard</div>
      <div class="app-hero-subtitle">Data-driven insights · Demand forecasting · Supplier intelligence</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Navigation")
    section = st.radio(
        "Select section",
        [
            "Overview",
            "Data Upload",
            "Filters & Search",
            "Data Visualization",
            "KPIs",
            "Inventory",
            "Demand Forecast",
            "Supplier Insights",
            "Settings",
        ],
    )
    st.markdown("---")
    st.markdown("Use this sidebar to switch views and control high-level app options.")

if section == "Overview":
    with st.spinner("Loading Overview..."):
        st.markdown('<div class="section-header"><span class="section-header-accent"></span>Overview</div>', unsafe_allow_html=True)

        df = st.session_state.get("uploaded_df")
        if df is not None:
            rows, cols = df.shape
            numeric_count = len(df.select_dtypes(include=["number"]).columns)
            missing_pct = round(df.isnull().sum().sum() / max(df.size, 1) * 100, 1)
            st.markdown(f"""
<div class="overview-stats-bar">
  <div class="overview-stat">
    <div class="overview-stat-value">{rows:,}</div>
    <div class="overview-stat-label">Rows</div>
  </div>
  <div class="overview-stat">
    <div class="overview-stat-value">{cols}</div>
    <div class="overview-stat-label">Columns</div>
  </div>
  <div class="overview-stat">
    <div class="overview-stat-value">{numeric_count}</div>
    <div class="overview-stat-label">Numeric Cols</div>
  </div>
  <div class="overview-stat">
    <div class="overview-stat-value">{missing_pct}%</div>
    <div class="overview-stat-label">Missing Values</div>
  </div>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="empty-state">
  <div class="empty-state-icon">📂</div>
  <div class="empty-state-title">No data loaded yet</div>
  <div class="empty-state-body">Upload a CSV in <strong>Data Upload</strong> to see your dashboard come to life.</div>
</div>
""", unsafe_allow_html=True)

        st.info("Add executive summary cards, KPIs, and dashboard highlights here.")

elif section == "Data Upload":
    with st.spinner("Loading Data Upload..."):
        render_data_upload()

elif section == "Filters & Search":
    with st.spinner("Loading Filters..."):
        render_filters()

elif section == "Data Visualization":
    with st.spinner("Loading Data Visualization..."):
        render_data_view()

elif section == "KPIs":
    with st.spinner("Loading KPIs..."):
        render_kpi()

elif section == "Inventory":
    with st.spinner("Loading Inventory..."):
        st.markdown('<div class="section-header"><span class="section-header-accent"></span>Inventory</div>', unsafe_allow_html=True)
        st.info("Add inventory levels, reorder alerts, and stock movement charts here.")

elif section == "Demand Forecast":
    with st.spinner("Loading Demand Forecast..."):
        render_forecast_view()

elif section == "Supplier Insights":
    with st.spinner("Loading Supplier Insights..."):
        st.markdown('<div class="section-header"><span class="section-header-accent"></span>Supplier Insights</div>', unsafe_allow_html=True)
        st.info("Add supplier performance, lead time analysis, and risk scoring here.")

elif section == "Settings":
    with st.spinner("Loading Settings..."):
        st.markdown('<div class="section-header"><span class="section-header-accent"></span>Settings</div>', unsafe_allow_html=True)
        st.write("Application configuration and user info")
        st.markdown(f"**Mail ID:** {USER_EMAIL}")
        st.markdown(f"**User name:** {USER_NAME}")
        st.info("Add user preferences, data source configuration, and app controls here.")
