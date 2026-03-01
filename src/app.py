from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_widget
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from matplotlib.ticker import FuncFormatter

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

# for plot_map
REGION_MAPPING = {
        "Asia": [
            "China", "India", "Japan", "South Korea", "Vietnam", "Thailand", 
            "Indonesia", "Malaysia", "Philippines", "Singapore", "Taiwan"
        ],
        "Europe": [
            "Germany", "France", "United Kingdom", "Italy", "Spain", "Netherlands", 
            "Belgium", "Switzerland", "Sweden", "Norway", "Poland", "Portugal"
        ],
        "Middle East": [
            "Saudi Arabia", "United Arab Emirates", "Israel", "Turkey", "Qatar", 
            "Kuwait", "Jordan", "Oman", "Lebanon"
        ],
        "North America": [
            "United States", "Canada", "Mexico"
        ]
    }

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
                ui.output_ui("trend_header"),
                ui.output_plot("plot_trend"),
            ),
            ui.card(
                ui.card_header("Selected Regions"),
                output_widget("plot_map"),
            ),
            col_widths=(6, 6),
        ),

        # Average Sales by Season + Revenue by Payment Method
        ui.layout_columns(
            ui.panel_conditional(
                "input.input_season", 
                ui.card(
                    ui.output_ui("season_header"),
                    ui.output_plot("plot_season"),
                ),
            ),
            ui.card(
                ui.output_ui("payment_header"),
                ui.output_plot("payment_method_bar"),
            ),
            col_widths=(6, 6),
        ),
    ),
)


