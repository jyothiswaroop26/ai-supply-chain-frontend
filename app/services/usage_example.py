"""
Complete Usage Examples for AI Supply Chain Frontend API Integration
Demonstrates all API features and integration patterns.
"""

import streamlit as st
import pandas as pd
from typing import Optional

# ============================================================================
# Example 1: Basic Streamlit Integration (Recommended)
# ============================================================================

def example_streamlit_service():
    """
    The easiest and recommended way to use the API in Streamlit components.
    Handles caching, error handling, and session state automatically.
    """
    from app.services import get_streamlit_api_service
    
    service = get_streamlit_api_service()
    
    # Fetch data with automatic error handling and caching
    suppliers = service.fetch_suppliers(page=1, limit=10)
    
    if suppliers:
        st.write(f"Found {len(suppliers)} suppliers")
        st.dataframe(pd.DataFrame(suppliers))
    # If None, error was already displayed


# ============================================================================
# Example 2: Using Unified API Client Directly
# ============================================================================

def example_unified_client():
    """
    Direct use of the UnifiedAPIClient for more control.
    Supports both mock and HTTP modes automatically.
    """
    from app.services import get_unified_api_client
    
    client = get_unified_api_client()
    
    # Make an API call
    response = client.fetch_suppliers(page=1, limit=10)
    
    # Check response
    if response.success:
        st.success(f"Success: {response.message}")
        suppliers = response.data
        st.write(suppliers)
    else:
        st.error(f"Error: {response.error}")
        st.write(f"Message: {response.message}")


# ============================================================================
# Example 3: HTTP Client (Production Use)
# ============================================================================

def example_http_client():
    """
    Direct use of HTTPAPIClient for real backend servers.
    Use this when you have a real API server to connect to.
    """
    from app.services import HTTPAPIClient, APIConfig, APIEnvironment
    
    # Configure for your backend
    config = APIConfig(
        environment=APIEnvironment.PRODUCTION,
        base_url="https://api.example.com",
        api_version="v1",
        use_auth=True,
        api_key="your-api-key-here",
        request_timeout=30,
        max_retries=3
    )
    
    # Create client
    client = HTTPAPIClient(config=config)
    
    try:
        # Make requests
        response = client.fetch_suppliers(page=1, limit=10)
        
        if response.success:
            suppliers = response.data
            print(f"Fetched {len(suppliers)} suppliers")
        else:
            print(f"Error: {response.error}")
            
    finally:
        # Clean up
        client.close()


# ============================================================================
# Example 4: Mock Client (Development/Testing)
# ============================================================================

def example_mock_client():
    """
    Use MockAPIClient for development without a real backend.
    Returns realistic mock data for all endpoints.
    """
    from app.services import MockAPIClient
    
    # Create mock client
    client = MockAPIClient(simulate_delay=True)
    
    # All API calls return mock data
    response = client.fetch_suppliers()
    print(f"Mock suppliers: {response.data}")
    
    response = client.get_inventory_levels()
    print(f"Mock inventory: {response.data}")


# ============================================================================
# Example 5: Data Upload and Processing
# ============================================================================

def example_upload_and_process():
    """
    Upload data and calculate KPIs - end-to-end workflow.
    """
    from app.services import get_streamlit_api_service
    
    service = get_streamlit_api_service()
    
    # Upload file
    uploaded_file = st.file_uploader("Choose CSV", type=["csv"])
    
    if uploaded_file:
        # Read file
        df = pd.read_csv(uploaded_file)
        
        # Upload to API
        success = service.upload_data(uploaded_file.name, uploaded_file.getvalue())
        
        if success:
            st.success("File uploaded!")
            
            # Calculate KPIs
            kpis = service.calculate_kpis(df)
            
            if kpis:
                st.write("Calculated KPIs:")
                for key, value in kpis.items():
                    st.metric(key, value)


# ============================================================================
# Example 6: Forecasting Workflow
# ============================================================================

def example_forecasting():
    """
    Generate and display demand forecasts.
    """
    from app.services import get_streamlit_api_service
    import plotly.graph_objects as go
    
    service = get_streamlit_api_service()
    
    # Get data
    if "uploaded_df" in st.session_state:
        df = st.session_state.uploaded_df
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        
        if numeric_cols:
            # Select column to forecast
            col = st.selectbox("Select metric to forecast", numeric_cols)
            periods = st.slider("Forecast periods", 1, 30, 7)
            method = st.selectbox("Method", ["Linear Trend", "Moving Average", "Exponential Smoothing"])
            
            # Generate forecast
            method_map = {"Linear Trend": "linear", "Moving Average": "moving_average", "Exponential Smoothing": "exponential"}
            forecast_data = service.generate_forecast(
                data_points=df[col].dropna().values.tolist(),
                periods=periods,
                method=method_map[method]
            )
            
            if forecast_data:
                # Display
                fig = go.Figure()
                
                # Historical
                fig.add_trace(go.Scatter(
                    y=df[col].values,
                    name="Historical",
                    line=dict(color="blue")
                ))
                
                # Forecast
                fig.add_trace(go.Scatter(
                    y=forecast_data["forecast_values"],
                    name="Forecast",
                    line=dict(color="orange", dash="dash")
                ))
                
                st.plotly_chart(fig)


