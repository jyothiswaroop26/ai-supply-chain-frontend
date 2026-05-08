import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def render_kpi():
    """Render Key Performance Indicators (KPI) cards for supply chain metrics."""
    st.header("Key Performance Indicators (KPIs)")
    st.write("Monitor critical supply chain metrics and performance indicators.")

    # Check if data is available in session state
    if "uploaded_df" not in st.session_state or st.session_state.uploaded_df is None:
        st.info("📊 No data available. Please upload a CSV file in the **Data Upload** section first.")
        return

    df = st.session_state.uploaded_df

    # Get numeric columns for metrics calculation
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        st.warning("No numeric columns found in the data. KPIs require numeric data.")
        return

    # Create KPI section with tabs
    kpi_tab1, kpi_tab2 = st.tabs(["Summary Metrics", "Detailed Analysis"])

    with kpi_tab1:
        st.subheader("Summary KPI Cards")
        
        # Calculate metrics
        metrics = _calculate_kpis(df, numeric_cols)
        
        # Display main KPIs in columns
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="📦 Total Records",
                value=f"{metrics['total_records']:,}",
                delta="Data points in dataset"
            )

        with col2:
            st.metric(
                label="💰 Average Value",
                value=f"${metrics['avg_value']:.2f}",
                delta=f"Max: ${metrics['max_value']:.2f}"
            )

        with col3:
            st.metric(
                label="📈 Total Sum",
                value=f"${metrics['total_sum']:.2f}",
                delta_color="normal"
            )

        with col4:
            st.metric(
                label="📊 Data Quality",
                value=f"{metrics['data_quality_score']:.1f}%",
                delta="Complete records"
            )

        # Secondary KPIs
        st.subheader("Additional Metrics")
        
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="🎯 Mean Value",
                value=f"{metrics['mean_value']:.2f}",
            )

        with col2:
            st.metric(
                label="📉 Minimum Value",
                value=f"${metrics['min_value']:.2f}",
            )

        with col3:
            st.metric(
                label="📊 Standard Deviation",
                value=f"{metrics['std_dev']:.2f}",
            )

        with col4:
            st.metric(
                label="🔄 Coefficient of Variation",
                value=f"{metrics['cv_percentage']:.2f}%",
            )

    with kpi_tab2:
        st.subheader("Detailed Performance Analysis")
        
        # Column selection for detailed analysis
        col1, col2 = st.columns(2)
        
        with col1:
            selected_metric = st.selectbox(
                "Select metric for detailed analysis",
                options=numeric_cols,
                help="Choose a numeric column to analyze"
            )
        
        with col2:
            analysis_type = st.selectbox(
                "Analysis type",
                ["Distribution", "Trend", "Comparison"],
                help="Choose the type of analysis"
            )

        # Get detailed metrics for selected column
        detailed_metrics = _calculate_detailed_metrics(df[selected_metric].dropna())

        if analysis_type == "Distribution":
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Count", f"{detailed_metrics['count']:,}")
            with col2:
                st.metric("Median", f"{detailed_metrics['median']:.2f}")
            with col3:
                st.metric("Q1 (25%)", f"{detailed_metrics['q1']:.2f}")
            with col4:
                st.metric("Q3 (75%)", f"{detailed_metrics['q3']:.2f}")

        elif analysis_type == "Trend":
            col1, col2, col3, col4 = st.columns(4)
            
            trend_direction = "📈 Increasing" if detailed_metrics['trend_direction'] > 0 else "📉 Decreasing"
            trend_strength = abs(detailed_metrics['trend_direction'])
            
            with col1:
                st.metric("Trend", trend_direction)
            with col2:
                st.metric("Rate of Change", f"{detailed_metrics['trend_direction']:.4f}")
            with col3:
                st.metric("Range", f"{detailed_metrics['range']:.2f}")
            with col4:
                st.metric("IQR", f"{detailed_metrics['iqr']:.2f}")

        elif analysis_type == "Comparison":
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Skewness", f"{detailed_metrics['skewness']:.3f}")
            with col2:
                st.metric("Kurtosis", f"{detailed_metrics['kurtosis']:.3f}")
            with col3:
                st.metric("Variance", f"{detailed_metrics['variance']:.2f}")
            with col4:
                st.metric("Mean Absolute Dev.", f"{detailed_metrics['mad']:.2f}")

    # Summary statistics table
    st.subheader("Summary Statistics by Column")
    
    summary_stats = df[numeric_cols].describe().round(2)
    st.dataframe(summary_stats, use_container_width=True)

    # Performance indicators
    st.subheader("Performance Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        high_variance_cols = []
        for col in numeric_cols:
            cv = (df[col].std() / df[col].mean()) * 100 if df[col].mean() != 0 else 0
            if cv > 50:
                high_variance_cols.append(f"{col} (CV: {cv:.1f}%)")
        
        if high_variance_cols:
            st.warning(
                f"⚠️ **High Variance Detected:**\n" +
                "\n".join([f"• {col}" for col in high_variance_cols])
            )
        else:
            st.success("✅ All metrics show stable variance")

    with col2:
        missing_data_pct = (df[numeric_cols].isnull().sum() / len(df) * 100).max()
        
        if missing_data_pct > 10:
            st.warning(f"⚠️ **Missing Data:** Up to {missing_data_pct:.1f}% missing values detected")
        elif missing_data_pct > 0:
            st.info(f"ℹ️ **Data Quality:** {missing_data_pct:.1f}% missing values")
        else:
            st.success("✅ Complete dataset with no missing values")


def _calculate_kpis(df, numeric_cols):
    """Calculate key performance indicators from the data."""
    
    # Combine all numeric data
    all_numeric_data = df[numeric_cols].values.flatten()
    all_numeric_data = all_numeric_data[~np.isnan(all_numeric_data)]
    
    # Calculate metrics
    total_records = len(df)
    total_sum = all_numeric_data.sum()
    avg_value = all_numeric_data.mean()
    max_value = all_numeric_data.max()
    min_value = all_numeric_data.min()
    std_dev = all_numeric_data.std()
    
    # Data quality score (percentage of non-null values)
    total_cells = df[numeric_cols].shape[0] * df[numeric_cols].shape[1]
    non_null_cells = df[numeric_cols].count().sum()
    data_quality_score = (non_null_cells / total_cells) * 100 if total_cells > 0 else 0
    
    # Coefficient of variation (relative variability)
    cv_percentage = (std_dev / avg_value * 100) if avg_value != 0 else 0
    
    mean_value = all_numeric_data.mean()
    
    return {
        "total_records": total_records,
        "avg_value": avg_value,
        "total_sum": total_sum,
        "max_value": max_value,
        "min_value": min_value,
        "std_dev": std_dev,
        "data_quality_score": data_quality_score,
        "cv_percentage": cv_percentage,
        "mean_value": mean_value
    }


def _calculate_detailed_metrics(series):
    """Calculate detailed statistical metrics for a series."""
    
    series_clean = series.dropna()
    
    if len(series_clean) == 0:
        return {}
    
    # Calculate statistics
    count = len(series_clean)
    median = series_clean.median()
    q1 = series_clean.quantile(0.25)
    q3 = series_clean.quantile(0.75)
    iqr = q3 - q1
    range_val = series_clean.max() - series_clean.min()
    variance = series_clean.var()
    
    # Trend direction (simple linear trend)
    x = np.arange(len(series_clean))
    if len(series_clean) > 1:
        coeffs = np.polyfit(x, series_clean.values, 1)
        trend_direction = coeffs[0]
    else:
        trend_direction = 0
    
    # Skewness and Kurtosis
    skewness = series_clean.skew()
    kurtosis = series_clean.kurtosis()
    
    # Mean Absolute Deviation
    mad = (series_clean - series_clean.mean()).abs().mean()
    
    return {
        "count": count,
        "median": median,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "range": range_val,
        "variance": variance,
        "trend_direction": trend_direction,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "mad": mad
    }
