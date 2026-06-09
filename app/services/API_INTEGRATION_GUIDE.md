# AI Supply Chain Frontend - API Integration Guide

## Overview

This guide provides comprehensive information on how to use the API integration system for the AI Supply Chain Frontend.

## Architecture

### Components

1. **APIConfig** (`config.py`) - Configuration management
2. **MockAPIClient** (`api_client.py`) - Mock API client for development
3. **HTTPAPIClient** (`http_client.py`) - Real HTTP client for production
4. **UnifiedAPIClient** (`unified_client.py`) - Unified interface supporting both
5. **Cache** (`cache.py`) - Response caching with multiple backends
6. **StreamlitAPIService** (`streamlit_service.py`) - Streamlit integration

### Data Flow

```
Component
  ↓
StreamlitAPIService (with caching & error handling)
  ↓
UnifiedAPIClient (switches between mock/HTTP)
  ↓
MockAPIClient or HTTPAPIClient
  ↓
API/Mock Data
```

## Configuration

### Environment Variables

Set these in `.env` or `.streamlit/secrets.toml`:

```env
# Environment (local, development, staging, production, mock)
API_ENV=mock

# API Server
API_BASE_URL=http://localhost:8000
API_VERSION=v1

# Authentication
API_USE_AUTH=false
# API_KEY=your-key
# API_TOKEN=your-token

# Performance
API_TIMEOUT=30
API_MAX_RETRIES=3
API_RETRY_DELAY=1.0

# Caching
API_CACHE_ENABLED=true
API_CACHE_TTL=300
API_BATCH_SIZE=100

# Features
API_SIMULATE_DELAY=true
API_VERBOSE_LOGGING=false
API_MOCK_MODE=true
```

### Programmatic Configuration

```python
from app.services import APIConfig, APIEnvironment

config = APIConfig(
    environment=APIEnvironment.DEVELOPMENT,
    base_url="https://api.example.com",
    api_key="your-api-key",
    use_auth=True,
    enable_caching=True,
    cache_ttl=600,
    mock_mode=False
)
```

## Usage Examples

### Basic Usage with Streamlit Service

The easiest way to use the API in components:

```python
import streamlit as st
from app.services import get_streamlit_api_service

# Get the service
service = get_streamlit_api_service()

# Fetch data
suppliers = service.fetch_suppliers(page=1, limit=10)
if suppliers:
    st.write(f"Found {len(suppliers)} suppliers")
else:
    st.error("Failed to fetch suppliers")
```

### Using Unified API Client Directly

```python
from app.services import get_unified_api_client

# Get the client
client = get_unified_api_client()

# Make API calls
response = client.fetch_suppliers(page=1, limit=10)

if response.success:
    print(f"Success: {response.message}")
    data = response.data
else:
    print(f"Error: {response.error}")
```

### Using HTTP Client (Production)

```python
from app.services import HTTPAPIClient, APIConfig

config = APIConfig(
    base_url="https://api.example.com",
    use_auth=True,
    api_key="your-api-key"
)

client = HTTPAPIClient(config=config)

# Make requests
response = client.fetch_suppliers()
print(response.to_dict())
```

### Using Mock Client (Development)

```python
from app.services import MockAPIClient

client = MockAPIClient(simulate_delay=True)

# Make requests - returns mock data
response = client.fetch_suppliers()
print(response.to_dict())
```

## API Endpoints

### Data Management

```python
# Upload data
service.upload_data(filename="data.csv", data=df_bytes)

# Fetch datasets
datasets = service.fetch_datasets()

# Get specific dataset
dataset = service.get_dataset(dataset_id="123")

# Delete dataset
service.delete_dataset(dataset_id="123")
```

### Forecasting

```python
# Generate forecast
forecast = service.generate_forecast(
    data_points=[100, 120, 115, 130, 125],
    periods=7,
    method="linear"  # or "exponential", "moving_average"
)

# Get available models
models = service.get_forecast_models()
```

### KPI Calculation

```python
# Calculate KPIs
kpis = service.calculate_kpis(data=df)

# Get KPI history
history = service.get_kpi_history(metric_name="on_time_delivery")

# Export KPIs
export = service.export_kpis(format="csv")  # or "excel", "json"
```

### Supplier Management

```python
# Fetch suppliers list
suppliers = service.fetch_suppliers(page=1, limit=10)

# Get supplier details
supplier = service.get_supplier_details(supplier_id=1)

# Update supplier
updated = service.update_supplier(
    supplier_id=1,
    data={"rating": 4.8, "status": "active"}
)
```

### Analytics

```python
# Get supply chain analytics
analytics = service.get_supply_chain_analytics()

# Get inventory levels
inventory = service.get_inventory_levels()

# Get supply chain metrics
metrics = service.get_supply_chain_metrics()
```

### Chat/AI

```python
# Create chat session
session = service.create_chat_session()
session_id = session.get("session_id")

# Send message
response = service.send_chat_message(
    message="What's the current inventory level?",
    session_id=session_id
)

# Get chat history
history = service.get_chat_history(session_id=session_id)
```

### Reports

```python
# Generate report
report = service.generate_report(
    report_type="summary",  # or "detailed", "executive"
    data=df
)

# Get report details
report_info = service.get_report(report_id="RPT-20240101")

# Download report
download_link = service.download_report(report_id="RPT-20240101")
```

## Error Handling

All API calls return an `APIResponse` object:

```python
from app.services import get_unified_api_client

client = get_unified_api_client()
response = client.fetch_suppliers()

if response.success:
    print(f"Success: {response.message}")
    data = response.data
else:
    print(f"Error: {response.error}")
    print(f"Message: {response.message}")
```

