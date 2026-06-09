# 🚀 API Integration - Quick Reference

## TL;DR - Start Here

### In Your Component (Simplest)
```python
from app.services import get_streamlit_api_service

service = get_streamlit_api_service()

# Fetch data
suppliers = service.fetch_suppliers()

# Use data
if suppliers:
    st.dataframe(pd.DataFrame(suppliers))
# Errors displayed automatically
```

### In .env
```env
API_ENV=mock
API_MOCK_MODE=true
```

**That's it!** You now have API integration with caching and error handling.

---

## Common Tasks

### Fetch Suppliers
```python
suppliers = service.fetch_suppliers(page=1, limit=10)
```

### Fetch Inventory
```python
inventory = service.get_inventory_levels()
```

### Calculate KPIs
```python
kpis = service.calculate_kpis(data=df)
```

### Generate Forecast
```python
forecast = service.generate_forecast(
    data_points=[100, 120, 115, 130, 125],
    periods=7,
    method="linear"
)
```

### Send Chat Message
```python
response = service.send_chat_message(
    message="What's the inventory level?",
    session_id=session_id
)
```

### Get Analytics
```python
analytics = service.get_supply_chain_analytics()
```

---

## Configuration

### Environment Variables
```env
# Environment (mock, development, staging, production)
API_ENV=mock

# Server settings
API_BASE_URL=http://localhost:8000
API_VERSION=v1

# Authentication
API_USE_AUTH=false
# API_KEY=your-key
# API_TOKEN=your-token

# Performance
API_TIMEOUT=30
API_MAX_RETRIES=3
API_CACHE_ENABLED=true
API_CACHE_TTL=300

# Features
API_MOCK_MODE=true
API_SIMULATE_DELAY=true
API_VERBOSE_LOGGING=false
```

### Programmatic Configuration
```python
from app.services import APIConfig, UnifiedAPIClient

config = APIConfig(
    base_url="https://api.example.com",
    use_auth=True,
    api_key="your-key"
)

client = UnifiedAPIClient(config=config)
```

---

## Integration Methods

### ✅ Method 1: Streamlit Service (Recommended)
**Easiest, handles errors automatically**
```python
from app.services import get_streamlit_api_service
service = get_streamlit_api_service()
data = service.fetch_suppliers()
```

### Method 2: Unified Client
**More control**
```python
from app.services import get_unified_api_client
client = get_unified_api_client()
response = client.fetch_suppliers()
if response.success:
    data = response.data
```

### Method 3: Direct HTTP Client
**Production use**
```python
from app.services import HTTPAPIClient, APIConfig
config = APIConfig(base_url="https://api.example.com")
client = HTTPAPIClient(config=config)
```

### Method 4: Mock Client
**Development only**
```python
from app.services import MockAPIClient
client = MockAPIClient()
```

---

## All Available Methods

### Data Management
- `upload_data(filename, data)`
- `fetch_datasets()`
- `get_dataset(dataset_id)`
- `delete_dataset(dataset_id)`

### Forecasting
- `generate_forecast(data_points, periods, method)`
- `get_forecast_models()`
- `validate_forecast(forecast_id)`

### KPIs
- `calculate_kpis(data)`
- `get_kpi_history(metric_name)`
- `export_kpis(format)`

### Suppliers
- `fetch_suppliers(page, limit)`
- `get_supplier_details(supplier_id)`
- `update_supplier(supplier_id, data)`

### Analytics
- `get_supply_chain_analytics()`
- `get_inventory_levels()`
- `get_supply_chain_metrics()`

### Chat/AI
- `create_chat_session()`
- `send_chat_message(message, session_id)`
- `get_chat_history(session_id)`

### Reports
- `generate_report(report_type, data)`
- `get_report(report_id)`
- `download_report(report_id)`

### System
- `health_check()`
- `get_api_status()`

---

## Error Handling

### With Streamlit Service (Auto-handled)
```python
data = service.fetch_suppliers()
# If error: automatically displays with st.error()
# If success: returns data
```

### With Unified Client
```python
response = client.fetch_suppliers()

if response.success:
    data = response.data
else:
    print(f"Error: {response.error}")
```

---

## Caching

### Enable/Disable
```env
API_CACHE_ENABLED=true
API_CACHE_TTL=300  # seconds
```

### Clear Cache
```python
service.clear_cache()                    # Clear all
service.clear_cache("fetch_suppliers")  # Clear specific
```

