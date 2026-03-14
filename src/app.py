from shiny import App, ui, reactive, render, req
from shinywidgets import output_widget, render_widget
import pandas as pd
from pathlib import Path
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import os
import json
import requests

# =============================================================================
# 1. Data Loading and Preprocessing
# =============================================================================
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "amazon_sales_dataset.csv"

# Load and sanitize data
df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])
df["total_revenue"] = pd.to_numeric(df["total_revenue"], errors="coerce").fillna(0)

min_year, max_year = int(df["order_date"].dt.year.min()), int(df["order_date"].dt.year.max())
year_choices = [str(y) for y in range(min_year, max_year + 1)]
categories = sorted(df["product_category"].dropna().unique().tolist())
regions = sorted(df["customer_region"].dropna().unique().tolist())

REGION_COUNTRY_MAPPING = {
    "Asia": ["China", "India", "Japan", "South Korea", "Vietnam", "Thailand", "Indonesia", "Malaysia", "Philippines", "Singapore", "Taiwan"],
    "Europe": ["Germany", "France", "United Kingdom", "Italy", "Spain", "Netherlands", "Belgium", "Switzerland", "Sweden", "Norway", "Poland", "Portugal"],
    "Middle East": ["Saudi Arabia", "United Arab Emirates", "Israel", "Turkey", "Qatar", "Kuwait", "Jordan", "Oman", "Lebanon"],
    "North America": ["United States", "Canada", "Mexico"]
}

LABEL_MAP = {
    "month_start": "Month",
    "product_category": "Category",
    "season": "Season",
    "payment_method": "Payment Method",
    "total_revenue": "Revenue ($)",
    "order_id": "Total Orders",
    "customer_region": "Region"
}

# =============================================================================
# 2. User Interface (UI) Definition
# =============================================================================
app_ui = ui.page_navbar(
    # --- TAB 1: DASHBOARD ---
    ui.nav_panel(
        "Dashboard",
        ui.page_fillable(
            ui.layout_sidebar(
                ui.sidebar(
                    ui.input_checkbox_group("input_year", "Years", choices=year_choices, selected=year_choices, inline=True),
                    ui.input_selectize(
                        "input_month", "Months", 
                        choices={i: m for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)},
                        multiple=True, selected=list(range(1, 13))
                    ),
                    ui.input_selectize("input_category", "Categories (Max 3)", choices=categories, selected=categories[0], multiple=True, options={"maxItems": 3}),
                    ui.output_ui("aggregate_switch_ui"),                    
                    ui.input_checkbox_group("input_region", "Regions", choices=regions, selected=regions, inline=False),
                    ui.input_radio_buttons("input_metric", "Primary Metric:", choices={"total_revenue": "Revenue ($)", "order_id": "Total Orders"}, selected="total_revenue", inline=True),
                    ui.input_switch("input_season", "Show Seasonality", value=True),
                    ui.input_action_button("reset_btn", "Reset All Filters", class_="btn-warning mt-2"),
                    width=260,
                ),

                # Main Display Area
                ui.div(
                    # ROW 1 (3/5 Height Ratio)
                    ui.div(
                        ui.layout_columns(
                            ui.layout_columns(
                                ui.card(ui.div(ui.strong("Total Revenue: "), ui.output_text("valuebox_revenue", inline=True)), class_="d-flex justify-content-center align-items-center bg-primary text-white fs-6 p-2 m-0 text-nowrap"),
                                ui.card(ui.div(ui.strong("Total Orders: "), ui.output_text("valuebox_orders", inline=True)), class_="d-flex justify-content-center align-items-center bg-info text-white fs-6 p-2 m-0 text-nowrap"),
                                ui.card(ui.output_ui("trend_header"), output_widget("plot_trend")),
                                col_widths=(6, 6, 12), row_heights=["min-content", "1fr"], gap="10px", height="100%"
                            ),
                            ui.card(ui.card_header("Regional Distribution (Click to filter)"), output_widget("plot_map")),
                            col_widths=(5, 7), gap="10px", height="100%"
                        ),
                        style="flex: 3 1 0; min-height: 0;"
                    ),
                    
                    # ROW 2 (2/5 Height Ratio)
                    ui.div(
                        ui.layout_columns(
                            ui.div(
                                ui.panel_conditional("input.input_season", ui.card(ui.output_ui("season_header"), output_widget("plot_season"), style="height: 100%; margin: 0;")),
                                style="height: 100%;"
                            ),
                            ui.card(ui.output_ui("payment_header"), output_widget("payment_method_bar")),
                            col_widths=(6, 6), gap="10px", height="100%"
                        ),
                        style="flex: 2 1 0; min-height: 0;"
                    ),
                    # Unified Footer
                    ui.tags.footer(
                        ui.div(
                            ui.div(ui.strong("Project: Amazon Sales Dashboard"), style="margin-bottom: 2px;"),
                            ui.span("Authors: Hoi Hin Kwok, Yanxin Liang, Eduardo Sanchez"),
                            ui.span(" | "),
                            ui.tags.a("GitHub Repository", href="https://github.com/UBC-MDS/DSCI-532_2026_28_amazon-sales", target="_blank"),
                            ui.span(" | "),
                            ui.tags.a("Data Source: Kaggle", href="https://www.kaggle.com/datasets/aliiihussain/amazon-sales-dataset", target="_blank"),
                            ui.div("Last Modified: March 2026", style="font-size: 0.9em; margin-top: 2px;"),
                            style="text-align: center; color: #6c757d; font-size: 0.72em; padding: 5px; border-top: 1px solid #eee;"
                        ),
                        style="flex: 0 0 auto;"
                    ),
                    style="display: flex; flex-direction: column; height: calc(100vh - 80px); gap: 10px; overflow: hidden;"
                ),
            ),
        )
    ),

    # --- TAB 2: AI ASSISTANT ---
    ui.nav_panel(
        "AI Assistant",
        ui.page_fluid(
            ui.h3("Ask the Data", class_="mt-3"),
            ui.p("Use natural language to filter the dataset."),
            ui.input_text_area("ai_query", "Your query", placeholder="Example: electronics orders in North America in 2023", rows=3),
            ui.div(
                ui.input_action_button("run_ai_query", "Run Query", class_="btn-primary"), 
                ui.download_button("download_ai_data", "Download CSV"), 
                style="display: flex; gap: 10px;"
            ),
            ui.br(), ui.output_text("ai_status"), ui.hr(),
            ui.h4("Filtered Dataframe"),
            ui.output_data_frame("ai_filtered_table"),
            ui.hr(),
            ui.layout_columns(
                ui.card(ui.card_header("Revenue Trend by Category"), ui.output_plot("ai_plot_trend")),
                ui.card(ui.card_header("Average Revenue by Season"), ui.output_plot("ai_plot_season")),
                col_widths=(6, 6)
            ),
        )
    ),
    title="Amazon Sales Dashboard",
    fillable=True,
)

