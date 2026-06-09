"""
Unified API Client - Integrates mock and HTTP clients with caching
"""

from typing import Optional, List, Dict, Any
from .config import APIConfig, DEFAULT_CONFIG
from .cache import MemoryCache, APICache
from .api_client import MockAPIClient, APIResponse
import logging

logger = logging.getLogger(__name__)


class UnifiedAPIClient:
    """
    Unified API client that supports both mock and HTTP backends with caching.
    Automatically switches between mock and real HTTP based on configuration.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        Initialize the unified API client.
        
        Args:
            config: API configuration object
        """
        self.config = config or DEFAULT_CONFIG
        self.logger = logger
        
        # Initialize cache
        self.memory_cache = MemoryCache(ttl=self.config.cache_ttl)
        
        # Initialize backend client based on configuration
        if self.config.mock_mode:
            self.logger.info(f"Using Mock API Client (Environment: {self.config.environment.value})")
            self.client = MockAPIClient(
                base_url=self.config.base_url,
                simulate_delay=self.config.simulate_delay
            )
        else:
            self.logger.info(f"Using HTTP API Client (Environment: {self.config.environment.value})")
            from .http_client import HTTPAPIClient
            self.client = HTTPAPIClient(config=self.config)
    
    def _get_cached(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Any]:
        """Get data from cache if caching is enabled."""
        if not self.config.enable_caching:
            return None
        return self.memory_cache.get(endpoint, params)
    
    def _set_cache(self, endpoint: str, data: Any, params: Optional[Dict] = None):
        """Set data in cache if caching is enabled."""
        if not self.config.enable_caching:
            return
        self.memory_cache.set(endpoint, data, params)
    
    def _make_cached_request(
        self,
        endpoint: str,
        method_name: str,
        *args,
        **kwargs
    ) -> APIResponse:
        """
        Make a request with caching support.
        
        Args:
            endpoint: API endpoint identifier
            method_name: Name of the method to call on the backend client
            *args: Positional arguments for the method
            **kwargs: Keyword arguments for the method
            
        Returns:
            APIResponse object
        """
        # Check cache for GET-like operations
        if endpoint in ["fetch_datasets", "fetch_suppliers", "get_inventory_levels", "get_supply_chain_analytics"]:
            cached = self._get_cached(endpoint, kwargs)
            if cached is not None:
                self.logger.debug(f"Returning cached response for {endpoint}")
                return APIResponse(success=True, data=cached, message="From cache")
        
        # Make actual request
        method = getattr(self.client, method_name)
        response = method(*args, **kwargs)
        
        # Cache successful responses
        if response.success and endpoint not in ["send_chat_message", "upload_data"]:
            self._set_cache(endpoint, response.data, kwargs)
        
        return response
    
    # =========================================================================
    # Data Management Endpoints
    # =========================================================================
    
    def upload_data(self, filename: str, data) -> APIResponse:
        """Upload supply chain data."""
        return self._make_cached_request("upload_data", "upload_data", filename, data)
    
    def fetch_datasets(self) -> APIResponse:
        """Fetch available datasets."""
        return self._make_cached_request("fetch_datasets", "fetch_datasets")
    
    def get_dataset(self, dataset_id: str) -> APIResponse:
        """Get a specific dataset."""
        if not self.config.mock_mode:
            return self._make_cached_request("get_dataset", "get_dataset", dataset_id)
        return APIResponse(success=False, error="Not implemented in mock client")
    
    def delete_dataset(self, dataset_id: str) -> APIResponse:
        """Delete a dataset."""
        if not self.config.mock_mode:
            return self.client.delete_dataset(dataset_id)
        self.memory_cache.clear("fetch_datasets")
        return APIResponse(success=True, message="Dataset deleted")
    
    # =========================================================================
    # Forecasting Endpoints
    # =========================================================================
    
    def generate_forecast(
        self,
        data_points: List[float],
        periods: int = 7,
        method: str = "linear"
    ) -> APIResponse:
        """Generate demand forecast."""
        return self._make_cached_request(
            "generate_forecast",
            "generate_forecast",
            data_points,
            periods,
            method
        )
    
    def get_forecast_models(self) -> APIResponse:
        """Get available forecast models."""
        if not self.config.mock_mode:
            return self._make_cached_request("get_forecast_models", "get_forecast_models")
        return APIResponse(
            success=True,
            data=["linear", "exponential", "moving_average"],
            message="Available models"
        )
    
    def validate_forecast(self, forecast_id: str) -> APIResponse:
        """Validate a forecast."""
        if not self.config.mock_mode:
            return self.client.validate_forecast(forecast_id)
        return APIResponse(success=True, message="Forecast validated")
    
    # =========================================================================
    # KPI Calculation Endpoints
    # =========================================================================
    
    def calculate_kpis(self, data) -> APIResponse:
        """Calculate supply chain KPIs."""
        return self._make_cached_request("calculate_kpis", "calculate_kpis", data)
    
    def get_kpi_history(self, metric_name: str) -> APIResponse:
        """Get KPI calculation history."""
        if not self.config.mock_mode:
            return self._make_cached_request("get_kpi_history", "get_kpi_history", metric_name)
        return APIResponse(
            success=True,
            data=[],
            message="KPI history retrieved"
        )
    
    def export_kpis(self, format: str = "csv") -> APIResponse:
        """Export KPIs in specified format."""
        if not self.config.mock_mode:
            return self.client.export_kpis(format)
        return APIResponse(success=True, message=f"KPIs exported as {format}")
    
    # =========================================================================
    # Supplier Management Endpoints
    # =========================================================================
    
    def fetch_suppliers(self, page: int = 1, limit: int = 10) -> APIResponse:
        """Fetch list of suppliers."""
        return self._make_cached_request(
            "fetch_suppliers",
            "fetch_suppliers",
            page,
            limit
        )
    
    def get_supplier_details(self, supplier_id: int) -> APIResponse:
        """Get detailed supplier information."""
        return self._make_cached_request(
            "get_supplier_details",
            "get_supplier_details",
            supplier_id
        )
    
    def update_supplier(self, supplier_id: int, data: Dict) -> APIResponse:
        """Update supplier information."""
        if not self.config.mock_mode:
            return self.client.update_supplier(supplier_id, data)
        self.memory_cache.clear("fetch_suppliers")
        return APIResponse(success=True, message="Supplier updated")
    
    # =========================================================================
    # Analytics Endpoints
    # =========================================================================
    
    def get_supply_chain_analytics(self) -> APIResponse:
        """Get supply chain analytics dashboard data."""
        return self._make_cached_request("get_supply_chain_analytics", "get_supply_chain_analytics")
    
    def get_inventory_levels(self) -> APIResponse:
        """Get current inventory levels."""
        return self._make_cached_request("get_inventory_levels", "get_inventory_levels")
    
    def get_supply_chain_metrics(self) -> APIResponse:
        """Get supply chain metrics."""
        if not self.config.mock_mode:
            return self._make_cached_request("get_supply_chain_metrics", "get_supply_chain_metrics")
        return self.get_supply_chain_analytics()
    
    # =========================================================================
    # Chat/AI Endpoints
    # =========================================================================
    
    def send_chat_message(self, message: str, session_id: Optional[str] = None) -> APIResponse:
        """Send a chat message to the AI."""
        return self._make_cached_request(
            "send_chat_message",
            "send_chat_message",
            message,
            session_id
        )
    
    def create_chat_session(self) -> APIResponse:
        """Create a new chat session."""
        if not self.config.mock_mode:
            return self.client.create_chat_session()
        return APIResponse(
            success=True,
            data={"session_id": self.client._generate_session_id()},
            message="Chat session created"
        )
    
    def get_chat_history(self, session_id: str) -> APIResponse:
        """Get chat history for a session."""
        if not self.config.mock_mode:
            return self.client.get_chat_history(session_id)
        return APIResponse(success=True, data=[], message="Chat history retrieved")
    
    # =========================================================================
    # Report Generation Endpoints
    # =========================================================================
    
    def generate_report(self, report_type: str, data=None) -> APIResponse:
        """Generate a report."""
        if not self.config.mock_mode and data is not None:
            return self.client.generate_report(report_type, {"data": data})
        return self._make_cached_request("generate_report", "generate_report", report_type, data)
    
    def get_report(self, report_id: str) -> APIResponse:
        """Get report details."""
        if not self.config.mock_mode:
            return self.client.get_report(report_id)
        return APIResponse(success=True, message="Report retrieved")
    
    def download_report(self, report_id: str) -> APIResponse:
        """Get report download link."""
        if not self.config.mock_mode:
            return self.client.download_report(report_id)
        return self._make_cached_request("download_report", "download_report", report_id)
    
    # =========================================================================
    # System Endpoints
    # =========================================================================
    
    def health_check(self) -> APIResponse:
        """Check API health status."""
        return self._make_cached_request("health_check", "health_check")
    
    def get_api_status(self) -> APIResponse:
        """Get detailed API status."""
        return self.health_check()
    
    # =========================================================================
    # Cache Management
    # =========================================================================
    
    def clear_cache(self, endpoint: Optional[str] = None):
        """Clear cache entries."""
        self.memory_cache.clear(endpoint)
        self.logger.info(f"Cache cleared for {endpoint or 'all endpoints'}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.memory_cache.get_cache_stats()
    
    def switch_mode(self, use_http: bool = False):
        """Switch between mock and HTTP mode."""
        self.config.mock_mode = not use_http
        self.clear_cache()
        
        if use_http:
            self.logger.info("Switched to HTTP mode")
            from .http_client import HTTPAPIClient
            self.client = HTTPAPIClient(config=self.config)
        else:
            self.logger.info("Switched to Mock mode")
            self.client = MockAPIClient(
                base_url=self.config.base_url,
                simulate_delay=self.config.simulate_delay
            )
    
    def close(self):
        """Close the client and cleanup resources."""
        if hasattr(self.client, 'close'):
            self.client.close()
        self.logger.info("API client closed")


# Singleton instance for module-level access
_unified_client: Optional[UnifiedAPIClient] = None


def get_unified_api_client(config: Optional[APIConfig] = None) -> UnifiedAPIClient:
    """
    Get or create the unified API client singleton.
    
    Args:
        config: Optional API configuration
        
    Returns:
        UnifiedAPIClient instance
    """
    global _unified_client
    if _unified_client is None:
        _unified_client = UnifiedAPIClient(config or DEFAULT_CONFIG)
    return _unified_client


def reset_unified_api_client():
    """Reset the unified API client singleton."""
    global _unified_client
    if _unified_client:
        _unified_client.close()
    _unified_client = None
