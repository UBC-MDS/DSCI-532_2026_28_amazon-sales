from shiny import App, ui
import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "amazon_sales_dataset.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])

app_ui = ui.page_fluid(
    ui.panel_title("Amazon Sales Dashboard"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_slider(
                id="time_slider",
                label="Time Slider",
                min=df["order_date"].min(), max=df["order_date"].max(), 
                value=(df["order_date"].min(), df["order_date"].max()),
            ),

            ui.input_selectize(
                id="category",
                label="Product Category",
                choices=sorted(df["product_category"].dropna().unique()),
                multiple=True,
                options={"maxItems": 3},
            ),

            ui.input_selectize(
                id="region",
                label="Region",
                choices=sorted(df["customer_region"].dropna().unique()),
                multiple=True,
            ),

            ui.input_radio_buttons(
                id="metric",
                label="Metric",
                choices={
                    "total_revenue": "Revenue",
                    "quantity_sold": "Quantity Sold",
                    "avg_order_value": "Avg Order Value",
                },
                selected="total_revenue",
            ),

            ui.input_checkbox(
                id="rolling",
                label="Apply 3-Month Rolling Average",
                value=True,
            ),
            width=300,
        ),

        # KPI Section
        ui.card(
            ui.card_header("KPI SECTION"),

            ui.layout_columns(
                ui.card(
                    ui.card_header("Total Revenue"),
                    ui.output_text("kpi_revenue"),
                    ui.output_plot("kpi_revenue_sparkline", height="30px"),
                ),
                ui.card(
                    ui.card_header("Total Orders"),
                    ui.output_text("kpi_orders"),
                    ui.output_plot("kpi_orders_sparkline", height="30px"),
                ),
                ui.card(
                    ui.card_header("Avg Order Value"),
                    ui.output_text("kpi_aov"),
                    ui.output_plot("kpi_aov_sparkline", height="30px"),
                ),
                col_widths=(4, 4, 4),
                gap="40px",
            ),
        ),
        


        # Trend chart + Sales by Region chart
        ui.layout_columns(
            ui.card(
                ui.card_header("Trend Chart"),
                ui.output_plot("trend_chart"),
            ),
            ui.card(
                ui.card_header("Sales by Region"),
                ui.output_plot("sales_by_region"),
            ),
            col_widths=(6, 6),
        ),

        # Average Sales by Season + Revenue by Payment Method
        ui.layout_columns(
            ui.card(
                ui.card_header("Average Sales by Season"),
                ui.output_plot("season_sales_bar"),
            ),
            ui.card(
                ui.card_header("Revenue by Payment Method"),
                ui.output_plot("payment_method_bar"),
            ),
            col_widths=(6, 6),
        ),
    ),
)


def server(input, output, session):
    pass


app = App(app_ui, server)