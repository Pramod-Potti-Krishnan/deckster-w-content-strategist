"""
CSV Utilities for Analytics Data
=================================

Provides CSV conversion utilities for chart data.
Converts DataPoint lists to CSV format for export and display.

Author: Analytics Agent System
Date: 2024
Version: 1.0
"""

import csv
import io
from typing import List, Dict, Any, Optional
from .models import DataPoint, ChartType


def data_points_to_csv(
    data_points: List[DataPoint],
    chart_type: Optional[ChartType] = None,
    include_headers: bool = True
) -> str:
    """
    Convert a list of DataPoints to CSV format.
    
    Args:
        data_points: List of data points to convert
        chart_type: Optional chart type for specialized formatting
        include_headers: Whether to include CSV headers
        
    Returns:
        CSV formatted string
    """
    if not data_points:
        return ""
    
    # Create string buffer for CSV
    output = io.StringIO()
    
    # Determine headers based on chart type
    headers = _get_headers_for_chart_type(chart_type, data_points)
    
    # Create CSV writer
    writer = csv.writer(output)
    
    # Write headers if requested
    if include_headers:
        writer.writerow(headers)
    
    # Write data rows
    for dp in data_points:
        row = _format_data_point_row(dp, chart_type)
        writer.writerow(row)
    
    # Get CSV string
    csv_string = output.getvalue()
    output.close()
    
    return csv_string


def _get_headers_for_chart_type(
    chart_type: Optional[ChartType],
    data_points: List[DataPoint]
) -> List[str]:
    """
    Get appropriate CSV headers based on chart type.
    
    Args:
        chart_type: Chart type
        data_points: Data points to analyze
        
    Returns:
        List of header names
    """
    # Check if we have categories
    has_categories = any(dp.category for dp in data_points)
    
    if chart_type in [ChartType.SCATTER, ChartType.BUBBLE]:
        return ["X", "Y", "Size"] if chart_type == ChartType.BUBBLE else ["X", "Y"]
    elif chart_type == ChartType.HEATMAP:
        return ["Row", "Column", "Value"]
    elif chart_type == ChartType.WATERFALL:
        return ["Stage", "Value", "Cumulative"]
    elif has_categories:
        return ["Category", "Label", "Value"]
    else:
        return ["Label", "Value"]


def _format_data_point_row(
    data_point: DataPoint,
    chart_type: Optional[ChartType]
) -> List[Any]:
    """
    Format a data point as a CSV row.
    
    Args:
        data_point: Data point to format
        chart_type: Chart type for specialized formatting
        
    Returns:
        List of values for CSV row
    """
    # Basic row with label and value
    row = [data_point.label, data_point.value]
    
    # Add category if present
    if data_point.category:
        row = [data_point.category] + row
    
    # Add any metadata values if needed for specific chart types
    if chart_type == ChartType.WATERFALL and data_point.metadata:
        cumulative = data_point.metadata.get("cumulative", "")
        row.append(cumulative)
    
    return row


def dict_list_to_csv(
    data: List[Dict[str, Any]],
    headers: Optional[List[str]] = None
) -> str:
    """
    Convert a list of dictionaries to CSV format.
    
    Args:
        data: List of dictionaries
        headers: Optional list of headers (uses dict keys if not provided)
        
    Returns:
        CSV formatted string
    """
    if not data:
        return ""
    
    # Use provided headers or extract from first item
    if not headers:
        headers = list(data[0].keys())
    
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    
    writer.writeheader()
    writer.writerows(data)
    
    csv_string = output.getvalue()
    output.close()
    
    return csv_string


def format_for_display(csv_string: str, max_rows: int = 10) -> str:
    """
    Format CSV for display with truncation if needed.
    
    Args:
        csv_string: CSV string to format
        max_rows: Maximum number of rows to display
        
    Returns:
        Formatted CSV string for display
    """
    lines = csv_string.strip().split('\n')
    
    if len(lines) <= max_rows + 1:  # +1 for header
        return csv_string
    
    # Keep header and first max_rows of data
    truncated = lines[:max_rows + 1]
    truncated.append(f"... ({len(lines) - max_rows - 1} more rows)")
    
    return '\n'.join(truncated)