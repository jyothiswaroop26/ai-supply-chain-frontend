import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from services.api_client import get_forecast


def render_forecast_view():
    """Render demand forecast predictions component."""
    st.markdown('<div class="section-header"><span class="section-header-accent"></span>Demand Forecast</div>', unsafe_allow_html=True)
    st.write("View AI-powered demand forecasts and trend predictions for your supply chain data.")

    # Check if data is available in session state
    if "uploaded_df" not in st.session_state or st.session_state.uploaded_df is None:
        st.info("📊 No data available. Please upload a CSV file in the **Data Upload** section first.")
        return

    df = st.session_state.uploaded_df

    # Get numeric columns for forecasting
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    if not numeric_cols:
        st.warning("No numeric columns found in the data. Forecasting requires numeric data.")
        return

    st.subheader("Forecast Configuration")
    col1, col2, col3 = st.columns(3)

    with col1:
        forecast_column = st.selectbox(
            "Select metric to forecast",
            options=numeric_cols,
            help="Choose which metric you want to forecast"
        )

    with col2:
        forecast_periods = st.slider(
            "Forecast periods ahead",
            min_value=1,
            max_value=30,
            value=7,
            help="How many periods to forecast into the future"
        )

    with col3:
        forecast_method = st.selectbox(
            "Forecast method",
            ["Linear Trend", "Moving Average", "Exponential Smoothing"],
            help="Select the forecasting algorithm"
        )

    run_forecast = st.button("Generate Forecast", type="primary")
    if not run_forecast:
        st.info("Select forecast settings and click Generate Forecast.")
        return

    # Generate forecast
    historical_data = df[forecast_column].dropna()
    
    if len(historical_data) < 2:
        st.error("Not enough data points to generate forecast.")
        return

    method_map = {
        "Linear Trend": "linear",
        "Moving Average": "moving_average",
        "Exponential Smoothing": "exponential",
    }

    try:
        with st.spinner("Generating forecast from API..."):
            response = get_forecast(
                data_points=historical_data.values.tolist(),
                periods=forecast_periods,
                metric=forecast_column,
                method=method_map.get(forecast_method, "linear"),
            )
    except Exception as exc:
        st.error(f"Forecast API request failed: {exc}")
        return

    if not response.get("success"):
        st.error(response.get("error") or "Failed to generate forecast from API.")
        return

    forecast_values = np.array(response.get("forecast_values", []), dtype=float)
    if forecast_values.size == 0:
        st.warning("API returned an empty forecast. Try a different metric or method.")
        return

    if forecast_values.size != forecast_periods:
        st.warning(
            f"Expected {forecast_periods} forecast points, but got {forecast_values.size}. Showing available data."
        )
        forecast_periods = int(forecast_values.size)

    confidence = response.get("confidence_interval") or {}
    upper_from_api = confidence.get("upper_bound")
    lower_from_api = confidence.get("lower_bound")

    # Create visualization
    st.subheader("Forecast Visualization")
    
    # Prepare data for plotting
    historical_index = np.arange(len(historical_data))
    forecast_index = np.arange(len(historical_data), len(historical_data) + forecast_periods)

    fig = go.Figure()

    # Add historical data
    fig.add_trace(go.Scatter(
        x=historical_index,
        y=historical_data.values,
        mode='lines+markers',
        name='Historical Data',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=6)
    ))

    # Add forecast
    fig.add_trace(go.Scatter(
        x=forecast_index,
        y=forecast_values,
        mode='lines+markers',
        name='Forecast',
        line=dict(color='#ff7f0e', width=2, dash='dash'),
        marker=dict(size=6)
    ))

    # Add confidence interval from API when available.
    if upper_from_api and lower_from_api and len(upper_from_api) == forecast_periods and len(lower_from_api) == forecast_periods:
        upper_bound = np.array(upper_from_api, dtype=float)
        lower_bound = np.array(lower_from_api, dtype=float)
    else:
        upper_bound = forecast_values * 1.1
        lower_bound = forecast_values * 0.9

    fig.add_trace(go.Scatter(
        x=forecast_index.tolist() + forecast_index.tolist()[::-1],
        y=upper_bound.tolist() + lower_bound.tolist()[::-1],
        fill='toself',
        fillcolor='rgba(255, 127, 14, 0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        showlegend=True,
        name='Confidence Band (±10%)'
    ))

    fig.update_layout(
        title=f"Demand Forecast for {forecast_column} ({forecast_method})",
        xaxis_title="Time Period",
        yaxis_title=forecast_column,
        height=500,
        hovermode='x unified',
        template='plotly_white'
    )

    st.plotly_chart(fig, use_container_width=True)

    raw = response.get("raw") or {}
    mape = raw.get("mape")
    rmse = raw.get("rmse")
    model_used = response.get("method", "-")
    st.caption(
        f"API model: {model_used}"
        + (f" | MAPE: {mape}" if mape is not None else "")
        + (f" | RMSE: {rmse}" if rmse is not None else "")
    )

    # Display forecast statistics
    st.subheader("Forecast Statistics")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        baseline_value = historical_data.iloc[-1]
        if baseline_value == 0:
            delta_value = "N/A"
        else:
            delta_value = f"{forecast_values[0] - baseline_value:.2f}"

        st.metric(
            "Last Historical Value",
            f"{baseline_value:.2f}",
            delta=delta_value,
            delta_color="inverse"
        )

    with col2:
        st.metric(
            "Average Forecast",
            f"{forecast_values.mean():.2f}"
        )

    with col3:
        st.metric(
            "Max Forecast",
            f"{forecast_values.max():.2f}"
        )

    with col4:
        st.metric(
            "Min Forecast",
            f"{forecast_values.min():.2f}"
        )

    # Display forecast table
    st.subheader("Forecast Data")
    
    forecast_df = pd.DataFrame({
        "Period": range(1, forecast_periods + 1),
        "Forecast Value": forecast_values,
        "Upper Bound": upper_bound,
        "Lower Bound": lower_bound,
        "Change %": [
            0.0 if historical_data.iloc[-1] == 0 else (forecast_values[i] - historical_data.iloc[-1]) / historical_data.iloc[-1] * 100
            for i in range(len(forecast_values))
        ]
    })

    st.dataframe(forecast_df.round(2), use_container_width=True)

    # Advanced analysis
    st.subheader("Trend Analysis")
    
    col1, col2 = st.columns(2)

    with col1:
        # Calculate trend
        trend_direction = "📈 Uptrend" if forecast_values[-1] > historical_data.iloc[-1] else "📉 Downtrend"
        volatility = np.std(forecast_values)
        
        st.write(f"**Trend Direction:** {trend_direction}")
        st.write(f"**Forecast Volatility:** {volatility:.2f}")
        st.write(f"**Historical Mean:** {historical_data.mean():.2f}")
        st.write(f"**Historical Std Dev:** {historical_data.std():.2f}")

    with col2:
        # Growth rate
        if historical_data.iloc[-1] == 0:
            st.info("📊 Growth rate unavailable because the latest historical value is 0.", icon="ℹ️")
            return

        growth_rate = ((forecast_values[-1] - historical_data.iloc[-1]) / historical_data.iloc[-1]) * 100
        
        if growth_rate > 0:
            st.success(f"📊 Predicted Growth: +{growth_rate:.2f}%", icon="✅")
        elif growth_rate < 0:
            st.warning(f"📊 Predicted Decline: {growth_rate:.2f}%", icon="⚠️")
        else:
            st.info(f"📊 Predicted Stability: {growth_rate:.2f}%", icon="ℹ️")