### Get Stats
```python
stats = service.get_cache_stats()
print(stats)
```

### Bypass Cache
```python
data = service.fetch_suppliers(use_cache=False)
```

---

## Switching Modes

### At Runtime
```python
client = get_unified_api_client()

client.switch_mode(use_http=True)   # Use real API
client.switch_mode(use_http=False)  # Use mock
```

### Check Current Mode
```python
if client.config.mock_mode:
    print("Using Mock API")
else:
    print("Using HTTP API")
```

---

## Testing

### Run Examples
```bash
streamlit run app/services/USAGE_EXAMPLES_COMPLETE.py
```

### Test Health
```python
if service.health_check():
    st.success("API is healthy")
else:
    st.error("API connection failed")
```

### Test with Mock
```env
API_MOCK_MODE=true
API_SIMULATE_DELAY=false  # Disable delays for testing
```

---

## Response Format

All responses have this structure:
```python
response = {
    "success": True/False,
    "data": {...},           # Varies by endpoint
    "message": "...",
    "error": "...",         # Only if error
    "timestamp": "ISO"
}
```

---

## Troubleshooting

### Connection Failed
```python
if service.health_check():
    st.success("✓ API OK")
else:
    st.error("✗ API failed")
```

### Cache Issues
```python
service.clear_cache()
data = service.fetch_suppliers(use_cache=False)
```

### Auth Errors
```bash
# Check credentials in .env
echo $API_KEY
echo $API_TOKEN
echo $API_USE_AUTH
```

### Slow Requests
```env
# Disable mock delays
API_SIMULATE_DELAY=false

# Increase cache TTL
API_CACHE_TTL=600
```

---

## Real-World Examples

### Example 1: Suppliers Dashboard
```python
import streamlit as st
from app.services import get_streamlit_api_service

service = get_streamlit_api_service()

suppliers = service.fetch_suppliers(page=1, limit=20)
if suppliers and "suppliers" in suppliers:
    st.dataframe(pd.DataFrame(suppliers["suppliers"]))
```

### Example 2: Analytics Display
```python
analytics = service.get_supply_chain_analytics()
if analytics:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Orders", analytics["total_orders"])
    with col2:
        st.metric("On-Time %", analytics["on_time_delivery_rate"])
    with col3:
        st.metric("Lead Time", f"{analytics['average_lead_time']}d")
```

### Example 3: Forecast
```python
forecast = service.generate_forecast(
    data_points=df["sales"].values.tolist(),
    periods=30,
    method="linear"
)
if forecast:
    st.line_chart(forecast["forecast_values"])
```

### Example 4: Chat
```python
if "chat_session" not in st.session_state:
    session = service.create_chat_session()
    st.session_state.chat_session = session["session_id"]

message = st.text_input("Ask AI:")
if message:
    response = service.send_chat_message(
        message=message,
        session_id=st.session_state.chat_session
    )
    if response:
        st.write(response.get("response", ""))
```

---

## File Reference

| File | Purpose |
|------|---------|
| `config.py` | Configuration system |
| `api_client.py` | Mock API client |
| `http_client.py` | HTTP REST client |
| `cache.py` | Caching system |
| `unified_client.py` | Unified interface |
| `streamlit_service.py` | Streamlit wrapper ⭐ |
| `API_INTEGRATION_GUIDE.md` | Full documentation |
| `USAGE_EXAMPLES_COMPLETE.py` | 15 detailed examples |

---

## Key Features Summary

✅ **Easy to Use** - Single service with intuitive methods
✅ **Flexible** - Supports mock and real API
✅ **Robust** - Comprehensive error handling
✅ **Fast** - Intelligent caching
✅ **Secure** - Authentication support
✅ **Well-Documented** - Complete guides and examples
✅ **Production-Ready** - Enterprise features included

---

## Getting Help

1. **Quick Start**: This file (you're reading it!)
2. **Full Guide**: `API_INTEGRATION_GUIDE.md`
3. **Examples**: `USAGE_EXAMPLES_COMPLETE.py`
4. **Source Code**: Check the module files
5. **Config**: `config.py` for all options

---

## Next Steps

1. ✅ Import `get_streamlit_api_service`
2. ✅ Use in your component
3. ✅ Configure `.env`
4. ✅ Test with mock data
5. ✅ Switch to real API when ready

**You're all set! 🎉**

