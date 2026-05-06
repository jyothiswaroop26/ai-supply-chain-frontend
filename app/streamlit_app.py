import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from components.data_upload import render_data_upload
from components.data_view import render_data_view

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

st.title("AI Supply Chain Dashboard")
st.markdown("Welcome to the AI Supply Chain frontend dashboard. Use the sidebar to navigate between sections and explore data-driven supply chain insights.")

with st.sidebar:
    st.header("Navigation")
    section = st.radio(
        "Select section",
        [
            "Overview",
            "Data Upload",
            "Data Visualization",
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

elif section == "Data Visualization":
    render_data_view()

elif section == "Inventory":
    st.header("Inventory")
    st.write("Placeholder content for the Inventory section.")
    st.info("Add inventory levels, reorder alerts, and stock movement charts here.")

elif section == "Demand Forecast":
    st.header("Demand Forecast")
    st.write("Placeholder content for the Demand Forecast section.")
    st.info("Add forecast charts, trend analysis, and scenario planning tools here.")

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
