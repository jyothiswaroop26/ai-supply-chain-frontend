import streamlit as st
import pandas as pd
import plotly.express as px


def render_data_view():
    """Render data visualization component with line and bar charts."""
    st.markdown('<div class="section-header"><span class="section-header-accent"></span>Data Visualization</div>', unsafe_allow_html=True)
    st.write("Create interactive charts from your supply chain data.")

    # Check if data is available in session state
    if "uploaded_df" not in st.session_state or st.session_state.uploaded_df is None:
        st.info("📊 No data available. Please upload a CSV file in the **Data Upload** section first.")
        return

    df = st.session_state.uploaded_df

    # Chart type selection
    chart_type = st.selectbox(
        "Select chart type",
        ["Line Chart", "Bar Chart", "Scatter Plot", "Box Plot"]
    )

    # Get numeric and non-numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(include=["object"]).columns.tolist()
    all_cols = df.columns.tolist()

    if not numeric_cols:
        st.warning("No numeric columns found in the data. Charts require numeric data.")
        return

    # Chart configuration
    st.subheader("Chart Configuration")
    col1, col2, col3 = st.columns(3)

    with col1:
        if chart_type in ["Line Chart", "Scatter Plot"]:
            x_column = st.selectbox("X-axis (typically time)", options=all_cols, key="x_axis")
        else:
            x_column = st.selectbox("X-axis", options=all_cols, key="x_axis")

    with col2:
        y_column = st.selectbox("Y-axis", options=numeric_cols, key="y_axis")

    with col3:
        color_column = st.selectbox(
            "Color by (optional)",
            options=[None] + categorical_cols,
            key="color_by"
        )

    # Additional options
    col1, col2 = st.columns(2)
    with col1:
        show_markers = st.checkbox("Show markers", value=True) if chart_type == "Line Chart" else False
    with col2:
        show_grid = st.checkbox("Show grid", value=True)

    # Render selected chart
    try:
        chart_kwargs = {
            "x": x_column,
            "y": y_column,
            "template": "plotly_white"
        }
        
        if color_column:
            chart_kwargs["color"] = color_column
        
        if chart_type == "Line Chart":
            chart_kwargs["title"] = f"{y_column} over {x_column}"
            chart_kwargs["markers"] = show_markers
            fig = px.line(df, **chart_kwargs)
        elif chart_type == "Bar Chart":
            chart_kwargs["title"] = f"{y_column} by {x_column}"
            fig = px.bar(df, **chart_kwargs)
        elif chart_type == "Scatter Plot":
            chart_kwargs["title"] = f"{y_column} vs {x_column}"
            fig = px.scatter(df, **chart_kwargs)
        elif chart_type == "Box Plot":
            chart_kwargs["title"] = f"Distribution of {y_column} by {x_column}"
            fig = px.box(df, **chart_kwargs)

        # Apply grid setting
        fig.update_xaxes(showgrid=show_grid)
        fig.update_yaxes(showgrid=show_grid)

        # Display chart
        st.plotly_chart(fig, use_container_width=True)

        # Chart statistics
        with st.expander("📈 Chart Statistics"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Mean", f"{df[y_column].mean():.2f}")
            with col2:
                st.metric("Median", f"{df[y_column].median():.2f}")
            with col3:
                st.metric("Std Dev", f"{df[y_column].std():.2f}")

    except Exception as e:
        st.error(f"Error generating chart: {e}")
        st.info("Make sure the selected columns contain compatible data types.")


def render_summary_charts(df):
    """Render summary overview charts."""
    st.subheader("Summary Overview")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        st.info("No numeric data available for summary charts.")
        return

    # Create columns for multiple charts
    cols = st.columns(2)

    # Distribution chart
    with cols[0]:
        selected_col = st.selectbox("Select column for distribution", numeric_cols, key="dist_col")
        fig_hist = px.histogram(
            df,
            x=selected_col,
            nbins=30,
            title=f"Distribution of {selected_col}",
            template="plotly_white"
        )
        st.plotly_chart(fig_hist, use_container_width=True)

    # Correlation chart
    with cols[1]:
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            fig_corr = px.imshow(
                corr_matrix,
                title="Correlation Matrix",
                template="plotly_white",
                color_continuous_scale="RdBu_r"
            )
            st.plotly_chart(fig_corr, use_container_width=True)
        else:
            st.info("Need at least 2 numeric columns for correlation matrix.")
