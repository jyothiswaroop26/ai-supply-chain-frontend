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

st.title("AI Supply Chain Dashboard")
st.markdown("Welcome to the AI Supply Chain frontend dashboard. Use the sidebar to navigate between sections and explore data-driven supply chain insights.")

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
    st.header("Overview")
    st.write("Placeholder content for the Overview section.")
    st.info("Add executive summary cards, KPIs, and dashboard highlights here.")

elif section == "Data Upload":
    render_data_upload()

elif section == "Filters & Search":
    render_filters()

elif section == "Data Visualization":
    render_data_view()

elif section == "KPIs":
    render_kpi()

elif section == "Inventory":
    st.header("Inventory")
    st.write("Placeholder content for the Inventory section.")
    st.info("Add inventory levels, reorder alerts, and stock movement charts here.")

elif section == "Demand Forecast":
    render_forecast_view()

elif section == "Supplier Insights":
    st.header("Supplier Insights")
    st.write("Placeholder content for the Supplier Insights section.")
    st.info("Add supplier performance, lead time analysis, and risk scoring here.")

elif section == "Settings":
    st.header("Settings")
    st.write("Application configuration and user info")
    st.markdown(f"**Mail ID:** {USER_EMAIL}")
    st.markdown(f"**User name:** {USER_NAME}")
    st.info("Add user preferences, data source configuration, and app controls here.")