# =============================================================================
# 3. Server Logic
# =============================================================================
def server(input, output, session):

    # --- Reactive Value Stores ---
    clicked_region_state = reactive.Value(None)
    ai_df_store = reactive.Value(df.copy())
    ai_status_store = reactive.Value("Waiting for a query.")

    # --- DASHBOARD LOGIC ---

    @output
    @render.ui
    def aggregate_switch_ui():
        # Read the current categories
        cats = input.input_category()
        
        # Only render the switch if more than 1 category is selected
        if cats is not None and len(cats) > 1:
            return ui.input_switch("input_aggregate", "Show Aggregate", value=True)
        return None
    
    @reactive.effect
    @reactive.event(input.reset_btn)
    def _reset_filters():
        ui.update_checkbox_group("input_year", selected=year_choices)
        ui.update_selectize("input_month", selected=list(range(1, 13)))
        ui.update_selectize("input_category", selected=[categories[0]])
        ui.update_checkbox_group("input_region", selected=regions)
        ui.update_radio_buttons("input_metric", selected="total_revenue")
        ui.update_switch("input_aggregate", value=False)
        ui.update_switch("input_season", value=True)

    @reactive.calc
    def m_info():
        is_rev = input.input_metric() == "total_revenue"
        return {
            "id": input.input_metric(),
            "label": "Revenue ($)" if is_rev else "Total Orders",
            "exact_format": "$,.0f" if is_rev else ",.0f",
            "short": "Revenue" if is_rev else "Orders",
            "agg_func": "sum" if is_rev else "nunique"
        }

    @reactive.calc
    def dashboard_filtered_df():
        d = df.copy()
        years = [int(y) for y in (input.input_year() or [])]
        months = [int(m) for m in (input.input_month() or [])]
        cats = input.input_category() or []
        regs = input.input_region() or []
        if not (years and months and cats and regs): return d.iloc[0:0]
        return d[d["order_date"].dt.year.isin(years) & d["order_date"].dt.month.isin(months) & d["product_category"].isin(cats) & d["customer_region"].isin(regs)]

    @output 
    @render.text
    def valuebox_revenue(): return f"${dashboard_filtered_df()['total_revenue'].sum():,.0f}"

    @output 
    @render.text
    def valuebox_orders(): return f"{dashboard_filtered_df()['order_id'].nunique():,}"

    @output 
    @render_widget
    def plot_trend():
        d = dashboard_filtered_df()
        if d.empty: return px.line(title="No data").update_layout(template="plotly_white")
        info = m_info()
        d["month_start"] = d["order_date"].dt.to_period("M").dt.to_timestamp()
        grouped = d.groupby(["month_start", "product_category"], as_index=False).agg({info["id"]: info["agg_func"]})
        fig = px.line(grouped, x="month_start", y=info["id"], color="product_category", markers=True, template="plotly_white", labels=LABEL_MAP)
        if input.input_aggregate():
            agg = d.groupby("month_start", as_index=False).agg({info["id"]: info["agg_func"]})
            fig.add_scatter(x=agg["month_start"], y=agg[info["id"]], mode="lines+markers", name="Aggregate", line=dict(color="black", dash="dash"))
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), yaxis_title=info["label"], yaxis_tickformat=info["exact_format"])
        return fig

    @output 
    @render_widget 
    def plot_map():
        # Map ignores region sidebar for background view
        d_base = df.copy()
        years, months, cats = [int(y) for y in (input.input_year() or [])], [int(m) for m in (input.input_month() or [])], input.input_category() or []
        d_base = d_base[d_base["order_date"].dt.year.isin(years) & d_base["order_date"].dt.month.isin(months) & d_base["product_category"].isin(cats)]
        info = m_info()
        if d_base.empty: return px.choropleth(scope="world").update_layout(template="plotly_white")
        summary = d_base.groupby("customer_region", as_index=False).agg({info["id"]: info["agg_func"]})
        map_list = []
        selected_regs = list(input.input_region() or [])
        for _, row in summary.iterrows():
            reg = row["customer_region"]
            val = row[info["id"]]
            fmt_val = f"${val:,.0f}" if info["id"] == "total_revenue" else f"{val:,.0f}"
            if reg in REGION_COUNTRY_MAPPING:
                for country in REGION_COUNTRY_MAPPING[reg]:
                    map_list.append({"Country": country, "Region": reg, "FormattedValue": fmt_val, info["id"]: val})
        if not map_list: return px.choropleth(scope="world").update_layout(template="plotly_white")
        fig = px.choropleth(pd.DataFrame(map_list), locations="Country", locationmode="country names", color="Region", custom_data=["Region", "FormattedValue"], template="plotly_white", labels=LABEL_MAP)
        fig.update_traces(hovertemplate="<b>%{customdata[0]}</b><br>" + info["label"] + ": %{customdata[1]}<extra></extra>")
        fig.update_geos(showcountries=True, countrycolor="White", showocean=True, oceancolor="#E8F4F8", projection_type="equirectangular")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, clickmode="event", showlegend=False, dragmode=False)
        for trace in fig.data: trace.marker.opacity = 1.0 if trace.name in selected_regs else 0.2
        fw = go.FigureWidget(fig)
        def handle_click(trace, points, state):
            if points.point_inds: clicked_region_state.set(trace.customdata[points.point_inds[0]][0])
        for trace in fw.data: trace.on_click(handle_click)
        return fw

    @reactive.effect
    def _sync_map_click():
        reg = clicked_region_state()
        if reg:
            current = list(input.input_region() or [])
            if reg in current: current.remove(reg)
            else: current.append(reg)
            ui.update_checkbox_group("input_region", selected=current)
            clicked_region_state.set(None)

    @output 
    @render_widget
    def plot_season():
        d = dashboard_filtered_df()
        if d.empty: return px.line(title="No data").update_layout(template="plotly_white")
        info, mapping = m_info(), {12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring", 6: "Summer", 7: "Summer", 8: "Summer", 9: "Fall", 10: "Fall", 11: "Fall"}
        d["season"] = d["order_date"].dt.month.map(mapping)
        grouped = d.groupby(["season", "product_category"], as_index=False).agg({info["id"]: info["agg_func"]})
        grouped["season"] = pd.Categorical(grouped["season"], ["Spring", "Summer", "Fall", "Winter"], ordered=True)
        fig = px.line(grouped.sort_values("season"), x="season", y=info["id"], color="product_category", markers=True, template="plotly_white", labels=LABEL_MAP)
        fig.update_yaxes(rangemode="normal") 
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), yaxis_title=info["label"], yaxis_tickformat=info["exact_format"])
        return fig

    @output 
    @render_widget
    def payment_method_bar():
        d = dashboard_filtered_df()
        if d.empty: return px.bar(title="No data").update_layout(template="plotly_white")
        info = m_info()
        grouped = d.groupby("payment_method", as_index=False).agg({info["id"]: info["agg_func"]}).sort_values(info["id"], ascending=False)
        fig = px.bar(grouped, x="payment_method", y=info["id"], color="payment_method", template="plotly_white", labels=LABEL_MAP)
        fig.update_yaxes(rangemode="normal")
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False, yaxis_title=info["label"], yaxis_tickformat=info["exact_format"])
        return fig

    # --- AI ASSISTANT LOGIC (Full Integration) ---

    def parse_query_rule_based(query: str):
        query = query.lower().strip()
        f = {"categories": [], "regions": [], "years": [], "payment_methods": []}
        words = set(query.replace(",", " ").split())
        for cat in categories:
            if cat.lower() in query or any(w in words for w in cat.lower().split()): f["categories"].append(cat)
        for reg in regions:
            if reg.lower() in query: f["regions"].append(reg)
        for yr in range(min_year, max_year + 1):
            if str(yr) in query: f["years"].append(yr)
        p_methods = sorted(df["payment_method"].dropna().unique().tolist())
        for pm in p_methods:
            if pm.lower() in query: f["payment_methods"].append(pm)
        return f

    @reactive.effect
    @reactive.event(input.run_ai_query)
    def _run_ai_logic():
        query = input.ai_query().strip()
        if not query:
            ai_df_store.set(df.copy())
            ai_status_store.set("Showing full dataset.")
            return
        
        # You can toggle between parse_query_github_models(query) or rule_based here
        filters = parse_query_rule_based(query)
        d_ai = df.copy()
        if filters["years"]: d_ai = d_ai[d_ai["order_date"].dt.year.isin(filters["years"])]
        if filters["categories"]: d_ai = d_ai[d_ai["product_category"].isin(filters["categories"])]
        if filters["regions"]: d_ai = d_ai[d_ai["customer_region"].isin(filters["regions"])]
        if filters["payment_methods"]: d_ai = d_ai[d_ai["payment_method"].isin(filters["payment_methods"])]
        
        ai_df_store.set(d_ai)
        ai_status_store.set(f"Found {len(d_ai):,} matches.")

    @output 
    @render.text
    def ai_status(): return ai_status_store()

    @output 
    @render.data_frame
    def ai_filtered_table(): return render.DataGrid(ai_df_store(), filters=True)

    @render.download(filename="ai_export.csv")
    def download_ai_data(): yield ai_df_store().to_csv(index=False)

    @output 
    @render.plot
    def ai_plot_trend():
        d = ai_df_store()
        fig, ax = plt.subplots(figsize=(6, 4))
        if d.empty: return fig
        d["m"] = d["order_date"].dt.to_period("M").dt.to_timestamp()
        d.groupby(["m", "product_category"])["total_revenue"].sum().unstack().fillna(0).plot(ax=ax, marker='o')
        ax.set_ylabel("Revenue ($)")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))
        return fig

    @output 
    @render.plot
    def ai_plot_season():
        d = ai_df_store()
        fig, ax = plt.subplots(figsize=(6, 4))
        if d.empty: return fig
        m = d["order_date"].dt.month
        d["season"] = np.select([m.isin([12,1,2]), m.isin([3,4,5]), m.isin([6,7,8])], ["Winter", "Spring", "Summer"], default="Fall")
        d.groupby(["season", "product_category"])["total_revenue"].mean().unstack().fillna(0).plot(kind='bar', ax=ax)
        ax.set_ylabel("Avg Revenue ($)")
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f"${x:,.0f}"))
        return fig

    # Titles
    @output 
    @render.ui
    def trend_header(): return ui.card_header(f"{m_info()['short']} Trends")
    @output 
    @render.ui
    def season_header(): return ui.card_header(f"Total {m_info()['short']} by Season")
    @output 
    @render.ui
    def payment_header(): return ui.card_header(f"{m_info()['short']} by Payment Method")

app = App(app_ui, server)