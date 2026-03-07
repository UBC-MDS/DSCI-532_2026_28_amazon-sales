from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_widget
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from matplotlib.ticker import FuncFormatter
from anthropic import Anthropic

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

app_ui = ui.page_navbar(
    ui.nav_panel(
        "Dashboard",
        ui.page_fluid(
            ui.panel_title("Amazon Sales Dashboard"),
            ui.layout_sidebar(
                ui.sidebar(

                    ui.input_slider(
                        id="input_year",
                        label="Years",
                        min=min_year, 
                        max=max_year, 
                        value=(min_year, max_year),
                        step=1,
                        sep="", 
                    ),

                    ui.input_selectize(
                        id="input_month",
                        label="Months",
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
                        label="Categories (Max 3)",
                        choices=categories,
                        selected=default_category,
                        multiple=True,
                        options={"maxItems": 3},
                    ),

                    ui.input_switch(
                        id="input_aggregate",
                        label="Compare to Aggregate",
                        value=False,
                    ),

                    ui.input_checkbox_group(
                        id="input_region",
                        label="Regions",
                        choices=regions,
                        selected=regions,
                    ),
                    
                    ui.input_radio_buttons(
                        id="input_metric",
                        label="Primary Metric",
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
                        ui.output_ui("trend_header"),
                        ui.output_plot("plot_trend"),
                    ),
                    ui.card(
                        ui.card_header("Selected Regions"),
                        output_widget("plot_map"),
                    ),
                    col_widths=(6, 6),
                ),

                # 3. Bottom Row
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
            # Footer
            ui.tags.footer(
                ui.HTML(
                    """
                    <div style="text-align: center; margin-top: 30px; margin-bottom: 20px; padding-top: 15px; border-top: 1px solid #e5e5e5; color: #6c757d; font-size: 0.9em;">
                        <p style="margin-bottom: 5px;"><strong>Amazon Sales Dashboard:</strong> An interactive tool for exploring product trends, regional performance, and seasonal sales patterns.</p>
                        <p style="margin-bottom: 5px;"><strong>Authors:</strong> Hoi Hin Kwok, Yanxin Liang, Eduardo Sanchez</p>
                        <p style="margin-bottom: 0;">
                            <a href="https://github.com/UBC-MDS/DSCI_524_group_25" target="_blank" style="color: #0d6efd; text-decoration: none;">GitHub Repository</a> 
                            | Last Updated: Feb 2026
                        </p>
                    </div>
                    """
                )
            )
        )
    ),
    ui.nav_panel(
    "AI Assistant",
        ui.page_fluid(
            ui.h3("Ask the Data"),
            ui.p("Use natural language to filter the dataset."),

            ui.input_text_area(
                "ai_query",
                "Your query",
                placeholder="Example: show electronics orders in North America in 2023",
                rows=3,
            ),

            ui.input_action_button("run_ai_query", "Run query"),

            ui.br(),
            ui.br(),

            ui.output_text("ai_status"),

            ui.hr(),

            ui.h4("Filtered dataframe"),
            ui.output_data_frame("ai_filtered_table"),
        )
    ),
title="Amazon Sales Dashboard",
)
   

def server(input, output, session):

    ai_df_store = reactive.value(df.copy())
    ai_status_store = reactive.value("Waiting for a query.")

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
    
    def parse_query_rule_based(query: str):
        query = query.lower().strip()

        filters = {
            "categories": [],
            "regions": [],
            "years": [],
            "payment_methods": [],
        }

        query_words = set(query.replace(",", " ").split())

        for cat in categories:
            cat_lower = cat.lower()
            cat_words = set(cat_lower.split())

            if cat_lower in query:
                filters["categories"].append(cat)
            elif any(word in query_words for word in cat_words):
                filters["categories"].append(cat)
            elif cat_lower.endswith("s") and cat_lower[:-1] in query_words:
                filters["categories"].append(cat)

        for region in regions:
            region_lower = region.lower()
            if region_lower in query:
                filters["regions"].append(region)

        for year in range(min_year, max_year + 1):
            if str(year) in query:
                filters["years"].append(year)

        payment_methods = sorted(df["payment_method"].dropna().unique().tolist())
        for pm in payment_methods:
            pm_lower = pm.lower()
            if pm_lower in query:
                filters["payment_methods"].append(pm)

        return filters


    @reactive.effect
    @reactive.event(input.run_ai_query)
    def _run_ai_query():
        query = input.ai_query().strip()

        if not query:
            ai_df_store.set(df.copy())
            ai_status_store.set("No query entered. Showing full dataset.")
            return

        filters = parse_query_rule_based(query)

        no_filters_found = (
            not filters["years"]
            and not filters["categories"]
            and not filters["regions"]
            and not filters["payment_methods"]
        )

        if no_filters_found:
            ai_df_store.set(df.iloc[0:0].copy())
            ai_status_store.set("No recognizable filters found in query.")
            return

        d = df.copy()

        if filters["years"]:
            d = d[d["order_date"].dt.year.isin(filters["years"])]

        if filters["categories"]:
            d = d[d["product_category"].isin(filters["categories"])]

        if filters["regions"]:
            d = d[d["customer_region"].isin(filters["regions"])]

        if filters["payment_methods"]:
            d = d[d["payment_method"].isin(filters["payment_methods"])]

        ai_df_store.set(d)
        ai_status_store.set(f"Matched {len(d):,} rows.")


    #--- Chatbot DF output ---
    @output
    @render.text
    def ai_status():
        return ai_status_store()

    @output
    @render.data_frame
    def ai_filtered_table():
        return render.DataGrid(ai_df_store(), filters=True)
    

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