def server(input, output, session):

    def _months_selected():
        
        vals = input.input_month()
        if vals is None:
            return list(range(1, 13))
        return [int(v) for v in vals]

    def _metric_col():
        m = input.input_metric()
        return "total_revenue" if m == "total_revenue" else "quantity_sold"


    @reactive.calc
    def filtered_df():
        d = df.copy()

        y0, y1 = input.input_year()
        d = d[(d["order_date"].dt.year >= int(y0)) & (d["order_date"].dt.year <= int(y1))]

        months = _months_selected()
        d = d[d["order_date"].dt.month.isin(months)]

        cats = input.input_category()
        if cats:
            d = d[d["product_category"].isin(cats)]

        regs = input.input_region()
        if regs:
            d = d[d["customer_region"].isin(regs)]

        return d

    # --- shared KPI calc consumed by multiple outputs ---
    @reactive.calc
    def kpi():
        d = filtered_df()

        total_revenue = float(d["total_revenue"].sum())
        total_orders = int(d["order_id"].nunique())
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0

        return {
            "total_revenue": total_revenue,
            "total_orders": total_orders,
            "avg_order_value": avg_order_value,
        }

    # --- KPI outputs (2 outputs consuming same reactive calc) ---
    @output
    @render.text
    def valuebox_revenue():
        return f"${kpi()['total_revenue']:,.0f}"

    @output
    @render.text
    def valuebox_orders():
        return f"{kpi()['total_orders']:,}"

    # --- Trend chart (depends on filtered_df + metric + aggregate switch) ---
    @output
    @render.plot
    def plot_trend():
        d = filtered_df()
        metric = _metric_col()

        if d.empty:
            fig, ax = plt.subplots()
            ax.set_title("Trend Chart")
            ax.text(0.5, 0.5, "No data for selected filters", ha="center", va="center")
            ax.axis("off")
            return fig

        d2 = d.copy()
        d2["month_start"] = d2["order_date"].dt.to_period("M").dt.to_timestamp()

        by_cat = (
            d2.groupby(["month_start", "product_category"], as_index=False)[metric]
              .sum()
              .sort_values("month_start")
        )

        fig, ax = plt.subplots(constrained_layout=True)
        for cat, g in by_cat.groupby("product_category"):
            ax.plot(g["month_start"], g[metric], marker="o", linewidth=1, label=str(cat))

        if input.input_aggregate():
            overall = d2.groupby("month_start", as_index=False)[metric].sum().sort_values("month_start")
            ax.plot(overall["month_start"], overall[metric], linewidth=2, label="Aggregate")
        
        if metric == "total_revenue":
            ax.set_ylabel("Total revenue (USD)")
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"${x:,.0f}"))

        else:
            ax.set_ylabel("Total quantity sold (units)")

        ax.set_xlabel("Month")
        ax.set_xlabel("Month")
        
        ax.tick_params(axis="x", rotation=45)
        ax.legend(loc="best", fontsize=8)
        fig.tight_layout()
        return fig

    # --- "Map" placeholder (reactive summary by region) ---
    @output
    @render_widget 
    def plot_map():
        d = filtered_df()
        metric = _metric_col()
        
        # Create a clean label for the tooltip
        metric_label = "Total Revenue" if metric == "total_revenue" else "Total Orders"
        
        if d.empty:
            fig = px.choropleth(scope="world")
            fig.update_layout(title="No data for selected filters", margin={"r":0,"t":40,"l":0,"b":0})
            return fig

        # 1. Aggregate your data by the custom regions
        region_summary = d.groupby("customer_region", as_index=False)[metric].sum()

        map_data = [] 

        # 2. Map data and format the numbers for the tooltip
        for _, row in region_summary.iterrows():
            region_name = row["customer_region"]
            value = row[metric]
            
            # Format as currency or standard number
            if metric == "total_revenue":
                formatted_val = f"${value:,.2f}"
            else:
                formatted_val = f"{value:,.0f}"

            if region_name in REGION_MAPPING:
                for country in REGION_MAPPING[region_name]:
                    map_data.append({
                        "Country": country, 
                        "Region": region_name, 
                        metric_label: formatted_val
                    })
        
        if not map_data:
            fig = px.choropleth(scope="world")
            fig.update_layout(title="No mapped countries for selected regions", margin={"r":0,"t":40,"l":0,"b":0})
            return fig

        plot_df = pd.DataFrame(map_data)

        # 3. Create the Categorical Map
        fig = px.choropleth(
            plot_df,
            locations="Country",
            locationmode="country names",
            color="Region",  # <--- CHANGED: Colors by Region category instead of Value
            hover_name="Region", # <--- Sets the bold title of the tooltip to the Region
            hover_data={
                "Country": False,  # <--- Hides the specific country name
                "Region": False,   # Hides the redundant region row
                metric_label: True # Shows our formatted metric
            },
            color_discrete_sequence=px.colors.qualitative.Pastel, # Distinct, visually pleasing colors
            scope="world"
        )

        # 4. Background and Constant Zoom
        fig.update_geos(
            showcountries=True, 
            countrycolor="White", # Makes borders cleaner between colored blocks
            showocean=True, 
            oceancolor="#f0f8ff", # Very light blue for ocean
            projection_type="equirectangular"
        )

        fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            dragmode=False, 
            legend_title_text="Regions" # Updates the legend title
        )
        
        return fig
    
    # --- Season plot (reactive; shown only when input_season is ON in UI) ---
    @output
    @render.plot
    def plot_season():
        d = filtered_df()
        metric = _metric_col()

        fig, ax = plt.subplots(constrained_layout=True)
        if d.empty:
            ax.set_title("Average Sales by Season")
            ax.text(0.5, 0.5, "No data for selected filters", ha="center", va="center")
            ax.axis("off")
            return fig

        d2 = d.copy()
        m = d2["order_date"].dt.month
        d2["season"] = np.select(
            [m.isin([12, 1, 2]), m.isin([3, 4, 5]), m.isin([6, 7, 8]), m.isin([9, 10, 11])],
            ["Winter", "Spring", "Summer", "Fall"],
            default="Unknown"
        )

        # average per season by category
        season_summary = (
            d2.groupby(["season", "product_category"], as_index=False)[metric]
              .mean()
        )

        season_order = ["Winter", "Spring", "Summer", "Fall"]
        season_summary["season"] = pd.Categorical(season_summary["season"], season_order, ordered=True)
        season_summary = season_summary.sort_values(["season", "product_category"])

        # simple grouped bar (one bar per category per season)
        seasons = season_order
        cats = season_summary["product_category"].unique().tolist()
        x = np.arange(len(seasons))
        width = 0.8 / max(len(cats), 1)

        for i, cat in enumerate(cats):
            vals = []
            for s in seasons:
                row = season_summary[(season_summary["season"] == s) & (season_summary["product_category"] == cat)]
                vals.append(float(row[metric].iloc[0]) if not row.empty else 0.0)
            ax.bar(x + i * width, vals, width=width, label=str(cat))

        if metric == "total_revenue":
            ax.set_xlabel("Season")
            ax.set_ylabel("Average revenue (USD)")
            ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"${x:,.0f}"))
        else:
            ax.set_xlabel("Season")
            ax.set_ylabel("Average quantity sold (units)")

        ax.set_xticks(x + width * (len(cats) - 1) / 2 if len(cats) else x)
        ax.set_xticklabels(seasons)
        ax.legend(fontsize=8)
        fig.tight_layout()
        return fig

    # --- Payment method bar (reactive) ---
    @output
    @render.plot
    def payment_method_bar():
        d = filtered_df()

        fig, ax = plt.subplots(constrained_layout=True)
        if d.empty:
            ax.set_title("Revenue by Payment Method")
            ax.text(0.5, 0.5, "No data for selected filters", ha="center", va="center")
            ax.axis("off")
            return fig

        pm = (
            d.groupby("payment_method", as_index=False)["total_revenue"]
             .sum()
             .sort_values("total_revenue", ascending=False)
        )

        ax.bar(pm["payment_method"], pm["total_revenue"])
        ax.set_xlabel("Payment Method")
        ax.set_ylabel("Total revenue (USD)")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: f"${x:,.0f}"))
        ax.tick_params(axis="x", rotation=20)
        fig.tight_layout()
        return fig
    
    #add dynamic header for plot to show selected metric
    @output
    @render.ui
    def trend_header():
        if input.input_metric() == "total_revenue":
            return ui.card_header("Monthly Revenue Trend by Product Category")
        else:
            return ui.card_header("Monthly Quantity Sold Trend by Product Category")

    @output
    @render.ui
    def season_header():
        if input.input_metric() == "total_revenue":
            return ui.card_header("Average Revenue by Season")
        else:
            return ui.card_header("Average Quantity Sold by Season")

    @output
    @render.ui
    def payment_header():
        return ui.card_header("Total Revenue by Payment Method")

app = App(app_ui, server)