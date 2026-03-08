from shiny import App, ui, reactive, render
from shinywidgets import output_widget, render_widget
import pandas as pd
from pathlib import Path
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =============================================================================
# 1. Data Loading and Preprocessing
# =============================================================================
DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "amazon_sales_dataset.csv"

amazon_df = pd.read_csv(DATA_PATH, parse_dates=["order_date"])
amazon_df["total_revenue"] = pd.to_numeric(amazon_df["total_revenue"], errors="coerce").fillna(0)
amazon_df["quantity_sold"] = pd.to_numeric(amazon_df["quantity_sold"], errors="coerce").fillna(0)

min_year, max_year = amazon_df["order_date"].dt.year.min(), amazon_df["order_date"].dt.year.max()
year_choices = [str(y) for y in range(min_year, max_year + 1)]
unique_categories = sorted(amazon_df["product_category"].dropna().unique().tolist())
unique_regions = sorted(amazon_df["customer_region"].dropna().unique().tolist())

REGION_COUNTRY_MAPPING = {
    "Asia": ["China", "India", "Japan", "South Korea", "Vietnam", "Thailand", "Indonesia", "Malaysia", "Philippines", "Singapore", "Taiwan"],
    "Europe": ["Germany", "France", "United Kingdom", "Italy", "Spain", "Netherlands", "Belgium", "Switzerland", "Sweden", "Norway", "Poland", "Portugal"],
    "Middle East": ["Saudi Arabia", "United Arab Emirates", "Israel", "Turkey", "Qatar", "Kuwait", "Jordan", "Oman", "Lebanon"],
    "North America": ["United States", "Canada", "Mexico"]
}

