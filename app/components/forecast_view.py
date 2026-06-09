import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta


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

    # Generate forecast
    historical_data = df[forecast_column].dropna()
    
    if len(historical_data) < 2:
        st.error("Not enough data points to generate forecast.")
        return

    forecast_values = _generate_forecast(
        historical_data.values, 
        forecast_periods, 
        forecast_method
    )

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

    # Add confidence interval (simple visualization)
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

    # Display forecast statistics
    st.subheader("Forecast Statistics")
    
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Last Historical Value",
            f"{historical_data.iloc[-1]:.2f}",
            delta=f"{forecast_values[0] - historical_data.iloc[-1]:.2f}",
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
        "Upper Bound (±10%)": forecast_values * 1.1,
        "Lower Bound (±10%)": forecast_values * 0.9,
        "Change %": [(forecast_values[i] - historical_data.iloc[-1]) / historical_data.iloc[-1] * 100 
                     for i in range(len(forecast_values))]
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
        growth_rate = ((forecast_values[-1] - historical_data.iloc[-1]) / historical_data.iloc[-1]) * 100
        
        if growth_rate > 0:
            st.success(f"📊 Predicted Growth: +{growth_rate:.2f}%", icon="✅")
        elif growth_rate < 0:
            st.warning(f"📊 Predicted Decline: {growth_rate:.2f}%", icon="⚠️")
        else:
            st.info(f"📊 Predicted Stability: {growth_rate:.2f}%", icon="ℹ️")


def _generate_forecast(data, periods, method):
    """Generate forecast using specified method."""
    
    if method == "Linear Trend":
        # Linear regression trend
        x = np.arange(len(data))
        coeffs = np.polyfit(x, data, 1)
        poly = np.poly1d(coeffs)
        future_x = np.arange(len(data), len(data) + periods)
        forecast = poly(future_x)
        
    elif method == "Moving Average":
        # Exponential weighted moving average projection
        if len(data) >= 3:
            ma_window = min(3, len(data))
            ma = np.convolve(data, np.ones(ma_window)/ma_window, mode='valid')
            last_value = data[-1]
            trend = (ma[-1] - ma[0]) / (len(ma) - 1) if len(ma) > 1 else 0
            forecast = np.array([last_value + trend * (i + 1) for i in range(periods)])
        else:
            forecast = np.full(periods, data.mean())
            
    elif method == "Exponential Smoothing":
        # Simple exponential smoothing
        alpha = 0.3
        level = data[0]
        forecast = []
        
        # Fit on historical data
        for value in data[1:]:
            level = alpha * value + (1 - alpha) * level
        
        # Generate forecast
        for _ in range(periods):
            forecast.append(level)
            level = alpha * level + (1 - alpha) * level
            
        forecast = np.array(forecast)
    else:
        # Default: simple average
        forecast = np.full(periods, data.mean())
    
    return forecast
