import os
import sys

import streamlit as st

sys.path.insert(0, os.path.dirname(__file__))

from components.chat_ui import render_chat_ui
from components.data_upload import render_data_upload
from components.data_view import render_data_view
from components.filters import render_filters
from components.forecast_view import render_forecast_view
from components.inventory_view import render_inventory_view
from components.kpi import render_kpi
from components.supplier_view import render_supplier_view

# Configuration values
USER_EMAIL = "pallajyothiswaroopkumar@gmail.com"
USER_NAME = "jyothiswaroop26"

# Initialize session state
if "uploaded_df" not in st.session_state:
    st.session_state.uploaded_df = None
if "nav_section" not in st.session_state:
    st.session_state.nav_section = "Dashboard + Chat"

st.set_page_config(
    page_title="AI Supply Chain Dashboard",
    page_icon="📦",
    layout="wide",
)


def load_custom_css():
    """Load and inject custom CSS styling."""
    css_path = os.path.join(os.path.dirname(__file__), "styles", "custom.css")
    if os.path.exists(css_path):
        with open(css_path, "r") as css_file:
            css_content = css_file.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)


load_custom_css()

st.markdown(
    """
<div class="app-hero">
  <div class="app-hero-inner">
    <div class="app-hero-icon">📦</div>
    <div>
      <div class="app-hero-title">AI Supply Chain Dashboard</div>
      <div class="app-hero-subtitle">Data-driven insights · Demand forecasting · Supplier intelligence</div>
    </div>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Navigation")

    quick_col1, quick_col2 = st.columns(2)
    with quick_col1:
        if st.button("Workspace", use_container_width=True):
            st.session_state.nav_section = "Dashboard + Chat"
            st.rerun()
    with quick_col2:
        if st.button("Upload", use_container_width=True):
            st.session_state.nav_section = "Data Upload"
            st.rerun()

    section = st.radio(
        "Select section",
        [
            "Dashboard + Chat",
            "Data Upload",
            "Filters & Search",
            "Data Visualization",
            "KPIs",
            "Inventory",
            "Demand Forecast",
            "Supplier Insights",
            "Settings",
        ],
        key="nav_section",
    )
    st.markdown("---")
    st.markdown("Use this sidebar to switch views and control high-level app options.")
    st.caption("Release: UI Polish Final")

if section == "Dashboard + Chat":
    with st.spinner("Loading workspace..."):
        st.markdown(
            '<div class="section-header"><span class="section-header-accent"></span>Dashboard + Chat Workspace</div>',
            unsafe_allow_html=True,
        )
        st.caption("Review your data, then ask the chatbot for insights without leaving this screen.")

        dashboard_tab, chatbot_tab = st.tabs(["Dashboard", "Chatbot"])

        with dashboard_tab:
            st.subheader("Overview")
            df = st.session_state.get("uploaded_df")
            if df is not None:
                rows, cols = df.shape
                numeric_count = len(df.select_dtypes(include=["number"]).columns)
                missing_pct = round(df.isnull().sum().sum() / max(df.size, 1) * 100, 1)
                st.markdown(
                    f"""
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
""",
                    unsafe_allow_html=True,
                )
                st.dataframe(df.head(20), use_container_width=True)
            else:
                st.markdown(
                    """
<div class="empty-state">
  <div class="empty-state-icon">📂</div>
  <div class="empty-state-title">No data loaded yet</div>
  <div class="empty-state-body">Upload a CSV in <strong>Data Upload</strong> to activate dashboard + chatbot analysis.</div>
</div>
""",
                    unsafe_allow_html=True,
                )

            st.info("Need deeper analysis? Use Filters, Visualizations, KPIs, or Demand Forecast from the sidebar.")

        with chatbot_tab:
            render_chat_ui()

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
        render_inventory_view()

elif section == "Demand Forecast":
    with st.spinner("Loading Demand Forecast..."):
        render_forecast_view()

elif section == "Supplier Insights":
    with st.spinner("Loading Supplier Insights..."):
        render_supplier_view()

elif section == "Settings":
    with st.spinner("Loading Settings..."):
        st.markdown(
            '<div class="section-header"><span class="section-header-accent"></span>Settings</div>',
            unsafe_allow_html=True,
        )

        # ── Default session-state values ─────────────────────────────────────
        _settings_defaults = {
            "settings_theme": "Light",
            "settings_date_format": "YYYY-MM-DD",
            "settings_currency": "USD ($)",
            "settings_timezone": "UTC",
            "settings_default_view": "Dashboard + Chat",
            "settings_rows_per_page": 20,
            "settings_api_env": "Mock (offline demo)",
            "settings_api_base_url": "http://localhost:8000",
            "settings_api_key": "",
            "settings_mock_mode": True,
            "settings_request_timeout": 30,
            "settings_cache_enabled": True,
            "settings_cache_ttl": 300,
            "settings_batch_size": 100,
            "settings_verbose_logging": False,
            "settings_simulate_delay": True,
            "settings_notifications": True,
            "settings_auto_refresh": False,
            "settings_refresh_interval": 60,
        }
        for _k, _v in _settings_defaults.items():
            if _k not in st.session_state:
                st.session_state[_k] = _v

        # ── Section tabs ──────────────────────────────────────────────────────
        tab_user, tab_datasource, tab_controls = st.tabs(
            ["👤 User Preferences", "🔌 Data Source", "⚙️ App Controls"]
        )

        # ─────────────────────────────────────────────────────────────────────
        # TAB 1 – User Preferences
        # ─────────────────────────────────────────────────────────────────────
        with tab_user:
            st.subheader("Profile")
            col_a, col_b = st.columns(2)
            with col_a:
                display_name = st.text_input("Display name", value=USER_NAME)
            with col_b:
                display_email = st.text_input("Email", value=USER_EMAIL, disabled=True)

            st.divider()
            st.subheader("Display Preferences")
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.settings_theme = st.selectbox(
                    "Theme",
                    ["Light", "Dark", "Auto"],
                    index=["Light", "Dark", "Auto"].index(st.session_state.settings_theme),
                )
                st.session_state.settings_date_format = st.selectbox(
                    "Date format",
                    ["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "DD MMM YYYY"],
                    index=["YYYY-MM-DD", "DD/MM/YYYY", "MM/DD/YYYY", "DD MMM YYYY"].index(
                        st.session_state.settings_date_format
                    ),
                )
                st.session_state.settings_currency = st.selectbox(
                    "Currency",
                    ["USD ($)", "EUR (€)", "GBP (£)", "INR (₹)", "JPY (¥)"],
                    index=["USD ($)", "EUR (€)", "GBP (£)", "INR (₹)", "JPY (¥)"].index(
                        st.session_state.settings_currency
                    ),
                )
            with col2:
                st.session_state.settings_timezone = st.selectbox(
                    "Timezone",
                    ["UTC", "US/Eastern", "US/Pacific", "Europe/London", "Asia/Kolkata", "Asia/Tokyo"],
                    index=["UTC", "US/Eastern", "US/Pacific", "Europe/London", "Asia/Kolkata", "Asia/Tokyo"].index(
                        st.session_state.settings_timezone
                    ),
                )
                st.session_state.settings_default_view = st.selectbox(
                    "Default landing view",
                    [
                        "Dashboard + Chat",
                        "Data Upload",
                        "Filters & Search",
                        "Data Visualization",
                        "KPIs",
                        "Inventory",
                        "Demand Forecast",
                        "Supplier Insights",
                    ],
                    index=[
                        "Dashboard + Chat",
                        "Data Upload",
                        "Filters & Search",
                        "Data Visualization",
                        "KPIs",
                        "Inventory",
                        "Demand Forecast",
                        "Supplier Insights",
                    ].index(st.session_state.settings_default_view),
                )
                st.session_state.settings_rows_per_page = st.number_input(
                    "Rows per page (tables)",
                    min_value=5,
                    max_value=500,
                    step=5,
                    value=st.session_state.settings_rows_per_page,
                )

            st.divider()
            if st.button("💾 Save User Preferences", use_container_width=True):
                st.success(f"User preferences saved — welcome back, {display_name}!")

        # ─────────────────────────────────────────────────────────────────────
        # TAB 2 – Data Source Configuration
        # ─────────────────────────────────────────────────────────────────────
        with tab_datasource:
            st.subheader("API Environment")
            env_options = [
                "Mock (offline demo)",
                "Local (localhost:8000)",
                "Development",
                "Staging",
                "Production",
            ]
            st.session_state.settings_api_env = st.selectbox(
                "Environment",
                env_options,
                index=env_options.index(st.session_state.settings_api_env),
            )

            col_ds1, col_ds2 = st.columns(2)
            with col_ds1:
                st.session_state.settings_api_base_url = st.text_input(
                    "API base URL",
                    value=st.session_state.settings_api_base_url,
                    placeholder="http://localhost:8000",
                )
                st.session_state.settings_request_timeout = st.slider(
                    "Request timeout (seconds)",
                    min_value=5,
                    max_value=120,
                    value=st.session_state.settings_request_timeout,
                    step=5,
                )
                st.session_state.settings_batch_size = st.number_input(
                    "Batch size",
                    min_value=10,
                    max_value=1000,
                    step=10,
                    value=st.session_state.settings_batch_size,
                )
            with col_ds2:
                st.session_state.settings_api_key = st.text_input(
                    "API key",
                    value=st.session_state.settings_api_key,
                    type="password",
                    placeholder="Leave blank for mock/local",
                )
                st.session_state.settings_cache_ttl = st.slider(
                    "Cache TTL (seconds)",
                    min_value=30,
                    max_value=3600,
                    value=st.session_state.settings_cache_ttl,
                    step=30,
                )
                st.session_state.settings_mock_mode = st.toggle(
                    "Mock mode (use generated sample data)",
                    value=st.session_state.settings_mock_mode,
                )

            st.divider()
            st.caption("Current effective endpoint")
            effective_url = (
                "mock://internal"
                if st.session_state.settings_mock_mode
                else f"{st.session_state.settings_api_base_url}/api/v1"
            )
            st.code(effective_url, language=None)

            col_test, col_save = st.columns(2)
            with col_test:
                if st.button("🔍 Test Connection", use_container_width=True):
                    if st.session_state.settings_mock_mode:
                        st.success("Mock mode — connection always available.")
                    else:
                        st.warning("Live connection test not implemented in this build.")
            with col_save:
                if st.button("💾 Save Data Source Settings", use_container_width=True):
                    st.success("Data source configuration saved.")

        # ─────────────────────────────────────────────────────────────────────
        # TAB 3 – App Controls
        # ─────────────────────────────────────────────────────────────────────
        with tab_controls:
            st.subheader("Runtime Controls")
            ctrl_col1, ctrl_col2 = st.columns(2)
            with ctrl_col1:
                st.session_state.settings_verbose_logging = st.toggle(
                    "Verbose logging",
                    value=st.session_state.settings_verbose_logging,
                )
                st.session_state.settings_simulate_delay = st.toggle(
                    "Simulate API latency",
                    value=st.session_state.settings_simulate_delay,
                )
                st.session_state.settings_notifications = st.toggle(
                    "In-app notifications",
                    value=st.session_state.settings_notifications,
                )
            with ctrl_col2:
                st.session_state.settings_cache_enabled = st.toggle(
                    "Enable response caching",
                    value=st.session_state.settings_cache_enabled,
                )
                st.session_state.settings_auto_refresh = st.toggle(
                    "Auto-refresh dashboard",
                    value=st.session_state.settings_auto_refresh,
                )
                if st.session_state.settings_auto_refresh:
                    st.session_state.settings_refresh_interval = st.number_input(
                        "Refresh interval (seconds)",
                        min_value=10,
                        max_value=600,
                        step=10,
                        value=st.session_state.settings_refresh_interval,
                    )

            st.divider()
            st.subheader("Cache & Session Management")
            cache_col1, cache_col2, cache_col3 = st.columns(3)
            with cache_col1:
                if st.button("🗑️ Clear Data Cache", use_container_width=True):
                    keys_to_clear = [k for k in st.session_state if k.startswith("cache_")]
                    for k in keys_to_clear:
                        del st.session_state[k]
                    st.success(f"Cleared {len(keys_to_clear)} cached item(s).")
            with cache_col2:
                if st.button("📂 Clear Uploaded Data", use_container_width=True):
                    st.session_state.uploaded_df = None
                    st.success("Uploaded dataset removed from session.")
            with cache_col3:
                if st.button("♻️ Reset All Settings", use_container_width=True):
                    for _k, _v in _settings_defaults.items():
                        st.session_state[_k] = _v
                    st.success("All settings reset to defaults.")
                    st.rerun()

            st.divider()
            st.subheader("App Info")
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.markdown("**Release:** UI Polish Final")
                st.markdown("**Framework:** Streamlit")
                st.markdown(f"**User:** {USER_NAME}")
            with info_col2:
                st.markdown(f"**Email:** {USER_EMAIL}")
                st.markdown("**API Version:** v1")
                st.markdown(
                    f"**Mock mode:** {'✅ On' if st.session_state.settings_mock_mode else '❌ Off'}"
                )
