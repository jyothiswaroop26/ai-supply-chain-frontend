"""
Example usage of the Mock API Client
Shows how to integrate the API client into Streamlit components
"""

# ============================================================================
# Example 1: Using the API client in a component
# ============================================================================

from services import get_api_client
import streamlit as st
import pandas as pd

# Get the API client instance
api = get_api_client()


def example_upload_data():
    """Example: Upload data and get API response."""
    if st.session_state.uploaded_df is not None:
        df = st.session_state.uploaded_df
        
        # Call mock API to process upload
        response = api.upload_data("my_data.csv", df)
        
        if response.success:
            st.success(f"✓ {response.message}")
            st.json(response.to_dict())
        else:
            st.error(f"✗ {response.error}")


def example_generate_forecast():
    """Example: Generate demand forecast using API."""
    data_points = [100.0, 150.0, 120.0, 180.0, 200.0, 190.0, 210.0]
    
    response = api.generate_forecast(
        data_points=data_points,
        periods=7,
        method="linear"
    )
    
    if response.success:
        forecast_data = response.data
        st.write("Forecast Results:")
        st.metric("Forecast Values", forecast_data['forecast_values'])
        st.metric("MAPE (Error Metric)", f"{forecast_data['mape']}%")


def example_calculate_kpis():
    """Example: Calculate KPIs using API."""
    if st.session_state.uploaded_df is not None:
        df = st.session_state.uploaded_df
        
        response = api.calculate_kpis(df)
        
        if response.success:
            kpis = response.data
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", f"{kpis['total_records']:,}")
            with col2:
                st.metric("Avg Value", f"${kpis['avg_value']:.2f}")
            with col3:
                st.metric("Total Sum", f"${kpis['total_sum']:.2f}")
            with col4:
                st.metric("Data Quality", f"{kpis['data_quality_score']:.1f}%")


def example_fetch_suppliers():
    """Example: Fetch supplier list from API."""
    response = api.fetch_suppliers(page=1, limit=10)
    
    if response.success:
        suppliers = response.data['suppliers']
        suppliers_df = pd.DataFrame(suppliers)
        
        st.dataframe(suppliers_df, use_container_width=True)


def example_get_analytics():
    """Example: Get supply chain analytics."""
    response = api.get_supply_chain_analytics()
    
    if response.success:
        analytics = response.data
        
        st.metric("On-Time Delivery Rate", f"{analytics['on_time_delivery_rate']}%")
        st.metric("Average Lead Time", f"{analytics['average_lead_time']} days")
        st.metric("Inventory Turnover", f"{analytics['inventory_turnover']}x")
        st.metric("Order Accuracy", f"{analytics['order_accuracy']}%")


def example_chat_interaction():
    """Example: Send chat message to API."""
    user_message = "What's the current inventory level?"
    
    response = api.send_chat_message(message=user_message)
    
    if response.success:
        chat_data = response.data
        st.write(chat_data['response'])
        
        if chat_data['follow_up_suggestions']:
            st.subheader("Suggested Follow-ups:")
            for suggestion in chat_data['follow_up_suggestions']:
                st.write(f"• {suggestion}")


def example_generate_report():
    """Example: Generate a report using API."""
    if st.session_state.uploaded_df is not None:
        df = st.session_state.uploaded_df
        
        response = api.generate_report(
            report_type="executive",
            data=df
        )
        
        if response.success:
            report = response.data
            st.write(f"Report ID: {report['report_id']}")
            st.write(f"Generated at: {report['generated_at']}")
            st.write(f"Rows analyzed: {report['rows_analyzed']}")


def example_inventory_levels():
    """Example: Get current inventory levels."""
    response = api.get_inventory_levels()
    
    if response.success:
        inventory = response.data
        inventory_df = pd.DataFrame(inventory)
        
        st.dataframe(inventory_df, use_container_width=True)
        
        # Show status summary
        status_counts = inventory_df['status'].value_counts()
        st.bar_chart(status_counts)


# ============================================================================
# Integration with Components
# ============================================================================

def integrate_api_in_chat_component():
    """
    Example: How to integrate the API client in the chat component.
    
    Place this in app/components/chat_ui.py:
    """
    
    code = """
from services import get_api_client

def render_chat_ui():
    api = get_api_client()
    
    # ... existing chat UI code ...
    
    if user_message:
        response = api.send_chat_message(user_message, session_id)
        
        if response.success:
            ai_response = response.data['response']
            st.write(ai_response)
    """
    
    return code


def integrate_api_in_forecast_component():
    """
    Example: How to integrate the API client in the forecast component.
    
    Place this in app/components/forecast_view.py:
    """
    
    code = """
from services import get_api_client

def render_forecast_view():
    api = get_api_client()
    
    # ... existing code to get data_points ...
    
    response = api.generate_forecast(
        data_points=historical_data.values.tolist(),
        periods=forecast_periods,
        method=forecast_method.lower().replace(" ", "_")
    )
    
    if response.success:
        forecast_values = response.data['forecast_values']
        # ... use forecast values in visualization ...
    """
    
    return code


# ============================================================================
# Testing the API Client
# ============================================================================

def test_api_client():
    """Test all API client endpoints."""
    api = get_api_client(simulate_delay=False)  # No delay for testing
    
    print("Testing Mock API Client...")
    print("-" * 50)
    
    # Test health check
    response = api.health_check()
    print(f"✓ Health Check: {response.message}")
    
    # Test fetch suppliers
    response = api.fetch_suppliers()
    print(f"✓ Fetch Suppliers: {response.message}")
    
    # Test analytics
    response = api.get_supply_chain_analytics()
    print(f"✓ Analytics: {response.message}")
    
    # Test inventory
    response = api.get_inventory_levels()
    print(f"✓ Inventory: {response.message}")
    
    # Test forecast
    response = api.generate_forecast([100, 120, 110, 140, 130], periods=5)
    print(f"✓ Forecast: {response.message}")
    
    # Test chat
    response = api.send_chat_message("What's the inventory level?")
    print(f"✓ Chat: {response.message}")
    
    print("-" * 50)
    print("All tests completed!")


if __name__ == "__main__":
    test_api_client()