# ============================================================================
# Example 7: Supplier Intelligence
# ============================================================================

def example_supplier_intelligence():
    """
    Fetch and analyze supplier data.
    """
    from app.services import get_streamlit_api_service
    
    service = get_streamlit_api_service()
    
    # Get suppliers list
    suppliers_data = service.fetch_suppliers(page=1, limit=20)
    
    if suppliers_data and "suppliers" in suppliers_data:
        suppliers = suppliers_data["suppliers"]
        
        # Create comparison table
        df = pd.DataFrame(suppliers)
        st.dataframe(df, use_container_width=True)
        
        # Get details for selected supplier
        supplier_id = st.selectbox(
            "Select supplier for details",
            [s["id"] for s in suppliers],
            format_func=lambda x: next(s["name"] for s in suppliers if s["id"] == x)
        )
        
        details = service.get_supplier_details(supplier_id)
        if details:
            st.write("Supplier Details:")
            for key, value in details.items():
                st.write(f"**{key}**: {value}")


# ============================================================================
# Example 8: Chat/AI Integration
# ============================================================================

def example_chat_integration():
    """
    Use the AI chat feature for supply chain queries.
    """
    from app.services import get_streamlit_api_service
    
    service = get_streamlit_api_service()
    
    # Create session
    if "chat_session" not in st.session_state:
        session_data = service.create_chat_session()
        if session_data:
            st.session_state.chat_session = session_data.get("session_id")
    
    if st.session_state.get("chat_session"):
        # Chat input
        user_input = st.text_input("Ask about supply chain:")
        
        if user_input:
            # Send message
            response = service.send_chat_message(
                message=user_input,
                session_id=st.session_state.chat_session
            )
            
            if response:
                st.write("**Assistant:**")
                st.write(response.get("response", ""))
                
                # Show follow-up suggestions
                if "follow_up_suggestions" in response:
                    st.write("**Suggestions:**")
                    for suggestion in response["follow_up_suggestions"]:
                        st.write(f"- {suggestion}")


# ============================================================================
# Example 9: Report Generation
# ============================================================================

def example_report_generation():
    """
    Generate and download reports.
    """
    from app.services import get_streamlit_api_service
    
    service = get_streamlit_api_service()
    
    report_type = st.selectbox(
        "Report Type",
        ["summary", "detailed", "executive"]
    )
    
    if st.button("Generate Report"):
        # Generate
        report = service.generate_report(report_type=report_type)
        
        if report:
            st.write(f"**Report ID**: {report.get('report_id')}")
            st.write(f"**Title**: {report.get('title')}")
            
            # Download link
            download = service.download_report(report.get('report_id'))
            if download:
                st.download_button(
                    "Download Report",
                    data=b"Report content here",
                    file_name=download.get('filename')
                )


# ============================================================================
# Example 10: Configuration and Switching Modes
# ============================================================================

def example_configuration():
    """
    Configure API and switch between modes.
    """
    from app.services import (
        get_unified_api_client,
        APIConfig,
        APIEnvironment
    )
    
    client = get_unified_api_client()
    config = client.config
    
    # Display current config
    st.write("**Current Configuration:**")
    st.write(f"Environment: {config.environment.value}")
    st.write(f"Base URL: {config.base_url}")
    st.write(f"Mock Mode: {config.mock_mode}")
    st.write(f"Caching: {config.enable_caching}")
    
    # Switch mode
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Switch to HTTP Mode"):
            client.switch_mode(use_http=True)
            st.rerun()
    
    with col2:
        if st.button("Switch to Mock Mode"):
            client.switch_mode(use_http=False)
            st.rerun()
    
    # Cache stats
    st.write("**Cache Statistics:**")
    stats = client.get_cache_stats()
    st.json(stats)
    
    # Clear cache
    if st.button("Clear Cache"):
        client.clear_cache()
        st.success("Cache cleared!")


# ============================================================================
# Example 11: Error Handling and Retry Logic
# ============================================================================

