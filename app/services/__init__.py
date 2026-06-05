"""
Services package for AI Supply Chain Frontend.
Provides API client and other service utilities.
"""

from .config import APIConfig, APIEnvironment, DEFAULT_CONFIG, APIEndpoints, APIErrorCodes, APIErrorMessages
from .api_client import MockAPIClient, get_api_client, reset_api_client, APIResponse
from .http_client import HTTPAPIClient
from .cache import APICache, MemoryCache
from .unified_client import UnifiedAPIClient, get_unified_api_client, reset_unified_api_client
from .streamlit_service import StreamlitAPIService, get_streamlit_api_service, api_call

__all__ = [
    # Configuration
    'APIConfig',
    'APIEnvironment',
    'DEFAULT_CONFIG',
    'APIEndpoints',
    'APIErrorCodes',
    'APIErrorMessages',
    
    # Clients
    'MockAPIClient',
    'HTTPAPIClient',
    'UnifiedAPIClient',
    'StreamlitAPIService',
    
    # Caching
    'APICache',
    'MemoryCache',
    
    # Functions
    'get_api_client',
    'reset_api_client',
    'get_unified_api_client',
    'reset_unified_api_client',
    'get_streamlit_api_service',
    'api_call',
    'APIResponse',
]
