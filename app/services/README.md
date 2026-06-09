# Services Module - Complete API Integration

**⭐ Complete, production-ready API integration system for the AI Supply Chain Frontend.**

This module provides unified API integration supporting both mock (development) and HTTP (production) backends with intelligent caching, error handling, and Streamlit integration.

## Quick Start (30 seconds)

### 1. Import Service
```python
from app.services import get_streamlit_api_service
```

### 2. Use in Your Component
```python
service = get_streamlit_api_service()
suppliers = service.fetch_suppliers()

if suppliers:
    st.dataframe(pd.DataFrame(suppliers))
```

### 3. Configure (`.env`)
```env
API_ENV=mock
API_MOCK_MODE=true
```

**Done!** Your component now has full API integration with caching and error handling.

---

## Module Overview

**The Mock API Client** provides a comprehensive set of mock API endpoints for the AI Supply Chain Frontend application. It's designed for development, testing, and prototyping without requiring a real backend server.

## Features

- **Data Management**: Upload, fetch, and manage datasets
- **Forecasting**: Generate demand forecasts using multiple methods
- **KPI Calculations**: Calculate supply chain key performance indicators
- **Supplier Management**: Fetch and manage supplier information
- **Analytics**: Get supply chain analytics and insights
- **Chat/AI**: Send chat messages and get AI responses
- **Reporting**: Generate and download reports
- **Inventory Management**: Track inventory levels

## Installation

The API client is already included in the services package. Simply import it:

```python
from services import get_api_client

api = get_api_client()
```

## Quick Start

### Basic Usage

```python
from services import get_api_client
import pandas as pd

# Get API client instance
api = get_api_client()

# Upload data
df = pd.read_csv("data.csv")
response = api.upload_data("data.csv", df)

if response.success:
    print(f"Success: {response.message}")
    print(f"Data: {response.data}")
else:
    print(f"Error: {response.error}")
```

### Network Simulation

By default, the API client simulates network delays (200-800ms) for realistic behavior:

```python
# With delay simulation (default)
api = get_api_client(simulate_delay=True)

# Without delay simulation (for testing)
api = get_api_client(simulate_delay=False)
```

## API Endpoints

### Data Management

#### `upload_data(filename: str, data: pd.DataFrame) -> APIResponse`

Upload a CSV file and get a summary.

```python
response = api.upload_data("supply_data.csv", df)
# Returns: filename, rows, columns, column_names, data_types, uploaded_at, file_size_kb
```

#### `fetch_datasets() -> APIResponse`

Fetch list of available datasets.

```python
response = api.fetch_datasets()
# Returns: list of dataset objects with metadata
```

### Forecasting

#### `generate_forecast(data_points: List[float], periods: int, method: str) -> APIResponse`

Generate demand forecasts using specified method.

**Methods:**
- `"linear"` - Linear trend forecasting
- `"exponential"` - Exponential smoothing
- `"moving_average"` - Moving average forecasting

```python
data = [100, 150, 120, 180, 200, 190, 210]
response = api.generate_forecast(
    data_points=data,
    periods=7,
    method="linear"
)
# Returns: forecast_values, confidence_interval, mape, rmse, method
```

### KPI Calculations

#### `calculate_kpis(data: pd.DataFrame) -> APIResponse`

Calculate key performance indicators from data.

```python
response = api.calculate_kpis(df)
# Returns: total_records, avg_value, max_value, min_value, total_sum, 
#          std_dev, data_quality_score, mean_value, cv_percentage, 
#          missing_values_count, complete_records
```

### Supplier Management

#### `fetch_suppliers(page: int = 1, limit: int = 10) -> APIResponse`

Fetch paginated list of suppliers.

```python
response = api.fetch_suppliers(page=1, limit=10)
# Returns: suppliers list, total count, pagination metadata
```

#### `get_supplier_details(supplier_id: int) -> APIResponse`

Get detailed information about a specific supplier.

```python
response = api.get_supplier_details(supplier_id=1)
# Returns: supplier contact info, ratings, performance metrics, certifications
```

### Analytics

#### `get_supply_chain_analytics() -> APIResponse`

Get comprehensive supply chain analytics.

```python
response = api.get_supply_chain_analytics()
# Returns: total_orders, on_time_delivery_rate, average_lead_time, 
#          inventory_turnover, order_accuracy, trends, top_products
```

#### `get_inventory_levels() -> APIResponse`

Get current inventory levels across all SKUs.

```python
response = api.get_inventory_levels()
# Returns: list of inventory items with SKU, quantity, status, warehouse info
```

### Chat/AI

#### `send_chat_message(message: str, session_id: Optional[str] = None) -> APIResponse`

Send a chat message and get AI response.

```python
response = api.send_chat_message(
    message="What's the current inventory level?",
    session_id="optional_session_id"
)
# Returns: response text, confidence score, session_id, follow_up_suggestions
```

### Reporting

#### `generate_report(report_type: str, data: pd.DataFrame) -> APIResponse`

