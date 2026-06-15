"""
Mock API Client for AI Supply Chain Frontend
Provides mock implementations of API endpoints for development and testing.

UI Integration Features:
- Direct upload and analysis of CSV data
- Real-time KPI calculations
- Demand forecasting with multiple methods
- Supplier performance analytics
- Inventory management
- Chat-based AI assistance
- Report generation
"""

import time
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import json
import logging

# Setup logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    
    def __bool__(self):
        """Allow APIResponse to be used in boolean context."""
        return self.success


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

    # =========================================================================
    # UI Integration Methods
    # =========================================================================

    def validate_upload_data(self, data: pd.DataFrame) -> APIResponse:
        """
        Validate uploaded data for quality and compatibility.
        
        Args:
            data: DataFrame to validate
            
        Returns:
            APIResponse with validation results
        """
        self._simulate_network_delay()
        
        try:
            validation_results = {
                "is_valid": True,
                "total_rows": len(data),
                "total_columns": len(data.columns),
                "column_names": data.columns.tolist(),
                "data_types": data.dtypes.astype(str).to_dict(),
                "numeric_columns": data.select_dtypes(include=[np.number]).columns.tolist(),
                "categorical_columns": data.select_dtypes(include=["object"]).columns.tolist(),
                "missing_values": data.isnull().sum().to_dict(),
                "missing_percentage": (data.isnull().sum() / len(data) * 100).to_dict(),
                "duplicate_rows": len(data) - len(data.drop_duplicates()),
                "memory_usage_mb": round(data.memory_usage(deep=True).sum() / (1024 * 1024), 2),
                "warnings": self._generate_validation_warnings(data),
                "timestamp": datetime.now().isoformat()
            }
            
            return APIResponse(
                success=True,
                data=validation_results,
                message="Data validation completed successfully"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Data validation failed"
            )

    def _generate_validation_warnings(self, data: pd.DataFrame) -> List[str]:
        """Generate data quality warnings."""
        warnings = []
        
        # Check for excessive missing values
        missing_pct = (data.isnull().sum() / len(data) * 100).max()
        if missing_pct > 20:
            warnings.append(f"High missing values detected: {missing_pct:.1f}%")
        
        # Check for duplicate rows
        dup_count = len(data) - len(data.drop_duplicates())
        if dup_count > 0:
            warnings.append(f"Found {dup_count} duplicate rows")
        
        # Check for potential outliers in numeric columns
        numeric_data = data.select_dtypes(include=[np.number])
        for col in numeric_data.columns:
            Q1 = numeric_data[col].quantile(0.25)
            Q3 = numeric_data[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((numeric_data[col] < (Q1 - 1.5 * IQR)) | 
                       (numeric_data[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > 0:
                warnings.append(f"Column '{col}': {outliers} potential outliers detected")
        
        return warnings

    def get_data_insights(self, data: pd.DataFrame) -> APIResponse:
        """
        Generate automatic insights from uploaded data.
        
        Args:
            data: DataFrame to analyze
            
        Returns:
            APIResponse with insights
        """
        self._simulate_network_delay()
        
        try:
            numeric_data = data.select_dtypes(include=[np.number])
            
            insights = {
                "summary_stats": {
                    "rows": len(data),
                    "columns": len(data.columns),
                    "memory_mb": round(data.memory_usage(deep=True).sum() / (1024 * 1024), 2)
                },
                "numeric_summary": {
                    "count": len(numeric_data.columns),
                    "mean": numeric_data.mean().to_dict(),
                    "median": numeric_data.median().to_dict(),
                    "std": numeric_data.std().to_dict(),
                    "min": numeric_data.min().to_dict(),
                    "max": numeric_data.max().to_dict()
                },
                "categorical_summary": {
                    col: data[col].nunique() 
                    for col in data.select_dtypes(include=["object"]).columns
                },
                "data_quality": {
                    "completeness": round((1 - data.isnull().sum().sum() / (len(data) * len(data.columns))) * 100, 1),
                    "duplicates": len(data) - len(data.drop_duplicates()),
                    "unique_ratio": round(len(data.drop_duplicates()) / len(data) * 100, 1)
                },
                "key_findings": self._extract_key_findings(data),
                "generated_at": datetime.now().isoformat()
            }
            
            return APIResponse(
                success=True,
                data=insights,
                message="Insights generated successfully"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Insight generation failed"
            )

    def _extract_key_findings(self, data: pd.DataFrame) -> List[str]:
        """Extract key findings from data."""
        findings = []
        numeric_data = data.select_dtypes(include=[np.number])
        
        if not numeric_data.empty:
            # Find columns with high variance
            cv = (numeric_data.std() / numeric_data.mean()).abs()
            high_var_cols = cv[cv > 1].index.tolist()
            if high_var_cols:
                findings.append(f"High variability in: {', '.join(high_var_cols[:2])}")
            
            # Identify correlations
            corr_matrix = numeric_data.corr()
            strong_corrs = []
            for i in range(len(corr_matrix.columns)):
                for j in range(i+1, len(corr_matrix.columns)):
                    if abs(corr_matrix.iloc[i, j]) > 0.7:
                        strong_corrs.append(
                            f"{corr_matrix.columns[i]} ↔ {corr_matrix.columns[j]}: {corr_matrix.iloc[i, j]:.2f}"
                        )
            if strong_corrs:
                findings.extend(strong_corrs[:2])
        
        if len(findings) == 0:
            findings.append("Data appears consistent with normal patterns")
        
        return findings

    def process_data_for_analysis(self, data: pd.DataFrame, operations: Optional[Dict] = None) -> APIResponse:
        """
        Process data with specified transformations for analysis.
        
        Args:
            data: DataFrame to process
            operations: Dict of operations to apply {'drop_duplicates': True, 'fill_missing': 'mean', etc}
            
        Returns:
            APIResponse with processed data info
        """
        self._simulate_network_delay()
        
        try:
            processed_data = data.copy()
            operations = operations or {}
            applied_operations = []
            
            # Drop duplicates
            if operations.get('drop_duplicates', False):
                before = len(processed_data)
                processed_data = processed_data.drop_duplicates()
                removed = before - len(processed_data)
                applied_operations.append(f"Removed {removed} duplicate rows")
            
            # Fill missing values
            fill_strategy = operations.get('fill_missing')
            if fill_strategy:
                for col in processed_data.select_dtypes(include=[np.number]).columns:
                    if processed_data[col].isnull().any():
                        if fill_strategy == 'mean':
                            processed_data[col].fillna(processed_data[col].mean(), inplace=True)
                        elif fill_strategy == 'median':
                            processed_data[col].fillna(processed_data[col].median(), inplace=True)
                        elif fill_strategy == 'forward':
                            processed_data[col].fillna(method='ffill', inplace=True)
                applied_operations.append(f"Filled missing values using {fill_strategy}")
            
            # Normalize numeric columns
            if operations.get('normalize', False):
                numeric_cols = processed_data.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    min_val = processed_data[col].min()
                    max_val = processed_data[col].max()
                    if max_val != min_val:
                        processed_data[col] = (processed_data[col] - min_val) / (max_val - min_val)
                applied_operations.append("Normalized numeric columns")
            
            result = {
                "original_rows": len(data),
                "processed_rows": len(processed_data),
                "original_columns": len(data.columns),
                "processed_columns": len(processed_data.columns),
                "applied_operations": applied_operations,
                "data_summary": {
                    "rows": len(processed_data),
                    "columns": len(processed_data.columns),
                    "memory_mb": round(processed_data.memory_usage(deep=True).sum() / (1024 * 1024), 2)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return APIResponse(
                success=True,
                data=result,
                message="Data processed successfully"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Data processing failed"
            )

    def get_column_statistics(self, data: pd.DataFrame, column: str) -> APIResponse:
        """
        Get detailed statistics for a specific column.
        
        Args:
            data: DataFrame containing the column
            column: Column name
            
        Returns:
            APIResponse with column statistics
        """
        self._simulate_network_delay()
        
        try:
            if column not in data.columns:
                return APIResponse(
                    success=False,
                    error=f"Column '{column}' not found",
                    message="Column not found"
                )
            
            col_data = data[column]
            is_numeric = pd.api.types.is_numeric_dtype(col_data)
            
            stats = {
                "column_name": column,
                "dtype": str(col_data.dtype),
                "non_null_count": col_data.notna().sum(),
                "null_count": col_data.isnull().sum(),
                "unique_values": col_data.nunique()
            }
            
            if is_numeric:
                stats.update({
                    "mean": float(col_data.mean()),
                    "median": float(col_data.median()),
                    "mode": float(col_data.mode()[0]) if len(col_data.mode()) > 0 else None,
                    "std": float(col_data.std()),
                    "variance": float(col_data.var()),
                    "min": float(col_data.min()),
                    "25%": float(col_data.quantile(0.25)),
                    "50%": float(col_data.quantile(0.50)),
                    "75%": float(col_data.quantile(0.75)),
                    "max": float(col_data.max()),
                    "range": float(col_data.max() - col_data.min()),
                    "iqr": float(col_data.quantile(0.75) - col_data.quantile(0.25))
                })
            else:
                stats.update({
                    "top_values": col_data.value_counts().head(5).to_dict(),
                    "sample_values": col_data.unique()[:10].tolist()
                })
            
            return APIResponse(
                success=True,
                data=stats,
                message="Column statistics retrieved"
            )
        except Exception as e:
            return APIResponse(
                success=False,
                error=str(e),
                message="Failed to retrieve column statistics"
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
        logger.info("MockAPIClient initialized")
    return _client


def reset_api_client():
    """Reset the API client singleton."""
    global _client
    _client = None
    logger.info("MockAPIClient reset")


# ============================================================================
# Convenience functions for UI components
# ============================================================================

def upload_and_analyze_csv(filename: str, data: pd.DataFrame) -> Tuple[APIResponse, APIResponse, APIResponse]:
    """
    Complete workflow for uploading and analyzing CSV data.
    
    Args:
        filename: Name of the file
        data: DataFrame with the data
        
    Returns:
        Tuple of (upload_response, validation_response, insights_response)
    """
    client = get_api_client()
    
    logger.info(f"Starting upload and analysis workflow for {filename}")
    
    # Step 1: Upload
    upload_resp = client.upload_data(filename, data)
    if not upload_resp.success:
        return upload_resp, None, None
    
    # Step 2: Validate
    validation_resp = client.validate_upload_data(data)
    if not validation_resp.success:
        return upload_resp, validation_resp, None
    
    # Step 3: Get insights
    insights_resp = client.get_data_insights(data)
    
    logger.info(f"Upload and analysis workflow completed for {filename}")
    
    return upload_resp, validation_resp, insights_resp


def generate_complete_forecast(data: pd.DataFrame, periods: int = 7) -> APIResponse:
    """
    Generate forecast with data validation.
    
    Args:
        data: DataFrame with historical data
        periods: Number of periods to forecast
        
    Returns:
        APIResponse with forecast data
    """
    client = get_api_client()
    
    logger.info(f"Generating forecast for {periods} periods")
    
    # Get numeric columns
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    if not numeric_cols:
        return APIResponse(
            success=False,
            error="No numeric columns found",
            message="Forecast requires numeric data"
        )
    
    # Use first numeric column
    data_points = data[numeric_cols[0]].dropna().values.tolist()
    
    # Generate forecast
    forecast_resp = client.generate_forecast(
        data_points=data_points,
        periods=periods,
        method="linear"
    )
    
    logger.info(f"Forecast generated successfully")
    
    return forecast_resp


def analyze_data_quality(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Quick analysis of data quality.
    
    Args:
        data: DataFrame to analyze
        
    Returns:
        Dictionary with quality metrics
    """
    client = get_api_client()
    
    validation = client.validate_upload_data(data)
    if validation.success:
        return validation.data
    return {}


def get_kpi_summary(data: pd.DataFrame) -> Dict[str, Any]:
    """
    Get quick KPI summary from data.
    
    Args:
        data: DataFrame with data
        
    Returns:
        Dictionary with KPI values
    """
    client = get_api_client()
    
    kpi_resp = client.calculate_kpis(data)
    if kpi_resp.success:
        return kpi_resp.data
    return {}


# ============================================================================
# Configuration and factory functions
# ============================================================================

def create_api_client(mock_mode: bool = True, simulate_delay: bool = True) -> MockAPIClient:
    """
    Create a new API client instance.
    
    Args:
        mock_mode: Whether to use mock mode (always True for MockAPIClient)
        simulate_delay: Whether to simulate network delays
        
    Returns:
        MockAPIClient instance
    """
    logger.info(f"Creating new MockAPIClient (simulate_delay={simulate_delay})")
    return MockAPIClient(simulate_delay=simulate_delay)


def get_available_endpoints() -> List[str]:
    """
    Get list of available API endpoints.
    
    Returns:
        List of endpoint names
    """
    client = get_api_client()
    health = client.health_check()
    if health.success:
        return health.data.get("endpoints", [])
    return []


def send_query(query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Send a chat query through the API client.

    Args:
        query: User's message
        session_id: Optional session ID

    Returns:
        Response payload normalized for UI integration.
    """
    client = get_api_client()
    response = client.send_chat_message(message=query, session_id=session_id)

    if not response.success:
        return {
            "success": False,
            "session_id": session_id,
            "query": query,
            "response": "",
            "error": response.error or response.message or "Failed to get chat response",
            "source": "api_client",
            "timestamp": datetime.now().isoformat(),
        }

    payload = response.data if isinstance(response.data, dict) else {}
    return {
        "success": True,
        "session_id": payload.get("session_id", session_id),
        "query": query,
        "response": (
            payload.get("response")
            or payload.get("message")
            or payload.get("reply")
            or payload.get("answer")
            or ""
        ),
        "raw": payload,
        "source": "api_client",
        "timestamp": payload.get("timestamp", datetime.now().isoformat()),
    }


def get_forecast(
    data_points: Optional[List[float]] = None,
    periods: int = 7,
    metric: str = "demand",
    method: str = "linear",
) -> Dict[str, Any]:
    """
    Get forecast data through the API client.

    Args:
        data_points: Historical values for forecasting
        periods: Number of forecast periods
        metric: Metric name for forecast labeling
        method: Forecast method (linear, moving_average, exponential)

    Returns:
        Forecast payload normalized for UI integration.
    """
    safe_periods = max(1, int(periods))
    client = get_api_client()

    if data_points is None:
        data_points = [100.0, 108.0, 112.0, 119.0, 123.0, 130.0, 136.0]

    safe_method = (method or "linear").lower()
    if safe_method not in {"linear", "moving_average", "exponential"}:
        safe_method = "linear"

    response = client.generate_forecast(
        data_points=data_points,
        periods=safe_periods,
        method=safe_method,
    )

    if not response.success:
        return {
            "success": False,
            "metric": metric,
            "periods": safe_periods,
            "forecast_values": [],
            "error": response.error or response.message or "Failed to generate forecast",
            "source": "api_client",
            "timestamp": datetime.now().isoformat(),
        }

    payload = response.data if isinstance(response.data, dict) else {}
    return {
        "success": True,
        "metric": metric,
        "periods": payload.get("periods", safe_periods),
        "forecast_values": payload.get("forecast_values", []),
        "confidence_interval": payload.get("confidence_interval"),
        "method": payload.get("method", safe_method),
        "raw": payload,
        "source": "api_client",
        "timestamp": payload.get("generated_at", datetime.now().isoformat()),
    }
