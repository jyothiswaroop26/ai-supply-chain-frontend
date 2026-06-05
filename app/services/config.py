"""
API Configuration Module
Manages API endpoints, settings, and environment variables for the application.
"""

import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class APIEnvironment(Enum):
    """Supported API environments."""
    LOCAL = "local"
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    MOCK = "mock"


@dataclass
class APIConfig:
    """API configuration settings."""
    
    # Environment settings
    environment: APIEnvironment = APIEnvironment.MOCK
    base_url: str = "http://localhost:8000"
    api_version: str = "v1"
    
    # Authentication
    api_key: Optional[str] = None
    auth_token: Optional[str] = None
    use_auth: bool = False
    
    # Timeouts and retries
    request_timeout: int = 30  # seconds
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds
    
    # Performance
    enable_caching: bool = True
    cache_ttl: int = 300  # seconds
    batch_size: int = 100
    
    # Features
    simulate_delay: bool = True
    verbose_logging: bool = False
    mock_mode: bool = True  # Use mock data by default
    
    @property
    def api_url(self) -> str:
        """Get the full API base URL with version."""
        return f"{self.base_url}/api/{self.api_version}"
    
    @classmethod
    def from_environment(cls) -> "APIConfig":
        """Create configuration from environment variables."""
        env = os.getenv("API_ENV", "mock").lower()
        
        try:
            environment = APIEnvironment(env)
        except ValueError:
            environment = APIEnvironment.MOCK
        
        return cls(
            environment=environment,
            base_url=os.getenv("API_BASE_URL", "http://localhost:8000"),
            api_version=os.getenv("API_VERSION", "v1"),
            api_key=os.getenv("API_KEY"),
            auth_token=os.getenv("API_TOKEN"),
            use_auth=os.getenv("API_USE_AUTH", "false").lower() == "true",
            request_timeout=int(os.getenv("API_TIMEOUT", "30")),
            max_retries=int(os.getenv("API_MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("API_RETRY_DELAY", "1.0")),
            enable_caching=os.getenv("API_CACHE_ENABLED", "true").lower() == "true",
            cache_ttl=int(os.getenv("API_CACHE_TTL", "300")),
            batch_size=int(os.getenv("API_BATCH_SIZE", "100")),
            simulate_delay=os.getenv("API_SIMULATE_DELAY", "true").lower() == "true",
            verbose_logging=os.getenv("API_VERBOSE_LOGGING", "false").lower() == "true",
            mock_mode=os.getenv("API_MOCK_MODE", "true").lower() == "true",
        )


# API Endpoint definitions
class APIEndpoints:
    """API endpoint paths."""
    
    # Data Management
    UPLOAD_DATA = "/data/upload"
    FETCH_DATASETS = "/data/datasets"
    GET_DATASET = "/data/datasets/{dataset_id}"
    DELETE_DATASET = "/data/datasets/{dataset_id}"
    
    # Forecasting
    GENERATE_FORECAST = "/forecast/generate"
    GET_FORECAST_MODELS = "/forecast/models"
    VALIDATE_FORECAST = "/forecast/validate"
    
    # KPI Calculation
    CALCULATE_KPIS = "/kpi/calculate"
    GET_KPI_HISTORY = "/kpi/history"
    EXPORT_KPIS = "/kpi/export"
    
    # Supplier Management
    FETCH_SUPPLIERS = "/suppliers"
    GET_SUPPLIER_DETAILS = "/suppliers/{supplier_id}"
    UPDATE_SUPPLIER = "/suppliers/{supplier_id}"
    
    # Analytics
    GET_ANALYTICS = "/analytics"
    GET_INVENTORY_LEVELS = "/inventory"
    GET_SUPPLY_CHAIN_METRICS = "/metrics"
    
    # Chat/AI
    SEND_CHAT_MESSAGE = "/chat/message"
    CREATE_CHAT_SESSION = "/chat/session"
    GET_CHAT_HISTORY = "/chat/history"
    
    # Reports
    GENERATE_REPORT = "/reports/generate"
    GET_REPORT = "/reports/{report_id}"
    DOWNLOAD_REPORT = "/reports/{report_id}/download"
    
    # System
    HEALTH_CHECK = "/health"
    GET_API_STATUS = "/status"


# Error codes and messages
class APIErrorCodes:
    """API error code constants."""
    
    # Success
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    
    # Client errors
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    
    # Server errors
    INTERNAL_ERROR = 500
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class APIErrorMessages:
    """API error message constants."""
    
    NETWORK_ERROR = "Network connection error. Please check your internet connection."
    TIMEOUT_ERROR = "Request timeout. The server took too long to respond."
    AUTHENTICATION_ERROR = "Authentication failed. Please check your credentials."
    AUTHORIZATION_ERROR = "You do not have permission to access this resource."
    NOT_FOUND_ERROR = "Resource not found."
    VALIDATION_ERROR = "Invalid request data."
    SERVER_ERROR = "Server error. Please try again later."
    UNKNOWN_ERROR = "An unknown error occurred."


# Create default configuration
DEFAULT_CONFIG = APIConfig.from_environment()
