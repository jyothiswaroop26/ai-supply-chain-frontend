"""
Streamlit Integration Service
Provides Streamlit-specific API integration with session state management.
"""

import streamlit as st
from typing import Optional, Any, Dict, List, Callable
import logging

from .unified_client import get_unified_api_client, UnifiedAPIClient
from .api_client import APIResponse
from .config import APIConfig, DEFAULT_CONFIG

logger = logging.getLogger(__name__)


class StreamlitAPIService:
    """
    Streamlit-integrated API service with session state management.
    Handles caching and state management automatically.
    """
    
    def __init__(self):
        """Initialize the Streamlit API service."""
        self.client = get_unified_api_client()
        self._init_session_state()
    
    @staticmethod
    def _init_session_state():
        """Initialize session state for API data."""
        if "api_responses" not in st.session_state:
            st.session_state.api_responses = {}
        if "api_errors" not in st.session_state:
            st.session_state.api_errors = {}
        if "api_loading" not in st.session_state:
            st.session_state.api_loading = {}
        if "api_cache" not in st.session_state:
            st.session_state.api_cache = {}
    
    def _cache_key(self, endpoint: str, **params) -> str:
        """Generate a cache key for responses."""
        import hashlib
        import json
        key = f"{endpoint}:{json.dumps(params, sort_keys=True, default=str)}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def execute_api_call(
        self,
        endpoint: str,
        method_name: str,
        *args,
        use_cache: bool = True,
        show_error: bool = True,
        **kwargs
    ) -> Optional[Any]:
        """
        Execute an API call with error handling and caching.
        
        Args:
            endpoint: Name of the endpoint
            method_name: Name of the method to call on the API client
            *args: Positional arguments
            use_cache: Whether to use session cache
            show_error: Whether to display errors in UI
            **kwargs: Keyword arguments
            
        Returns:
            Response data or None if error
        """
        cache_key = self._cache_key(endpoint, **kwargs)
        
        # Check session cache
        if use_cache and cache_key in st.session_state.api_cache:
            logger.debug(f"Using cached data for {endpoint}")
            return st.session_state.api_cache[cache_key]
        
        # Mark as loading
        st.session_state.api_loading[cache_key] = True
        
        try:
            # Make API call
            method = getattr(self.client, method_name)
            response: APIResponse = method(*args, **kwargs)
            
            # Handle response
            if response.success:
                st.session_state.api_cache[cache_key] = response.data
                st.session_state.api_errors.pop(cache_key, None)
                logger.debug(f"Success: {endpoint}")
                return response.data
            else:
                error_msg = response.error or response.message or "Unknown error"
                st.session_state.api_errors[cache_key] = error_msg
                
                if show_error:
                    st.error(f"API Error: {error_msg}")
                
                logger.error(f"API Error [{endpoint}]: {error_msg}")
                return None
                
        except Exception as e:
            error_msg = str(e)
            st.session_state.api_errors[cache_key] = error_msg
            
            if show_error:
                st.error(f"Error: {error_msg}")
            
            logger.error(f"Exception [{endpoint}]: {error_msg}")
            return None
            
        finally:
            st.session_state.api_loading[cache_key] = False
    
    # =========================================================================
    # Data Management
    # =========================================================================
    
    def upload_data(self, filename: str, data) -> bool:
        """Upload data file."""
        result = self.execute_api_call(
            "upload_data",
            "upload_data",
            filename,
            data,
            use_cache=False,
            show_error=True
        )
        return result is not None
    
    def fetch_datasets(self) -> Optional[List[Dict]]:
        """Fetch available datasets."""
        return self.execute_api_call(
            "fetch_datasets",
            "fetch_datasets",
            use_cache=True,
            show_error=False
        )
    
    # =========================================================================
    # Forecasting
    # =========================================================================
    
    def generate_forecast(
        self,
        data_points: List[float],
        periods: int = 7,
        method: str = "linear"
    ) -> Optional[Dict]:
        """Generate demand forecast."""
        return self.execute_api_call(
            "generate_forecast",
            "generate_forecast",
            data_points,
            periods,
            method,
            use_cache=False,
            show_error=True
        )
    
    def get_forecast_models(self) -> Optional[List[str]]:
        """Get available forecast models."""
        return self.execute_api_call(
            "get_forecast_models",
            "get_forecast_models",
            use_cache=True,
            show_error=False
        )
    
    # =========================================================================
    # KPI Calculation
    # =========================================================================
    
    def calculate_kpis(self, data) -> Optional[Dict]:
        """Calculate supply chain KPIs."""
        return self.execute_api_call(
            "calculate_kpis",
            "calculate_kpis",
            data,
            use_cache=False,
            show_error=True
        )
    
    # =========================================================================
    # Supplier Management
    # =========================================================================
    
    def fetch_suppliers(self, page: int = 1, limit: int = 10) -> Optional[Dict]:
        """Fetch list of suppliers."""
        return self.execute_api_call(
            "fetch_suppliers",
            "fetch_suppliers",
            page,
            limit,
            use_cache=True,
            show_error=False,
            page=page,
            limit=limit
        )
    
    def get_supplier_details(self, supplier_id: int) -> Optional[Dict]:
        """Get detailed supplier information."""
        return self.execute_api_call(
            "get_supplier_details",
            "get_supplier_details",
            supplier_id,
            use_cache=True,
            show_error=False,
            supplier_id=supplier_id
        )
    
    # =========================================================================
    # Analytics
    # =========================================================================
    
    def get_supply_chain_analytics(self) -> Optional[Dict]:
        """Get supply chain analytics."""
        return self.execute_api_call(
            "get_supply_chain_analytics",
            "get_supply_chain_analytics",
            use_cache=True,
            show_error=False
        )
    
    def get_inventory_levels(self) -> Optional[List[Dict]]:
        """Get current inventory levels."""
        return self.execute_api_call(
            "get_inventory_levels",
            "get_inventory_levels",
            use_cache=True,
            show_error=False
        )
    
    # =========================================================================
    # Chat/AI
    # =========================================================================
    
    def send_chat_message(
        self,
        message: str,
        session_id: Optional[str] = None
    ) -> Optional[Dict]:
        """Send a chat message."""
        return self.execute_api_call(
            "send_chat_message",
            "send_chat_message",
            message,
            session_id,
            use_cache=False,
            show_error=True,
            message=message,
            session_id=session_id
        )
    
    def create_chat_session(self) -> Optional[Dict]:
        """Create a new chat session."""
        result = self.execute_api_call(
            "create_chat_session",
            "create_chat_session",
            use_cache=False,
            show_error=True
        )
        return result
    
    # =========================================================================
    # Reports
    # =========================================================================
    
    def generate_report(self, report_type: str, data=None) -> Optional[Dict]:
        """Generate a report."""
        return self.execute_api_call(
            "generate_report",
            "generate_report",
            report_type,
            data,
            use_cache=False,
            show_error=True,
            report_type=report_type
        )
    
    def download_report(self, report_id: str) -> Optional[Dict]:
        """Get report download link."""
        return self.execute_api_call(
            "download_report",
            "download_report",
            report_id,
            use_cache=True,
            show_error=False,
            report_id=report_id
        )
    
    # =========================================================================
    # System
    # =========================================================================
    
    def health_check(self) -> bool:
        """Check API health status."""
        result = self.execute_api_call(
            "health_check",
            "health_check",
            use_cache=True,
            show_error=False
        )
        return result is not None
    
    # =========================================================================
    # Cache Management
    # =========================================================================
    
    def clear_cache(self, endpoint: Optional[str] = None):
        """Clear cache entries."""
        if endpoint:
            cache_keys_to_remove = [
                k for k in st.session_state.api_cache.keys()
                if k.startswith(endpoint)
            ]
            for k in cache_keys_to_remove:
                del st.session_state.api_cache[k]
        else:
            st.session_state.api_cache.clear()
        
        self.client.clear_cache(endpoint)
        logger.info(f"Cache cleared for {endpoint or 'all endpoints'}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "session_cache_size": len(st.session_state.api_cache),
            "unified_client_stats": self.client.get_cache_stats()
        }
    
    # =========================================================================
    # Configuration
    # =========================================================================
    
    def switch_mode(self, use_http: bool = False):
        """Switch between mock and HTTP mode."""
        self.client.switch_mode(use_http)
        self.clear_cache()
        mode = "HTTP" if use_http else "Mock"
        st.info(f"Switched to {mode} mode")
    
    def get_config(self) -> APIConfig:
        """Get current API configuration."""
        return self.client.config


# Singleton service instance
_service: Optional[StreamlitAPIService] = None


def get_streamlit_api_service() -> StreamlitAPIService:
    """Get or create the Streamlit API service singleton."""
    global _service
    if _service is None:
        _service = StreamlitAPIService()
    return _service


# Convenience function for common usage
def api_call(
    endpoint: str,
    method_name: str,
    *args,
    **kwargs
) -> Optional[Any]:
    """
    Convenience function to make API calls.
    
    Usage:
        data = api_call("fetch_suppliers", "fetch_suppliers")
    """
    service = get_streamlit_api_service()
    return service.execute_api_call(endpoint, method_name, *args, **kwargs)
