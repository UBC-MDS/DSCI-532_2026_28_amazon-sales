import pandas as pd
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from app import filter_dashboard_data


def make_test_df():
    return pd.DataFrame(
        {
            "order_date": pd.to_datetime(
                [
                    "2022-01-15",
                    "2022-02-20",
                    "2023-01-10",
                    "2023-03-05",
                ]
            ),
            "product_category": [
                "Electronics",
                "Beauty",
                "Electronics",
                "Fashion",
            ],
            "customer_region": [
                "Asia",
                "Europe",
                "Asia",
                "North America",
            ],
            "order_id": [1, 2, 3, 4],
            "total_revenue": [100, 200, 300, 400],
        }
    )


def test_filter_dashboard_data_returns_expected_rows():
    """filter_dashboard_data returns rows matching all selected filters."""
    df = make_test_df()

    result = filter_dashboard_data(
        df=df,
        years=[2023],
        months=[1],
        categories=["Electronics"],
        regions=["Asia"],
    )

    assert len(result) == 1
    assert result.iloc[0]["order_id"] == 3
    assert result.iloc[0]["total_revenue"] == 300


def test_filter_dashboard_data_returns_empty_dataframe_when_filter_is_empty():
    """filter_dashboard_data returns an empty dataframe when a required filter is empty."""
    df = make_test_df()

    result = filter_dashboard_data(
        df=df,
        years=[],
        months=[1, 2, 3],
        categories=["Electronics"],
        regions=["Asia"],
    )

    assert result.empty