# =============================================================================
# 2. User Interface (UI)
# =============================================================================
app_ui = ui.page_fillable(
    ui.panel_title("Amazon Sales Dashboard"),
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_checkbox_group("input_year", "Years", choices=year_choices, selected=year_choices, inline=True),
            ui.input_selectize(
                "input_month", "Months", 
                choices={i: m for i, m in enumerate(["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)},
                multiple=True, selected=list(range(1, 13))
            ),
            ui.input_selectize("input_category", "Categories", choices=unique_categories, selected=unique_categories[0], multiple=True, options={"maxItems": 3}),
            ui.input_checkbox_group("input_region", "Regions", choices=unique_regions, selected=unique_regions, inline=False),
            ui.input_radio_buttons("input_metric", "Primary Metric:", choices={"total_revenue": "Revenue ($)", "quantity_sold": "Units Sold"}, selected="total_revenue", inline=True),
            ui.input_switch("input_aggregate", "Show Aggregate", value=False),
            ui.input_switch("input_season", "Show Seasonality", value=True),
            ui.input_action_button("reset_btn", "Reset All Filters", class_="btn-warning mt-2"),
            ui.HTML('<hr><div style="font-size: 0.85em; color: #6c757d;"><strong>Group 25 Dashboard</strong> | Feb 2026</div>'),
            width=260,
        ),

        # The Layout Engine: 
        # Using fill=True and row_heights=(2, 1) ensures Row 1 is 2/3 and Row 2 is 1/3
        ui.layout_columns(
            # --- ROW 1: 2/3 Height ---
            ui.layout_columns(
                ui.card(
                    ui.card_header("Regional Distribution (Click to filter)"), 
                    output_widget("plot_map"),
                    full_screen=True
                ),
                ui.layout_columns(
                    ui.card(ui.div(ui.strong("Total Revenue: "), ui.output_text("valuebox_revenue", inline=True)), class_="bg-primary text-white fs-5 p-2"),
                    ui.card(ui.div(ui.strong("Total Orders: "), ui.output_text("valuebox_orders", inline=True)), class_="bg-info text-white fs-5 p-2"),
                    ui.card(ui.output_ui("trend_header"), output_widget("plot_trend"), full_screen=True),
                    col_widths=(6, 6, 12), row_heights=["auto", "1fr"]
                ),
                col_widths=(7, 5),
                fill=True
            ),

            # --- ROW 2: 1/3 Height ---
            ui.layout_columns(
                ui.panel_conditional(
                    "input.input_season", 
                    ui.card(ui.output_ui("season_header"), output_widget("plot_season"), full_screen=True),
                ),
                ui.card(ui.output_ui("payment_header"), output_widget("payment_method_bar"), full_screen=True),
                col_widths=(6, 6),
                fill=True
            ),
            col_widths=12,
            row_heights=(2, 1), # THIS FIXES THE 2/3 TO 1/3 SPLIT
            fill=True,
            gap="15px"
        )
    ),
)

# =============================================================================
# 3. Server Logic
# =============================================================================
def server(input, output, session):

    clicked_region_state = reactive.Value(None)

    @reactive.Effect
    @reactive.event(input.reset_btn)
    def _():
        ui.update_checkbox_group("input_year", selected=year_choices)
        ui.update_selectize("input_month", selected=list(range(1, 13)))
        ui.update_selectize("input_category", selected=[unique_categories[0]])
        ui.update_checkbox_group("input_region", selected=unique_regions)
        ui.update_radio_buttons("input_metric", selected="total_revenue")
        ui.update_switch("input_aggregate", value=False)
        ui.update_switch("input_season", value=True)

    @reactive.calc
    def m_info():
        is_rev = input.input_metric() == "total_revenue"
        return {
            "id": input.input_metric(),
            "label": "Revenue ($)" if is_rev else "Units Sold",
            "format": "$,.0s" if is_rev else ",.0f",
            "short": "Revenue" if is_rev else "Quantity"
        }

    @reactive.calc
    def base_filtered_data():
        df = amazon_df.copy()
        years = [int(y) for y in (input.input_year() or [])]
        months = [int(m) for m in (input.input_month() or [])]
        cats = input.input_category() or []
        if not (years and months and cats): return df.iloc[0:0]
        return df[df["order_date"].dt.year.isin(years) & df["order_date"].dt.month.isin(months) & df["product_category"].isin(cats)]

    @reactive.calc
    def fully_filtered_data():
        df = base_filtered_data()
        regions = input.input_region() or []
        return df[df["customer_region"].isin(regions)] if regions else df.iloc[0:0]

    def get_empty_fig():
        return px.line(title="No data").update_layout(template="plotly_white", xaxis_visible=False, yaxis_visible=False)

    @output
    @render.text
    def valuebox_revenue(): return f"${fully_filtered_data()['total_revenue'].sum():,.0f}"

    @output
    @render.text
    def valuebox_orders(): return f"{fully_filtered_data()['order_id'].nunique():,}"

    @output
    @render_widget
    def plot_trend():
        df = fully_filtered_data()
        if df.empty: return get_empty_fig()
        info = m_info()
        df["month_start"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
        grouped = df.groupby(["month_start", "product_category"], as_index=False)[info["id"]].sum()
        fig = px.line(grouped, x="month_start", y=info["id"], color="product_category", markers=True, template="plotly_white")
        if input.input_aggregate():
            agg = df.groupby("month_start", as_index=False)[info["id"]].sum()
            fig.add_scatter(x=agg["month_start"], y=agg[info["id"]], mode="lines+markers", name=f"Total {info['short']}", line=dict(color="black", dash="dash"))
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), yaxis_title=info["label"], xaxis_title=None)
        fig.update_yaxes(tickformat=info["format"])
        return fig

    @output
    @render_widget 
    def plot_map():
        df = base_filtered_data()
        info = m_info()
        if df.empty: return get_empty_fig()
        summary = df.groupby("customer_region", as_index=False)[info["id"]].sum()
        map_list = []
        selected_regions = list(input.input_region() or [])
        for _, row in summary.iterrows():
            reg = row["customer_region"]
            if reg in REGION_COUNTRY_MAPPING:
                for country in REGION_COUNTRY_MAPPING[reg]:
                    map_list.append({"Country": country, "Region": reg, info["label"]: row[info["id"]]})
        if not map_list: return get_empty_fig()
        fig = px.choropleth(pd.DataFrame(map_list), locations="Country", locationmode="country names", color="Region", custom_data=["Region"], scope="world", template="plotly_white")
        fig.update_geos(showocean=True, oceancolor="#E8F4F8")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, clickmode="event", showlegend=False)
        for trace in fig.data: trace.marker.opacity = 1.0 if trace.name in selected_regions else 0.2
        fw = go.FigureWidget(fig)
        def handle_click(trace, points, state):
            if points.point_inds: clicked_region_state.set(trace.customdata[points.point_inds[0]][0])
        for trace in fw.data: trace.on_click(handle_click)
        return fw

    @reactive.Effect
    def _sync_map():
        region = clicked_region_state()
        if region:
            current = list(input.input_region() or [])
            if region in current: current.remove(region)
            else: current.append(region)
            ui.update_checkbox_group("input_region", selected=current)
            clicked_region_state.set(None)

    @output
    @render_widget
    def plot_season():
        df = fully_filtered_data()
        if df.empty: return get_empty_fig()
        info, mapping = m_info(), {12: "Winter", 1: "Winter", 2: "Winter", 3: "Spring", 4: "Spring", 5: "Spring", 6: "Summer", 7: "Summer", 8: "Summer", 9: "Fall", 10: "Fall", 11: "Fall"}
        df["season"] = df["order_date"].dt.month.map(mapping)
        grouped = df.groupby(["season", "product_category"], as_index=False)[info["id"]].sum()
        grouped["season"] = pd.Categorical(grouped["season"], ["Spring", "Summer", "Fall", "Winter"], ordered=True)
        fig = px.bar(grouped.sort_values("season"), x="season", y=info["id"], color="product_category", barmode="group", template="plotly_white")
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), yaxis_title=info["label"], xaxis_title=None)
        fig.update_yaxes(tickformat=info["format"])
        return fig

    @output
    @render_widget
    def payment_method_bar():
        df = fully_filtered_data()
        if df.empty: return get_empty_fig()
        info = m_info()
        grouped = df.groupby("payment_method", as_index=False)[info["id"]].sum().sort_values(info["id"], ascending=False)
        fig = px.bar(grouped, x="payment_method", y=info["id"], color="payment_method", template="plotly_white")
        fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), showlegend=False, yaxis_title=info["label"], xaxis_title=None)
        fig.update_yaxes(tickformat=info["format"])
        return fig

    @output
    @render.ui
    def trend_header(): return ui.card_header(f"{m_info()['short']} Trends by Category")
    @output
    @render.ui
    def season_header(): return ui.card_header(f"Total {m_info()['short']} by Season")
    @output
    @render.ui
    def payment_header(): return ui.card_header(f"{m_info()['short']} by Payment Method")

app = App(app_ui, server)