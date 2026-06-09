"""
HTTP API Client - Production-ready API integration
Provides HTTP/REST API client for connecting to real backends.
"""

import requests
import json
import time
from typing import Dict, Optional, Any, List
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from dataclasses import asdict
import logging

from .config import APIConfig, APIEndpoints, APIErrorCodes, APIErrorMessages
from .api_client import APIResponse

logger = logging.getLogger(__name__)


class HTTPAPIClient:
    """
    HTTP-based API client for connecting to real backend servers.
    Supports retries, authentication, and error handling.
    """
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        Initialize the HTTP API client.
        
        Args:
            config: API configuration object
        """
        self.config = config or APIConfig()
        self.session = self._create_session()
        self.logger = logging.getLogger(__name__)
        
        if self.config.verbose_logging:
            self.logger.setLevel(logging.DEBUG)
    
    def _create_session(self) -> requests.Session:
        """Create a requests session with retry strategy."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Add authentication headers if configured
        if self.config.use_auth:
            if self.config.api_key:
                session.headers.update({"X-API-Key": self.config.api_key})
            if self.config.auth_token:
                session.headers.update({"Authorization": f"Bearer {self.config.auth_token}"})
        
        # Add standard headers
        session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "AI-Supply-Chain-Frontend/1.0"
        })
        
        return session
    
    def _handle_error(self, response: requests.Response) -> APIResponse:
        """Handle API error responses."""
        try:
            error_data = response.json()
            error_message = error_data.get("message", "Unknown error")
            error_detail = error_data.get("error", error_data.get("detail", ""))
        except json.JSONDecodeError:
            error_message = response.text or "Unknown error"
            error_detail = f"HTTP {response.status_code}"
        
        self.logger.error(f"API Error {response.status_code}: {error_message}")
        
        return APIResponse(
            success=False,
            error=error_detail,
            message=error_message
        )
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> APIResponse:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            endpoint: API endpoint path
            data: Request body data
            params: Query parameters
            **kwargs: Additional request arguments
            
        Returns:
            APIResponse object
        """
        url = f"{self.config.api_url}{endpoint}"
        
        try:
            self.logger.debug(f"{method} {url}")
            
            response = self.session.request(
                method,
                url,
                json=data,
                params=params,
                timeout=self.config.request_timeout,
                **kwargs
            )
            
            # Handle errors
            if response.status_code >= 400:
                return self._handle_error(response)
            
            # Parse response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = {"data": response.text}
            
            return APIResponse(
                success=response.status_code < 400,
                data=response_data.get("data", response_data),
                message=response_data.get("message", "Success")
            )
            
        except requests.Timeout:
            error_msg = APIErrorMessages.TIMEOUT_ERROR
            self.logger.error(error_msg)
            return APIResponse(success=False, error=error_msg, message="Request timeout")
        
        except requests.ConnectionError:
            error_msg = APIErrorMessages.NETWORK_ERROR
            self.logger.error(error_msg)
            return APIResponse(success=False, error=error_msg, message="Connection error")
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.logger.error(error_msg)
            return APIResponse(success=False, error=error_msg, message=APIErrorMessages.UNKNOWN_ERROR)
    
    # =========================================================================
    # Data Management Endpoints
    # =========================================================================
    
    def upload_data(self, filename: str, file_content: bytes) -> APIResponse:
        """Upload a data file to the server."""
        files = {"file": (filename, file_content)}
        
        return self._make_request(
            "POST",
            APIEndpoints.UPLOAD_DATA,
            files=files
        )
    
    def fetch_datasets(self) -> APIResponse:
        """Fetch list of available datasets."""
        return self._make_request("GET", APIEndpoints.FETCH_DATASETS)
    
    def get_dataset(self, dataset_id: str) -> APIResponse:
        """Get a specific dataset."""
        endpoint = APIEndpoints.GET_DATASET.format(dataset_id=dataset_id)
        return self._make_request("GET", endpoint)
    
    def delete_dataset(self, dataset_id: str) -> APIResponse:
        """Delete a dataset."""
        endpoint = APIEndpoints.DELETE_DATASET.format(dataset_id=dataset_id)
        return self._make_request("DELETE", endpoint)
    
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
        payload = {
            "data_points": data_points,
            "periods": periods,
            "method": method
        }
        return self._make_request("POST", APIEndpoints.GENERATE_FORECAST, data=payload)
    
    def get_forecast_models(self) -> APIResponse:
        """Get available forecast models."""
        return self._make_request("GET", APIEndpoints.GET_FORECAST_MODELS)
    
    def validate_forecast(self, forecast_id: str) -> APIResponse:
        """Validate a forecast."""
        return self._make_request("GET", APIEndpoints.VALIDATE_FORECAST, params={"id": forecast_id})
    
    # =========================================================================
    # KPI Calculation Endpoints
    # =========================================================================
    
    def calculate_kpis(self, dataset_id: str, metrics: List[str]) -> APIResponse:
        """Calculate KPIs for a dataset."""
        payload = {
            "dataset_id": dataset_id,
            "metrics": metrics
        }
        return self._make_request("POST", APIEndpoints.CALCULATE_KPIS, data=payload)
    
    def get_kpi_history(self, metric_name: str) -> APIResponse:
        """Get KPI calculation history."""
        return self._make_request("GET", APIEndpoints.GET_KPI_HISTORY, params={"metric": metric_name})
    
    def export_kpis(self, format: str = "csv") -> APIResponse:
        """Export KPIs in specified format."""
        return self._make_request("GET", APIEndpoints.EXPORT_KPIS, params={"format": format})
    
    # =========================================================================
    # Supplier Management Endpoints
    # =========================================================================
    
    def fetch_suppliers(self, page: int = 1, limit: int = 10) -> APIResponse:
        """Fetch list of suppliers."""
        params = {"page": page, "limit": limit}
        return self._make_request("GET", APIEndpoints.FETCH_SUPPLIERS, params=params)
    
    def get_supplier_details(self, supplier_id: int) -> APIResponse:
        """Get detailed supplier information."""
        endpoint = APIEndpoints.GET_SUPPLIER_DETAILS.format(supplier_id=supplier_id)
        return self._make_request("GET", endpoint)
    
    def update_supplier(self, supplier_id: int, data: Dict) -> APIResponse:
        """Update supplier information."""
        endpoint = APIEndpoints.UPDATE_SUPPLIER.format(supplier_id=supplier_id)
        return self._make_request("PUT", endpoint, data=data)
    
    # =========================================================================
    # Analytics Endpoints
    # =========================================================================
    
    def get_analytics(self) -> APIResponse:
        """Get supply chain analytics dashboard data."""
        return self._make_request("GET", APIEndpoints.GET_ANALYTICS)
    
    def get_inventory_levels(self) -> APIResponse:
        """Get current inventory levels."""
        return self._make_request("GET", APIEndpoints.GET_INVENTORY_LEVELS)
    
    def get_supply_chain_metrics(self) -> APIResponse:
        """Get supply chain metrics."""
        return self._make_request("GET", APIEndpoints.GET_SUPPLY_CHAIN_METRICS)
    
    # =========================================================================
    # Chat/AI Endpoints
    # =========================================================================
    
    def send_chat_message(self, message: str, session_id: Optional[str] = None) -> APIResponse:
        """Send a chat message to the AI."""
        payload = {
            "message": message,
            "session_id": session_id
        }
        return self._make_request("POST", APIEndpoints.SEND_CHAT_MESSAGE, data=payload)
    
    def create_chat_session(self) -> APIResponse:
        """Create a new chat session."""
        return self._make_request("POST", APIEndpoints.CREATE_CHAT_SESSION, data={})
    
    def get_chat_history(self, session_id: str) -> APIResponse:
        """Get chat history for a session."""
        return self._make_request("GET", APIEndpoints.GET_CHAT_HISTORY, params={"session_id": session_id})
    
    # =========================================================================
    # Report Generation Endpoints
    # =========================================================================
    
    def generate_report(self, report_type: str, params: Dict) -> APIResponse:
        """Generate a report."""
        payload = {
            "type": report_type,
            **params
        }
        return self._make_request("POST", APIEndpoints.GENERATE_REPORT, data=payload)
    
    def get_report(self, report_id: str) -> APIResponse:
        """Get report details."""
        endpoint = APIEndpoints.GET_REPORT.format(report_id=report_id)
        return self._make_request("GET", endpoint)
    
    def download_report(self, report_id: str) -> APIResponse:
        """Get report download link."""
        endpoint = APIEndpoints.DOWNLOAD_REPORT.format(report_id=report_id)
        return self._make_request("GET", endpoint)
    
    # =========================================================================
    # System Endpoints
    # =========================================================================
    
    def health_check(self) -> APIResponse:
        """Check API health status."""
        return self._make_request("GET", APIEndpoints.HEALTH_CHECK)
    
    def get_api_status(self) -> APIResponse:
        """Get detailed API status."""
        return self._make_request("GET", APIEndpoints.GET_API_STATUS)
    
    def close(self):
        """Close the session."""
        self.session.close()
