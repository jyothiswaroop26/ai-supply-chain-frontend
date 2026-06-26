import os
import sys

import pandas as pd
import plotly.express as px
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


def _detect_column(df: pd.DataFrame, keywords: list[str]) -> str | None:
    """Return first column whose name matches any keyword."""
    for col in df.columns:
        lower_name = col.lower()
        if any(keyword in lower_name for keyword in keywords):
            return col
    return None


def _render_dashboard_tab(df: pd.DataFrame) -> None:
    """Render the dashboard workspace with interactive insights."""
    rows, cols = df.shape
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = [
        col
        for col in df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
        if df[col].nunique(dropna=True) <= 40
    ]
    missing_pct = round(df.isnull().sum().sum() / max(df.size, 1) * 100, 1)
    duplicate_pct = round(df.duplicated().mean() * 100, 1)

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
    <div class="overview-stat-value">{len(numeric_cols)}</div>
    <div class="overview-stat-label">Numeric Columns</div>
  </div>
  <div class="overview-stat">
    <div class="overview-stat-value">{missing_pct}%</div>
    <div class="overview-stat-label">Missing Values</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
<div class="dashboard-grid">
  <div class="dashboard-card">
    <div class="dashboard-card-title">Data Health</div>
    <div class="dashboard-card-value">{100 - missing_pct:.1f}% complete</div>
    <div class="dashboard-card-note">Based on non-null values across all cells</div>
  </div>
  <div class="dashboard-card">
    <div class="dashboard-card-title">Duplicate Rows</div>
    <div class="dashboard-card-value">{duplicate_pct}%</div>
    <div class="dashboard-card-note">Potentially repeated records in the dataset</div>
  </div>
  <div class="dashboard-card">
    <div class="dashboard-card-title">Analysis Readiness</div>
    <div class="dashboard-card-value">{len(categorical_cols)} segments</div>
    <div class="dashboard-card-note">Categorical columns suitable for grouped insights</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    health_tags = []
    health_tags.append(("GOOD", "Missing <= 5%") if missing_pct <= 5 else ("CHECK", "Missing > 5%"))
    health_tags.append(("GOOD", "Duplicates <= 2%") if duplicate_pct <= 2 else ("CHECK", "Duplicates > 2%"))
    health_tags.append(("GOOD", "Numeric columns found") if numeric_cols else ("WARN", "No numeric columns"))
    health_tags.append(("GOOD", "Segments available") if categorical_cols else ("CHECK", "Limited segmentation"))

    badges_html = "".join(
        f'<span class="health-badge health-{level.lower()}">{level}: {label}</span>' for level, label in health_tags
    )
    st.markdown(f'<div class="health-badges">{badges_html}</div>', unsafe_allow_html=True)

    if not numeric_cols:
        st.warning("No numeric columns found. Upload a dataset with at least one numeric field for charting.")
        st.dataframe(df.head(20), use_container_width=True)
        return

    default_metric = _detect_column(df, ["value", "cost", "price", "quantity", "demand", "inventory"]) or numeric_cols[0]
    default_category = _detect_column(df, ["supplier", "product", "category", "region", "warehouse"])
    default_date = _detect_column(df, ["date", "week", "month", "period", "time"])

    control_col1, control_col2, control_col3 = st.columns(3)
    with control_col1:
        metric_col = st.selectbox(
            "Primary metric",
            options=numeric_cols,
            index=numeric_cols.index(default_metric) if default_metric in numeric_cols else 0,
            help="Used by distribution and trend charts.",
        )
    with control_col2:
        category_options = [None] + categorical_cols
        category_col = st.selectbox(
            "Category segment",
            options=category_options,
            index=category_options.index(default_category) if default_category in category_options else 0,
            format_func=lambda x: "None" if x is None else x,
            help="Optional grouped analysis by categorical field.",
        )
    with control_col3:
        top_n = st.slider("Top categories", min_value=5, max_value=25, value=10, step=1)

    left_chart, right_chart = st.columns(2)

    with left_chart:
        st.subheader("Metric Trend or Distribution")
        date_col = default_date if default_date in df.columns else None
        if date_col:
            ts_df = df[[date_col, metric_col]].copy()
            ts_df[date_col] = pd.to_datetime(ts_df[date_col], errors="coerce")
            ts_df = ts_df.dropna(subset=[date_col, metric_col]).sort_values(date_col)
            if not ts_df.empty:
                ts_agg = ts_df.groupby(date_col, as_index=False)[metric_col].mean()
                trend_fig = px.line(
                    ts_agg,
                    x=date_col,
                    y=metric_col,
                    template="plotly_white",
                    title=f"Average {metric_col} over time",
                    markers=True,
                )
                trend_fig.update_layout(margin=dict(l=8, r=8, t=46, b=8))
                st.plotly_chart(trend_fig, use_container_width=True)
            else:
                st.info("Date parsing failed for trend view. Displaying metric distribution instead.")
                hist_fig = px.histogram(df, x=metric_col, nbins=30, template="plotly_white")
                hist_fig.update_layout(margin=dict(l=8, r=8, t=24, b=8))
                st.plotly_chart(hist_fig, use_container_width=True)
        else:
            hist_fig = px.histogram(df, x=metric_col, nbins=30, template="plotly_white")
            hist_fig.update_layout(margin=dict(l=8, r=8, t=24, b=8))
            st.plotly_chart(hist_fig, use_container_width=True)

    with right_chart:
        st.subheader("Segment Comparison")
        if category_col:
            grouped = (
                df[[category_col, metric_col]]
                .dropna()
                .groupby(category_col, as_index=False)[metric_col]
                .mean()
                .sort_values(metric_col, ascending=False)
                .head(top_n)
            )
            bar_fig = px.bar(
                grouped,
                x=category_col,
                y=metric_col,
                template="plotly_white",
                title=f"Top {top_n} by average {metric_col}",
                color=metric_col,
                color_continuous_scale="Blues",
            )
            bar_fig.update_layout(xaxis_tickangle=-30, margin=dict(l=8, r=8, t=46, b=8), coloraxis_showscale=False)
            st.plotly_chart(bar_fig, use_container_width=True)
        else:
            box_fig = px.box(df, y=metric_col, template="plotly_white", title=f"Distribution of {metric_col}")
            box_fig.update_layout(margin=dict(l=8, r=8, t=46, b=8))
            st.plotly_chart(box_fig, use_container_width=True)

    st.subheader("Data Preview")
    st.dataframe(df.head(20), use_container_width=True)
    st.caption("Tip: Move to Filters, KPIs, Inventory, and Supplier Insights for deeper diagnostics.")

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
                                _render_dashboard_tab(df)
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