Generate a report from data.

**Report Types:**
- `"summary"` - Summary report
- `"detailed"` - Detailed analysis report
- `"executive"` - Executive summary

```python
response = api.generate_report(
    report_type="executive",
    data=df
)
# Returns: report_id, type, title, generated_at, rows_analyzed, export_formats
```

#### `download_report(report_id: str) -> APIResponse`

Get download link for a generated report.

```python
response = api.download_report(report_id="RPT-20240115120000")
# Returns: download_url, filename, file_size_kb, expires_in_hours
```

### Utility

#### `health_check() -> APIResponse`

Check API health status.

```python
response = api.health_check()
# Returns: status, version, available endpoints
```

## Response Format

All API responses follow a standard format:

```python
@dataclass
class APIResponse:
    success: bool           # True if request succeeded
    data: Any              # Response data (varies by endpoint)
    message: str           # Human-readable message
    error: Optional[str]   # Error message if success=False
    timestamp: str         # ISO format timestamp
```

### Checking Responses

```python
response = api.fetch_suppliers()

if response.success:
    suppliers = response.data['suppliers']
    print(f"Retrieved {len(suppliers)} suppliers")
else:
    print(f"Error: {response.error}")

# Convert to dictionary
response_dict = response.to_dict()
```

## Integration Examples

### Integration with Chat Component

```python
# In app/components/chat_ui.py
from services import get_api_client

api = get_api_client()

def handle_chat_message(user_input):
    response = api.send_chat_message(user_input)
    if response.success:
        return response.data['response']
    return "Error processing message"
```

### Integration with Forecast Component

```python
# In app/components/forecast_view.py
from services import get_api_client

api = get_api_client()

response = api.generate_forecast(
    data_points=historical_data.tolist(),
    periods=forecast_periods,
    method=forecast_method.lower()
)

if response.success:
    forecast_values = response.data['forecast_values']
    # Use in visualization
```

### Integration with KPI Component

```python
# In app/components/kpi.py
from services import get_api_client

api = get_api_client()

response = api.calculate_kpis(df)
if response.success:
    kpis = response.data
    st.metric("On-Time Delivery", f"{kpis['total_records']:,}")
```

## Testing

### Test All Endpoints

```python
from services.USAGE_EXAMPLES import test_api_client

test_api_client()
```

### Manual Testing

```python
from services import get_api_client

api = get_api_client(simulate_delay=False)

# Test each endpoint
print(api.health_check().message)
print(api.fetch_suppliers().message)
print(api.get_supply_chain_analytics().message)
```

## Configuration

### Disabling Network Simulation

For faster development/testing, disable network delays:

```python
api = get_api_client(simulate_delay=False)
```

### Resetting the Client

To reset the singleton instance:

```python
from services import reset_api_client

reset_api_client()
api = get_api_client()  # Fresh instance
```

## Data Characteristics

### Mock Data

The API client generates realistic mock data:

- **Suppliers**: 4 pre-defined suppliers with realistic metrics
- **Forecasts**: Generated using statistical methods (linear, exponential, moving average)
- **KPIs**: Calculated from provided data
- **Inventory**: Predefined SKUs with realistic stock levels
- **Analytics**: Realistic supply chain metrics

### Data Persistence

Mock data is NOT persisted between API client instances. Each instance maintains its own state.

## Error Handling

### Standard Error Responses

```python
response = api.calculate_kpis(empty_dataframe)

if not response.success:
    print(f"Error: {response.error}")
    print(f"Message: {response.message}")
```

### Common Error Scenarios

1. **Insufficient Data**: Forecasting requires at least 2 data points
2. **No Numeric Columns**: KPI calculation requires numeric data
3. **Invalid Supplier ID**: Requesting non-existent supplier returns error

## Performance

- **Simulated Delay**: 200-800ms per request (realistic network latency)
- **Actual Processing**: < 100ms for mock calculations
- **Memory Usage**: Minimal, no data persistence

## Future Enhancements

Potential improvements for the mock API client:

1. Data persistence (JSON/SQLite backend)
2. Advanced forecast models (ARIMA, Prophet)
3. Real-time inventory updates
4. Multi-user chat sessions
5. Custom KPI definitions
6. Report scheduling and notifications

## Troubleshooting

### Module Not Found Error

```
ModuleNotFoundError: No module named 'services'
```

**Solution**: Ensure you're importing from the correct path:
```python
from app.services import get_api_client
# or if running from app directory
from services import get_api_client
```

### No Numeric Data Error

```
APIResponse(success=False, error="No numeric data found")
```

**Solution**: Ensure your DataFrame has numeric columns for KPI calculations.

### Insufficient Data Points

```
APIResponse(success=False, error="Insufficient data points")
```

**Solution**: Provide at least 2 data points for forecasting.

## API Reference

For complete method signatures and more examples, see [USAGE_EXAMPLES.py](USAGE_EXAMPLES.py).

## License

Part of the AI Supply Chain Frontend project.
```
