from shiny import App, ui
import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "amazon_sales_dataset.csv"
df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])

# for input_year
min_year = df["order_date"].dt.year.min()
max_year = df["order_date"].dt.year.max()

# for input_category
categories = sorted(df["product_category"].dropna().unique().tolist())
default_category = categories[0]

# for input_region
regions = sorted(df["customer_region"].dropna().unique().tolist())

app_ui = ui.page_fluid(
    ui.panel_title("Amazon Sales Dashboard"),
    ui.layout_sidebar(
        ui.sidebar(

            ui.input_slider(
                id="input_year",
                label="Select Year Range",
                min=min_year, 
                max=max_year, 
                value=(min_year, max_year),
                step=1,
                sep="", 
            ),

            ui.input_selectize(
                id="input_month",
                label="Select Months",
                choices={
                    1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 
                    5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 
                    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
                },
                multiple=True,
                selected=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            ),

            ui.input_selectize(
                id="input_category",
                label="Product Category (Max 3)",
                choices=categories,
                selected=default_category,
                multiple=True,
                options={"maxItems": 3},
            ),

            ui.input_switch(
                id="input_aggregate",
                label="Aggregate Category Trend",
                value=False,
            ),

            ui.input_checkbox_group(
                id="input_region",
                label="Region",
                choices=regions,
                selected=regions,
            ),
            
            ui.input_radio_buttons(
                id="input_metric",
                label="Metric",
                choices={
                    "total_revenue": "Revenue",
                    "quantity_sold": "Quantity Sold",
                },
                selected="total_revenue",
            ),

            ui.input_switch(
                id="input_season",
                label="Show Seasonality Comparison",
                value=False,
            ),
            width=300,
        ),


        # 1. KPI Section
        ui.layout_columns(
            ui.value_box(
                title="Total Revenue",
                value=ui.output_text("valuebox_revenue"),
                theme="primary",
            ),
            ui.value_box(
                title="Total Orders",
                value=ui.output_text("valuebox_orders"),
                theme="bg-info",
            ),
            col_widths=(6, 6),
            gap="20px",
        ),
        
        # 2. Middle Row
        ui.layout_columns(
            ui.card(
                ui.card_header("Trend Chart"),
                ui.output_plot("plot_trend"),
            ),
            ui.card(
                ui.card_header("Sales by Region"),
                ui.output_plot("plot_map"),
            ),
            col_widths=(6, 6),
        ),

        # 3. Bottom Row
        ui.layout_columns(
            ui.panel_conditional(
                "input.input_season", 
                ui.card(
                    ui.card_header("Average Sales by Season"),
                    ui.output_plot("plot_season"),
                ),
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