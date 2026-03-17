import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app import get_metric_info

def test_get_metric_info_returns_revenue_settings():
    """get_metric_info returns the correct settings for revenue metric."""
    result = get_metric_info("total_revenue")

    assert result["id"] == "total_revenue"
    assert result["label"] == "Revenue ($)"
    assert result["exact_format"] == "$,.0f"
    assert result["short"] == "Revenue"
    assert result["agg_func"] == "sum"


def test_get_metric_info_returns_order_settings():
    """get_metric_info returns the correct settings for order metric."""
    result = get_metric_info("order_id")

    assert result["id"] == "order_id"
    assert result["label"] == "Total Orders"
    assert result["exact_format"] == ",.0f"
    assert result["short"] == "Orders"
    assert result["agg_func"] == "nunique"

def test_get_metric_info_contains_required_keys():
    """get_metric_info returns dictionary with required keys."""
    result = get_metric_info("total_revenue")

    expected_keys = {"id", "label", "exact_format", "short", "agg_func"}

    assert expected_keys.issubset(result.keys())


def test_get_metric_info_unknown_metric_defaults_to_order_logic():
    """get_metric_info treats unknown metrics as order-based metric."""
    result = get_metric_info("unknown_metric")

    assert result["label"] == "Total Orders"
    assert result["agg_func"] == "nunique"