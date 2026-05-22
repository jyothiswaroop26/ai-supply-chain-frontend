"""
Mock API Client for AI Supply Chain Frontend
Provides mock implementations of API endpoints for development and testing.
"""

import time
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import json


@dataclass
class APIResponse:
    """Standard API response wrapper."""
    success: bool
    data: Any = None
    message: str = ""
    error: Optional[str] = None
    timestamp: str = ""

    def to_dict(self):
        """Convert response to dictionary."""
        self.timestamp = datetime.now().isoformat()
        return asdict(self)


class MockAPIClient:
    """Mock API client for supply chain operations."""

    def __init__(self, base_url: str = "http://localhost:8000", simulate_delay: bool = True):
        """
        Initialize the mock API client.
        
        Args:
            base_url: Base URL for API (unused in mock, kept for compatibility)
            simulate_delay: Whether to simulate network delays
        """
        self.base_url = base_url
        self.simulate_delay = simulate_delay
        self._delay_range = (0.2, 0.8)  # seconds

    def _simulate_network_delay(self):
        """Simulate network latency."""
        if self.simulate_delay:
            delay = random.uniform(*self._delay_range)
            time.sleep(delay)

    # =========================================================================
    # Data Management Endpoints
    # =========================================================================

    def upload_data(self, filename: str, data: pd.DataFrame) -> APIResponse:
        """
        Mock endpoint to upload supply chain data.
        
        Args:
            filename: Name of the uploaded file
            data: DataFrame containing the data
            
        Returns:
            APIResponse with upload confirmation and data summary
        """
        self._simulate_network_delay()
        
        try:
            summary = {
                "filename": filename,
                "rows": len(data),
                "columns": len(data.columns),
                "column_names": data.columns.tolist(),
                "data_types": data.dtypes.astype(str).to_dict(),
                "uploaded_at": datetime.now().isoformat(),
                "file_size_kb": len(data.to_json()) / 1024,
            }
            
            return APIResponse(
                success=True,
                data=summary,
                message=f"File '{filename}' uploaded successfully"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Failed to upload data"
            )

    def fetch_datasets(self) -> APIResponse:
        """
        Mock endpoint to fetch available datasets.
        
        Returns:
            APIResponse with list of available datasets
        """
        self._simulate_network_delay()
        
        datasets = [
            {
                "id": 1,
                "name": "Q1 2024 Supply Data",
                "rows": 1500,
                "columns": 12,
                "uploaded_date": "2024-01-15",
                "status": "active"
            },
            {
                "id": 2,
                "name": "Supplier Performance Metrics",
                "rows": 340,
                "columns": 8,
                "uploaded_date": "2024-02-10",
                "status": "active"
            },
            {
                "id": 3,
                "name": "Q4 2023 Historical Data",
                "rows": 2100,
                "columns": 15,
                "uploaded_date": "2024-01-05",
                "status": "archived"
            },
        ]
        
        return APIResponse(
            success=True,
            data=datasets,
            message="Datasets retrieved successfully"
        )

    # =========================================================================
    # Forecasting Endpoints
    # =========================================================================

    def generate_forecast(
        self,
        data_points: List[float],
        periods: int = 7,
        method: str = "linear"
    ) -> APIResponse:
        """
        Mock endpoint to generate demand forecasts.
        
        Args:
            data_points: Historical data values
            periods: Number of periods to forecast
            method: Forecasting method ('linear', 'exponential', 'moving_average')
            
        Returns:
            APIResponse with forecast values and confidence intervals
        """
        self._simulate_network_delay()
        
        try:
            if len(data_points) < 2:
                return APIResponse(
                    success=False,
                    error="Insufficient data points",
                    message="At least 2 data points required"
                )

            # Simple forecast generation based on method
            if method == "linear":
                forecast = self._linear_forecast(data_points, periods)
            elif method == "exponential":
                forecast = self._exponential_forecast(data_points, periods)
            else:
                forecast = self._moving_average_forecast(data_points, periods)

            result = {
                "forecast_values": forecast,
                "periods": periods,
                "method": method,
                "confidence_interval": self._generate_confidence_interval(forecast),
                "mape": round(random.uniform(5, 15), 2),  # Mock MAPE
                "rmse": round(random.uniform(50, 200), 2),  # Mock RMSE
                "generated_at": datetime.now().isoformat()
            }
            
            return APIResponse(
                success=True,
                data=result,
                message="Forecast generated successfully"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Forecast generation failed"
            )

    def _linear_forecast(self, data: List[float], periods: int) -> List[float]:
        """Generate linear forecast."""
        arr = np.array(data)
        x = np.arange(len(arr))
        slope, intercept = np.polyfit(x, arr, 1)
        
        last_x = x[-1]
        forecast = [slope * (last_x + i + 1) + intercept for i in range(periods)]
        return [round(f, 2) for f in forecast]

    def _exponential_forecast(self, data: List[float], periods: int) -> List[float]:
        """Generate exponential smoothing forecast."""
        arr = np.array(data)
        alpha = 0.3
        
        result = [arr[0]]
        for i in range(1, len(arr)):
            result.append(alpha * arr[i] + (1 - alpha) * result[-1])
        
        forecast = [result[-1] for _ in range(periods)]
        return [round(f, 2) for f in forecast]

    def _moving_average_forecast(self, data: List[float], periods: int) -> List[float]:
        """Generate moving average forecast."""
        arr = np.array(data)
        window = min(3, len(arr) // 2)
        ma = np.convolve(arr, np.ones(window) / window, mode='valid')
        
        forecast = [ma[-1] for _ in range(periods)]
        return [round(f, 2) for f in forecast]

    def _generate_confidence_interval(self, forecast: List[float], confidence: float = 0.95) -> Dict:
        """Generate confidence interval for forecast."""
        arr = np.array(forecast)
        std = np.std(arr) * 0.2  # Mock confidence band
        
        return {
            "confidence_level": confidence,
            "upper_bound": [round(v + std, 2) for v in forecast],
            "lower_bound": [round(v - std, 2) for v in forecast]
        }

    # =========================================================================
    # KPI Calculation Endpoints
    # =========================================================================

    def calculate_kpis(self, data: pd.DataFrame) -> APIResponse:
        """
        Mock endpoint to calculate supply chain KPIs.
        
        Args:
            data: DataFrame with supply chain data
            
        Returns:
            APIResponse with calculated KPIs
        """
        self._simulate_network_delay()
        
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            
            if numeric_data.empty:
                return APIResponse(
                    success=False,
                    error="No numeric data found",
                    message="KPI calculation requires numeric columns"
                )

            kpis = {
                "total_records": len(data),
                "avg_value": round(numeric_data.mean().mean(), 2),
                "max_value": round(numeric_data.max().max(), 2),
                "min_value": round(numeric_data.min().min(), 2),
                "total_sum": round(numeric_data.sum().sum(), 2),
                "std_dev": round(numeric_data.std().mean(), 2),
                "data_quality_score": self._calculate_data_quality(data),
                "mean_value": round(numeric_data.mean().mean(), 2),
                "cv_percentage": self._calculate_cv(numeric_data),
                "missing_values_count": int(data.isnull().sum().sum()),
                "complete_records": int((~data.isnull().any(axis=1)).sum()),
                "calculated_at": datetime.now().isoformat()
            }
            
            return APIResponse(
                success=True,
                data=kpis,
                message="KPIs calculated successfully"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="KPI calculation failed"
            )

    def _calculate_data_quality(self, data: pd.DataFrame) -> float:
        """Calculate data quality score (0-100)."""
        total_cells = data.shape[0] * data.shape[1]
        missing_cells = data.isnull().sum().sum()
        quality = 100 * (1 - missing_cells / total_cells) if total_cells > 0 else 0
        return round(quality, 1)

    def _calculate_cv(self, numeric_data: pd.DataFrame) -> float:
        """Calculate coefficient of variation."""
        mean = numeric_data.mean().mean()
        std = numeric_data.std().mean()
        cv = (std / mean * 100) if mean != 0 else 0
        return round(cv, 2)

    # =========================================================================
    # Supplier Management Endpoints
    # =========================================================================

    def fetch_suppliers(self, page: int = 1, limit: int = 10) -> APIResponse:
        """
        Mock endpoint to fetch supplier list.
        
        Args:
            page: Page number for pagination
            limit: Number of suppliers per page
            
        Returns:
            APIResponse with supplier list and metadata
        """
        self._simulate_network_delay()
        
        suppliers = [
            {
                "id": 1,
                "name": "Global Parts Inc.",
                "location": "Shanghai, China",
                "rating": 4.8,
                "lead_time_days": 21,
                "on_time_delivery": 97.5,
                "defect_rate": 0.5,
                "status": "active"
            },
            {
                "id": 2,
                "name": "European Manufacturing Ltd.",
                "location": "Berlin, Germany",
                "rating": 4.6,
                "lead_time_days": 14,
                "on_time_delivery": 95.2,
                "defect_rate": 0.8,
                "status": "active"
            },
            {
                "id": 3,
                "name": "American Supply Co.",
                "location": "Detroit, USA",
                "rating": 4.4,
                "lead_time_days": 7,
                "on_time_delivery": 93.1,
                "defect_rate": 1.2,
                "status": "active"
            },
            {
                "id": 4,
                "name": "Asian Components Ltd.",
                "location": "Bangalore, India",
                "rating": 4.3,
                "lead_time_days": 28,
                "on_time_delivery": 91.0,
                "defect_rate": 1.5,
                "status": "monitoring"
            },
        ]
        
        start = (page - 1) * limit
        end = start + limit
        paginated = suppliers[start:end]
        
        return APIResponse(
            success=True,
            data={
                "suppliers": paginated,
                "total": len(suppliers),
                "page": page,
                "limit": limit,
                "pages": (len(suppliers) + limit - 1) // limit
            },
            message="Suppliers retrieved successfully"
        )

    def get_supplier_details(self, supplier_id: int) -> APIResponse:
        """
        Mock endpoint to fetch detailed supplier information.
        
        Args:
            supplier_id: ID of the supplier
            
        Returns:
            APIResponse with detailed supplier information
        """
        self._simulate_network_delay()
        
        suppliers_db = {
            1: {
                "id": 1,
                "name": "Global Parts Inc.",
                "location": "Shanghai, China",
                "contact_email": "info@globalparts.cn",
                "contact_phone": "+86-21-5888-8888",
                "rating": 4.8,
                "lead_time_days": 21,
                "on_time_delivery": 97.5,
                "defect_rate": 0.5,
                "orders_count": 245,
                "total_spending": 1250000,
                "status": "active",
                "established": "2010",
                "certifications": ["ISO 9001", "ISO 14001"],
                "products": ["Electronic Components", "Mechanical Parts"]
            },
            2: {
                "id": 2,
                "name": "European Manufacturing Ltd.",
                "location": "Berlin, Germany",
                "contact_email": "contact@eurmfg.de",
                "contact_phone": "+49-30-5555-5555",
                "rating": 4.6,
                "lead_time_days": 14,
                "on_time_delivery": 95.2,
                "defect_rate": 0.8,
                "orders_count": 180,
                "total_spending": 980000,
                "status": "active",
                "established": "2008",
                "certifications": ["ISO 9001", "CE Marking"],
                "products": ["Machinery Components", "Precision Parts"]
            },
        }
        
        supplier = suppliers_db.get(supplier_id)
        if supplier:
            return APIResponse(
                success=True,
                data=supplier,
                message="Supplier details retrieved successfully"
            )
        else:
            return APIResponse(
                success=False,
                error=f"Supplier {supplier_id} not found",
                message="Supplier not found"
            )

    # =========================================================================
    # Analytics Endpoints
    # =========================================================================

    def get_supply_chain_analytics(self) -> APIResponse:
        """
        Mock endpoint to get supply chain analytics dashboard data.
        
        Returns:
            APIResponse with analytics metrics and insights
        """
        self._simulate_network_delay()
        
        analytics = {
            "total_orders": 1205,
            "on_time_delivery_rate": 94.7,
            "average_lead_time": 18.5,
            "inventory_turnover": 8.2,
            "order_accuracy": 98.5,
            "supplier_count": 12,
            "active_shipments": 34,
            "pending_orders": 78,
            "cost_per_unit": 127.45,
            "trends": {
                "orders_trend": "up",
                "delivery_trend": "stable",
                "cost_trend": "down"
            },
            "top_products": [
                {"name": "Product A", "units": 450},
                {"name": "Product B", "units": 380},
                {"name": "Product C", "units": 320},
            ],
            "generated_at": datetime.now().isoformat()
        }
        
        return APIResponse(
            success=True,
            data=analytics,
            message="Analytics retrieved successfully"
        )

    def get_inventory_levels(self) -> APIResponse:
        """
        Mock endpoint to get current inventory levels.
        
        Returns:
            APIResponse with inventory information
        """
        self._simulate_network_delay()
        
        inventory = [
            {
                "sku": "SKU-001",
                "product_name": "Component A",
                "quantity": 450,
                "reorder_point": 100,
                "unit_cost": 25.50,
                "warehouse": "Warehouse-1",
                "status": "optimal"
            },
            {
                "sku": "SKU-002",
                "product_name": "Component B",
                "quantity": 85,
                "reorder_point": 100,
                "unit_cost": 45.00,
                "warehouse": "Warehouse-1",
                "status": "low"
            },
            {
                "sku": "SKU-003",
                "product_name": "Assembly C",
                "quantity": 1200,
                "reorder_point": 300,
                "unit_cost": 120.00,
                "warehouse": "Warehouse-2",
                "status": "optimal"
            },
            {
                "sku": "SKU-004",
                "product_name": "Part D",
                "quantity": 0,
                "reorder_point": 50,
                "unit_cost": 15.75,
                "warehouse": "Warehouse-1",
                "status": "out_of_stock"
            },
        ]
        
        return APIResponse(
            success=True,
            data=inventory,
            message="Inventory levels retrieved successfully"
        )

    # =========================================================================
    # Chat/AI Endpoints
    # =========================================================================

    def send_chat_message(self, message: str, session_id: Optional[str] = None) -> APIResponse:
        """
        Mock endpoint for AI chat interactions.
        
        Args:
            message: User message
            session_id: Optional chat session ID
            
        Returns:
            APIResponse with AI response
        """
        self._simulate_network_delay()
        
        # Simple mock responses based on keywords
        responses = {
            "forecast": "Based on your historical data, I predict a 15% increase in demand for Q2. This is influenced by seasonal trends and market indicators.",
            "inventory": "Your current inventory turnover ratio is 8.2x annually. SKU-002 (Component B) is approaching reorder point. Consider placing an order with Global Parts Inc.",
            "supplier": "Global Parts Inc. has the highest performance rating (4.8/5) with 97.5% on-time delivery. However, they have a 21-day lead time.",
            "kpi": "Key metrics show strong performance: 94.7% on-time delivery rate and 98.5% order accuracy. The cost per unit has decreased by 5% this quarter.",
            "default": "I'm here to help with your supply chain analytics. You can ask me about forecasts, inventory levels, supplier performance, or KPIs.",
        }
        
        # Match keywords to responses
        message_lower = message.lower()
        response = responses["default"]
        
        for keyword, text in responses.items():
            if keyword in message_lower and keyword != "default":
                response = text
                break
        
        result = {
            "session_id": session_id or self._generate_session_id(),
            "response": response,
            "confidence": round(random.uniform(0.75, 0.99), 2),
            "timestamp": datetime.now().isoformat(),
            "follow_up_suggestions": [
                "Show me the detailed forecast",
                "What are the top suppliers?",
                "Generate a KPI report"
            ]
        }
        
        return APIResponse(
            success=True,
            data=result,
            message="Chat response generated successfully"
        )

    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"

    # =========================================================================
    # Report Generation Endpoints
    # =========================================================================

    def generate_report(self, report_type: str, data: pd.DataFrame) -> APIResponse:
        """
        Mock endpoint to generate reports.
        
        Args:
            report_type: Type of report ('summary', 'detailed', 'executive')
            data: DataFrame with report data
            
        Returns:
            APIResponse with report information
        """
        self._simulate_network_delay()
        
        report = {
            "report_id": f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": report_type,
            "title": f"{report_type.capitalize()} Supply Chain Report",
            "generated_at": datetime.now().isoformat(),
            "rows_analyzed": len(data),
            "columns_analyzed": len(data.columns),
            "file_size_kb": round(len(data.to_json()) / 1024, 2),
            "export_formats": ["PDF", "Excel", "CSV"],
            "sections": [
                "Executive Summary",
                "Key Metrics",
                "Trend Analysis",
                "Recommendations"
            ]
        }
        
        return APIResponse(
            success=True,
            data=report,
            message=f"{report_type} report generated successfully"
        )

    def download_report(self, report_id: str) -> APIResponse:
        """
        Mock endpoint to download a generated report.
        
        Args:
            report_id: ID of the report to download
            
        Returns:
            APIResponse with download link and metadata
        """
        self._simulate_network_delay()
        
        return APIResponse(
            success=True,
            data={
                "report_id": report_id,
                "download_url": f"/api/reports/{report_id}/download",
                "filename": f"{report_id}.pdf",
                "file_size_kb": round(random.uniform(100, 500), 2),
                "expires_in_hours": 24,
            },
            message="Report download link generated"
        )

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def health_check(self) -> APIResponse:
        """
        Mock endpoint to check API health status.
        
        Returns:
            APIResponse with health status
        """
        return APIResponse(
            success=True,
            data={
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "endpoints": [
                    "upload_data",
                    "fetch_datasets",
                    "generate_forecast",
                    "calculate_kpis",
                    "fetch_suppliers",
                    "get_supply_chain_analytics",
                    "send_chat_message",
                    "generate_report"
                ]
            },
            message="API is operational"
        )


# ============================================================================
# Singleton instance for easy module-level access
# ============================================================================

_client = None


def get_api_client(simulate_delay: bool = True) -> MockAPIClient:
    """
    Get or create the mock API client singleton.
    
    Args:
        simulate_delay: Whether to simulate network delays
        
    Returns:
        MockAPIClient instance
    """
    global _client
    if _client is None:
        _client = MockAPIClient(simulate_delay=simulate_delay)
    return _client


def reset_api_client():
    """Reset the API client singleton."""
    global _client
    _client = None