The Streamlit service handles errors automatically with UI feedback:

```python
from app.services import get_streamlit_api_service
import streamlit as st

service = get_streamlit_api_service()

# Errors are displayed automatically with st.error()
suppliers = service.fetch_suppliers(show_error=True)

# Or suppress error display
suppliers = service.fetch_suppliers(show_error=False)
if suppliers is None:
    # Handle error manually
    pass
```

## Caching

### How Caching Works

1. **Memory Cache** - Fast, session-scoped cache in Streamlit session state
2. **File Cache** - Persistent cache on disk (optional)
3. **Cache TTL** - Configurable time-to-live for cache entries

### Cache Control

```python
from app.services import get_streamlit_api_service

service = get_streamlit_api_service()

# Use cache (default for GET-like operations)
suppliers = service.fetch_suppliers(use_cache=True)

# Bypass cache
suppliers = service.fetch_suppliers(use_cache=False)

# Clear specific cache
service.clear_cache(endpoint="fetch_suppliers")

# Clear all cache
service.clear_cache()

# Get cache statistics
stats = service.get_cache_stats()
print(stats)
```

## Authentication

### API Key Authentication

```python
from app.services import APIConfig, UnifiedAPIClient

config = APIConfig(
    api_key="your-api-key-here",
    use_auth=True
)

client = UnifiedAPIClient(config=config)
```

### Bearer Token Authentication

```python
from app.services import APIConfig, UnifiedAPIClient

config = APIConfig(
    auth_token="your-bearer-token",
    use_auth=True
)

client = UnifiedAPIClient(config=config)
```

### Environment-based Authentication

```bash
# In .env file
API_USE_AUTH=true
API_KEY=your-api-key
API_TOKEN=your-bearer-token
```

## Switching Between Mock and HTTP Modes

```python
from app.services import get_unified_api_client

client = get_unified_api_client()

# Switch to HTTP mode (real API)
client.switch_mode(use_http=True)

# Switch back to mock mode
client.switch_mode(use_http=False)

# Check current mode
if client.config.mock_mode:
    print("Using mock API")
else:
    print("Using HTTP API")
```

## Integration with Components

### In a Streamlit Component

```python
import streamlit as st
from app.services import get_streamlit_api_service

def render_suppliers_view():
    st.markdown('<div class="section-header">Suppliers</div>', unsafe_allow_html=True)
    
    service = get_streamlit_api_service()
    
    # Fetch suppliers with automatic error handling
    suppliers_data = service.fetch_suppliers(page=1, limit=10)
    
    if suppliers_data:
        # Data retrieved successfully
        df = pd.DataFrame(suppliers_data)
        st.dataframe(df, use_container_width=True)
    # If None, error was already displayed by the service
```

## Debugging

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Now API calls will log detailed information
```

### Check API Health

```python
from app.services import get_streamlit_api_service

service = get_streamlit_api_service()

if service.health_check():
    st.success("API is healthy ✓")
else:
    st.error("API health check failed")
```

### View Configuration

```python
from app.services import get_streamlit_api_service

service = get_streamlit_api_service()
config = service.get_config()

st.write(f"Environment: {config.environment.value}")
st.write(f"Base URL: {config.base_url}")
st.write(f"Mock Mode: {config.mock_mode}")
st.write(f"Cache Enabled: {config.enable_caching}")
```

## Best Practices

1. **Use StreamlitAPIService** - Provides automatic caching and error handling
2. **Enable Caching** - Improves performance for repeated calls
3. **Implement Error Handling** - Always check response.success
4. **Use Appropriate Timeouts** - Set `API_TIMEOUT` based on expected response time
5. **Monitor Health** - Call health_check() periodically
6. **Clear Cache Strategically** - Only clear when data should be refreshed
7. **Use Mock Mode During Development** - Set `API_MOCK_MODE=true` in development

## Troubleshooting

### API Connection Failed

```bash
# Check configuration
echo $API_BASE_URL
echo $API_TIMEOUT

# Test connectivity
curl -X GET http://localhost:8000/api/v1/health
```

### Cache Issues

```python
from app.services import get_streamlit_api_service

service = get_streamlit_api_service()

# Clear cache and retry
service.clear_cache()
data = service.fetch_suppliers(use_cache=False)
```

### Authentication Errors

```bash
# Verify credentials
echo $API_KEY
echo $API_TOKEN

# Check if API_USE_AUTH is enabled
echo $API_USE_AUTH
```

## API Response Format

All API responses use the standard format:

```python
{
    "success": bool,      # True if request succeeded
    "data": Any,          # Response data (varies by endpoint)
    "message": str,       # Human-readable message
    "error": str,         # Error message (if failed)
    "timestamp": str      # ISO format timestamp
}
```

## Performance Optimization

### Batch Operations

```python
from app.services import APIConfig, UnifiedAPIClient

config = APIConfig(batch_size=50)  # Process 50 items at a time
client = UnifiedAPIClient(config=config)
```

### Reduce Cache TTL for Frequently Changing Data

```python
config = APIConfig(
    cache_ttl=60  # Cache for 60 seconds only
)
```

### Disable Unnecessary Features

```python
config = APIConfig(
    simulate_delay=False,      # Disable mock delays
    verbose_logging=False,     # Disable debug logging
)
```

## Additional Resources

- Configuration: `app/services/config.py`
- Mock Client: `app/services/api_client.py`
- HTTP Client: `app/services/http_client.py`
- Unified Client: `app/services/unified_client.py`
- Streamlit Service: `app/services/streamlit_service.py`
- Cache: `app/services/cache.py`

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Enable verbose logging for more details
3. Review the source code in `app/services/`
4. Check `USAGE_EXAMPLES.py` for example implementations