def example_error_handling():
    """
    Robust error handling patterns.
    """
    from app.services import get_unified_api_client
    import time
    
    client = get_unified_api_client()
    
    # Pattern 1: Basic error checking
    response = client.fetch_suppliers()
    
    if response.success:
        suppliers = response.data
    else:
        st.error(f"Failed to fetch suppliers: {response.error}")
    
    # Pattern 2: Retry logic
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        response = client.fetch_suppliers()
        
        if response.success:
            st.success("Data fetched successfully!")
            break
        else:
            if attempt < max_retries - 1:
                st.warning(f"Attempt {attempt + 1} failed, retrying...")
                time.sleep(retry_delay)
            else:
                st.error(f"Failed after {max_retries} attempts")


# ============================================================================
# Example 12: Advanced - Custom Configuration from Environment
# ============================================================================

def example_environment_config():
    """
    Load configuration from environment variables.
    Useful for different environments (dev, staging, prod).
    """
    from app.services import APIConfig
    import os
    
    # Automatic loading from .env or environment variables
    config = APIConfig.from_environment()
    
    st.write("Configuration loaded from environment:")
    st.write(f"Environment: {config.environment.value}")
    st.write(f"Mock Mode: {config.mock_mode}")
    st.write(f"Cache TTL: {config.cache_ttl}s")


# ============================================================================
# Example 13: Analytics Dashboard
# ============================================================================

def example_analytics_dashboard():
    """
    Display supply chain analytics dashboard.
    """
    from app.services import get_streamlit_api_service
    import plotly.express as px
    
    service = get_streamlit_api_service()
    
    # Fetch analytics
    analytics = service.get_supply_chain_analytics()
    
    if analytics:
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Orders", analytics.get("total_orders", 0))
        
        with col2:
            st.metric("On-Time Rate", f"{analytics.get('on_time_delivery_rate', 0)}%")
        
        with col3:
            st.metric("Avg Lead Time", f"{analytics.get('average_lead_time', 0)} days")
        
        with col4:
            st.metric("Suppliers", analytics.get("supplier_count", 0))
        
        # Top products chart
        if "top_products" in analytics:
            top_products = analytics["top_products"]
            df = pd.DataFrame(top_products)
            
            fig = px.bar(df, x="name", y="units", title="Top Products")
            st.plotly_chart(fig)


# ============================================================================
# Example 14: Inventory Management
# ============================================================================

def example_inventory_management():
    """
    View and manage inventory levels.
    """
    from app.services import get_streamlit_api_service
    
    service = get_streamlit_api_service()
    
    # Fetch inventory
    inventory = service.get_inventory_levels()
    
    if inventory:
        df = pd.DataFrame(inventory)
        
        # Display with color coding for status
        st.dataframe(df, use_container_width=True)
        
        # Low stock alerts
        low_stock = [item for item in inventory if item.get("status") == "low"]
        
        if low_stock:
            st.warning(f"⚠️ {len(low_stock)} items with low stock!")
            for item in low_stock:
                st.write(f"- {item['product_name']}: {item['quantity']} (reorder: {item['reorder_point']})")


# ============================================================================
# Example 15: Health Check and Monitoring
# ============================================================================

def example_health_check():
    """
    Check API health and display status.
    """
    from app.services import get_streamlit_api_service
    
    service = get_streamlit_api_service()
    
    # Health check
    if service.health_check():
        st.success("✓ API is healthy")
        
        # Get cache stats
        stats = service.get_cache_stats()
        st.write("Cache Statistics:")
        st.json(stats)
    else:
        st.error("✗ API health check failed")


# ============================================================================
# Main Runner
# ============================================================================

if __name__ == "__main__":
    st.title("API Integration Examples")
    
    example = st.selectbox(
        "Select Example",
        [
            "Streamlit Service (Recommended)",
            "Unified Client",
            "HTTP Client",
            "Mock Client",
            "Upload & Process",
            "Forecasting",
            "Supplier Intelligence",
            "Chat Integration",
            "Report Generation",
            "Configuration",
            "Error Handling",
            "Environment Config",
            "Analytics Dashboard",
            "Inventory Management",
            "Health Check"
        ]
    )
    
    examples = {
        "Streamlit Service (Recommended)": example_streamlit_service,
        "Unified Client": example_unified_client,
        "HTTP Client": example_http_client,
        "Mock Client": example_mock_client,
        "Upload & Process": example_upload_and_process,
        "Forecasting": example_forecasting,
        "Supplier Intelligence": example_supplier_intelligence,
        "Chat Integration": example_chat_integration,
        "Report Generation": example_report_generation,
        "Configuration": example_configuration,
        "Error Handling": example_error_handling,
        "Environment Config": example_environment_config,
        "Analytics Dashboard": example_analytics_dashboard,
        "Inventory Management": example_inventory_management,
        "Health Check": example_health_check,
    }
    
    if example in examples:
        examples[example]()
