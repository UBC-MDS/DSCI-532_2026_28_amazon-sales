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

min_order_year = amazon_df["order_date"].dt.year.min()
max_order_year = amazon_df["order_date"].dt.year.max()

# Convert years to strings for consistent Shiny UI checkbox handling
year_choices = [str(year) for year in range(min_order_year, max_order_year + 1)]

unique_categories = sorted(amazon_df["product_category"].dropna().unique().tolist())
default_selected_category = unique_categories[0]

unique_regions = sorted(amazon_df["customer_region"].dropna().unique().tolist())

REGION_COUNTRY_MAPPING = {
    "Asia": ["China", "India", "Japan", "South Korea", "Vietnam", "Thailand", "Indonesia", "Malaysia", "Philippines", "Singapore", "Taiwan"],
    "Europe": ["Germany", "France", "United Kingdom", "Italy", "Spain", "Netherlands", "Belgium", "Switzerland", "Sweden", "Norway", "Poland", "Portugal"],
    "Middle East": ["Saudi Arabia", "United Arab Emirates", "Israel", "Turkey", "Qatar", "Kuwait", "Jordan", "Oman", "Lebanon"],
    "North America": ["United States", "Canada", "Mexico"]
}

# =============================================================================
# 2. User Interface (UI) Definition
# =============================================================================
app_ui = ui.page_fillable(
    ui.panel_title("Amazon Sales Dashboard"),
    
    ui.layout_sidebar(
        # --- Sidebar Navigation ---
        ui.sidebar(
            ui.input_checkbox_group(
                id="input_year", 
                label="Years", 
                choices=year_choices, 
                selected=year_choices, 
                inline=True
            ),
            ui.input_selectize(
                id="input_month", 
                label="Months", 
                choices={1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr", 5: "May", 6: "Jun", 7: "Jul", 8: "Aug", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}, 
                multiple=True, 
                selected=list(range(1, 13))
            ),
            ui.input_selectize(
                id="input_category", 
                label="Categories", 
                choices=unique_categories, 
                selected=default_selected_category, 
                multiple=True, 
                options={"maxItems": 3}
            ),
            ui.input_checkbox_group(
                id="input_region", 
                label="Regions", 
                choices=unique_regions, 
                selected=unique_regions, 
                inline=False
            ),
            ui.input_radio_buttons(
                id="input_metric", 
                label="Primary Metric:", 
                choices={"total_revenue": "Revenue ($)", "quantity_sold": "Units Sold"}, 
                selected="total_revenue", 
                inline=True
            ),
            
            ui.input_switch("input_aggregate", "Show Total", value=False),
            ui.input_switch("input_season", "Show Seasonality", value=True),
            ui.input_action_button("reset_btn", "Reset All Filters", class_="btn-warning mt-2"),
            
            ui.HTML(
                """
                <hr>
                <div style="font-size: 0.85em; color: #6c757d;">
                    <strong>Group 25 Dashboard</strong><br>
                    <a href="https://github.com/UBC-MDS/DSCI_524_group_25" target="_blank">GitHub Repo</a> | Feb 2026
                </div>
                """
            ),
            width=260,
        ),

        # --- Main Dashboard Area (Nested Layout) ---
        ui.div(
            
            # ROW 1: Map (Left) and KPIs/Trend Plot (Right)
            ui.layout_columns(
                ui.card(
                    ui.card_header("Regional Distribution (Click to filter)"), 
                    output_widget("plot_map"),
                    style="height: 100%; min-height: 0;"
                ),
                ui.layout_columns(
                    ui.card(
                        ui.div(ui.strong("Total Revenue: "), ui.output_text("valuebox_revenue", inline=True)),
                        class_="d-flex justify-content-center align-items-center bg-primary text-white fs-5 m-0 p-2"
                    ),
                    ui.card(
                        ui.div(ui.strong("Total Orders: "), ui.output_text("valuebox_orders", inline=True)),
                        class_="d-flex justify-content-center align-items-center bg-info text-white fs-5 m-0 p-2"
                    ),
                    ui.card(
                        ui.output_ui("trend_header"), 
                        output_widget("plot_trend")
                    ),
                    col_widths=(6, 6, 12),
                    row_heights=["1fr", "4fr"], 
                    gap="10px",
                    style="height: 100%; min-height: 0;"
                ),
                col_widths=(6, 6),
                gap="10px",
                style="flex: 2; min-height: 0;" 
            ),
            
            # ROW 2: Seasonality (Left) and Payment Methods (Right)
            ui.layout_columns(
                ui.div(
                    ui.panel_conditional(
                        "input.input_season", 
                        ui.card(
                            ui.output_ui("season_header"), 
                            output_widget("plot_season"),
                            style="height: 100%; margin-bottom: 0;"
                        ),
                        style="height: 100%;"
                    ),
                    style="height: 100%; min-height: 0;"
                ),
                ui.card(
                    ui.output_ui("payment_header"), 
                    output_widget("payment_method_bar"),
                    style="height: 100%; min-height: 0;"
                ),
                col_widths=(6, 6),
                gap="10px",
                style="flex: 1; min-height: 0;" 
            ),
            style="display: flex; flex-direction: column; height: 100%; gap: 10px;"
        )
    ),
)

# =============================================================================
# 3. Server Logic
# =============================================================================
def server(input, output, session):

    # --- Filter Reset Logic ---
    @reactive.Effect
    @reactive.event(input.reset_btn)
    def reset_all_filters():
        ui.update_checkbox_group("input_year", selected=year_choices)
        ui.update_selectize("input_month", selected=list(range(1, 13)))
        ui.update_selectize("input_category", selected=[default_selected_category])
        ui.update_switch("input_aggregate", value=False)
        ui.update_checkbox_group("input_region", selected=unique_regions)
        ui.update_radio_buttons("input_metric", selected="total_revenue")
        ui.update_switch("input_season", value=True)

    # --- Helper Functions ---
    def get_selected_months():
        selected_months = input.input_month()
        return [int(month) for month in selected_months] if selected_months is not None else list(range(1, 13))

    def get_active_metric():
        return "total_revenue" if input.input_metric() == "total_revenue" else "quantity_sold"

    # --- Reactive Data Processing ---
    
    # Base data (Filtered by time and category. Used by the Map)
    @reactive.calc
    def base_filtered_data():
        filtered_df = amazon_df.copy()
        
        selected_years = input.input_year()
        if not selected_years:
            return filtered_df.iloc[0:0]
            
        filtered_df = filtered_df[filtered_df["order_date"].dt.year.isin([int(year) for year in selected_years])]
        
        selected_months = get_selected_months()
        if not selected_months:
            return filtered_df.iloc[0:0]
            
        filtered_df = filtered_df[filtered_df["order_date"].dt.month.isin(selected_months)]
        
        selected_categories = input.input_category()
        if not selected_categories: 
            return filtered_df.iloc[0:0] 
            
        filtered_df = filtered_df[filtered_df["product_category"].isin(selected_categories)]
        return filtered_df

    # Fully filtered data (Used by all charts except the Map)
    @reactive.calc
    def fully_filtered_data():
        filtered_df = base_filtered_data()
        
        selected_regions = input.input_region()
        if not selected_regions:
            return filtered_df.iloc[0:0]
            
        filtered_df = filtered_df[filtered_df["customer_region"].isin(selected_regions)]
        return filtered_df

    # --- KPI Calculations ---
    @reactive.calc
    def calculate_kpis():
        data = fully_filtered_data()
        total_revenue = float(data["total_revenue"].sum()) if not data.empty else 0.0
        total_orders = int(data["order_id"].nunique()) if not data.empty else 0
        return {"total_revenue": total_revenue, "total_orders": total_orders}

    @output
    @render.text
    def valuebox_revenue(): 
        return f"${calculate_kpis()['total_revenue']:,.0f}"

    @output
    @render.text
    def valuebox_orders(): 
        return f"{calculate_kpis()['total_orders']:,}"

    # --- Plot: Monthly Trend ---
    @output
    @render_widget
    def plot_trend():
        data = fully_filtered_data()
        active_metric = get_active_metric()
        
        if data.empty: 
            return px.line(title="No data to display", template="plotly_white").update_layout(autosize=True, xaxis_visible=False, yaxis_visible=False)

        trend_df = data.copy()
        trend_df["month_start"] = trend_df["order_date"].dt.to_period("M").dt.to_timestamp()
        
        monthly_trend_data = trend_df.groupby(["month_start", "product_category"], as_index=False)[active_metric].sum().sort_values("month_start")
        
        fig = px.line(monthly_trend_data, x="month_start", y=active_metric, color="product_category", markers=True, template="plotly_white")

        if input.input_aggregate():
            aggregate_trend_data = trend_df.groupby("month_start", as_index=False)[active_metric].sum().sort_values("month_start")
            metric_label = "Revenue" if active_metric == "total_revenue" else "Units"
            fig.add_scatter(
                x=aggregate_trend_data["month_start"], 
                y=aggregate_trend_data[active_metric], 
                mode="lines+markers", 
                name=f"Total {metric_label}",
                line=dict(color="black", dash="dash", width=2)
            )
        y_axis_label = "Revenue ($)" if active_metric == "total_revenue" else "Units"
        
        fig.update_layout(
            autosize=True, 
            xaxis_title="Month", 
            yaxis_title=y_axis_label, 
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(font=dict(size=10), title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        if active_metric == "total_revenue":
            fig.update_yaxes(tickformat="$,.0s", automargin=True)
        else:
            fig.update_yaxes(automargin=True)
            
        fig.update_xaxes(tickangle=0, tickformat="%b %Y", automargin=True)
        return fig

    # --- Plot: Regional Map ---
    clicked_region_state = reactive.Value(None)

    @reactive.Effect
    def toggle_region_selection():
        clicked_region = clicked_region_state()
        if clicked_region:
            with reactive.isolate():
                current_regions = list(input.input_region() or [])
            
            if clicked_region in current_regions:
                current_regions.remove(clicked_region)
            else:
                current_regions.append(clicked_region)
                
            ui.update_checkbox_group("input_region", selected=current_regions)
            clicked_region_state.set(None)

    @output
    @render_widget 
    def plot_map():
        data = base_filtered_data()
        active_metric = get_active_metric()
        metric_tooltip_label = "Total Revenue" if active_metric == "total_revenue" else "Total Orders"
        
        if data.empty: 
            return px.choropleth(scope="world", template="plotly_white").update_layout(autosize=True, geo=dict(showcountries=True, countrycolor="White", showocean=True, oceancolor="#E8F4F8"))

        region_summary_data = data.groupby("customer_region", as_index=False)[active_metric].sum()
        map_plot_data = [] 
        selected_regions_list = list(input.input_region() or [])

        for _, row in region_summary_data.iterrows():
            region_name = row["customer_region"]
            metric_value = row[active_metric]
            formatted_value = f"${metric_value:,.2f}" if active_metric == "total_revenue" else f"{metric_value:,.0f}"

            if region_name in REGION_COUNTRY_MAPPING:
                for country in REGION_COUNTRY_MAPPING[region_name]:
                    map_plot_data.append({
                        "Country": country, 
                        "Region": region_name, 
                        metric_tooltip_label: formatted_value
                    })
        
        if not map_plot_data: 
            return px.choropleth(scope="world", template="plotly_white").update_layout(autosize=True, geo=dict(showcountries=True, countrycolor="White", showocean=True, oceancolor="#E8F4F8"))

        map_df = pd.DataFrame(map_plot_data)
        
        fig = px.choropleth(
            map_df, locations="Country", locationmode="country names", 
            color="Region", hover_name="Region", 
            custom_data=["Region"], 
            hover_data={"Country": False, "Region": False, metric_tooltip_label: True},
            scope="world", template="plotly_white"
        )
        
        fig.update_geos(showcountries=True, countrycolor="White", showocean=True, oceancolor="#E8F4F8", projection_type="equirectangular")
        
        fig.update_layout(
            autosize=True, 
            margin={"r":0,"t":0,"l":0,"b":0}, 
            dragmode=False, 
            clickmode="event", 
            showlegend=False
        )
        
        for trace in fig.data:
            if trace.name not in selected_regions_list:
                trace.marker.opacity = 0.2
            else:
                trace.marker.opacity = 1.0

        figure_widget = go.FigureWidget(fig)
        
        def handle_map_click(trace, points, state):
            if points.point_inds:
                clicked_region_state.set(trace.customdata[points.point_inds[0]][0])
                
        for trace in figure_widget.data:
            trace.on_click(handle_map_click)
            
        return figure_widget
    
    # --- Plot: Seasonality ---
    @output
    @render_widget
    def plot_season():
        data = fully_filtered_data()
        active_metric = get_active_metric()
        
        if data.empty: 
            return px.bar(title="No data to display", template="plotly_white").update_layout(autosize=True, xaxis_visible=False, yaxis_visible=False)

        season_df = data.copy()
        order_months = season_df["order_date"].dt.month
        
        season_df["season"] = np.select(
            [order_months.isin([12, 1, 2]), order_months.isin([3, 4, 5]), order_months.isin([6, 7, 8]), order_months.isin([9, 10, 11])], 
            ["Winter", "Spring", "Summer", "Fall"], 
            default="Unknown"
        )

        season_summary_data = season_df.groupby(["season", "product_category"], as_index=False)[active_metric].sum()
        season_summary_data["season"] = pd.Categorical(season_summary_data["season"], ["Winter", "Spring", "Summer", "Fall"], ordered=True)
        season_summary_data = season_summary_data.sort_values(["season", "product_category"])

        fig = px.bar(season_summary_data, x="season", y=active_metric, color="product_category", barmode="group", template="plotly_white")
        
        y_axis_label = "Revenue ($)" if active_metric == "total_revenue" else "Units"
        
        fig.update_layout(
            autosize=True, 
            xaxis_title="Season", 
            yaxis_title=y_axis_label, 
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(font=dict(size=10), title=None)
        )
        
        if active_metric == "total_revenue":
            fig.update_yaxes(tickformat="$,.0s", automargin=True)
        else:
            fig.update_yaxes(automargin=True)
            
        fig.update_xaxes(automargin=True)
        return fig

    # --- Plot: Payment Methods ---
    @output
    @render_widget
    def payment_method_bar():
        data = fully_filtered_data()
        active_metric = get_active_metric()
        
        if data.empty: 
            return px.bar(title="No data to display", template="plotly_white").update_layout(autosize=True, xaxis_visible=False, yaxis_visible=False)

        payment_summary_data = data.groupby("payment_method", as_index=False)[active_metric].sum().sort_values(active_metric, ascending=False)
        
        fig = px.bar(payment_summary_data, x="payment_method", y=active_metric, color="payment_method", template="plotly_white")
        
        y_axis_label = "Revenue ($)" if active_metric == "total_revenue" else "Units"
        
        fig.update_layout(
            autosize=True, 
            xaxis_title="Payment Method", 
            yaxis_title=y_axis_label, 
            showlegend=False, 
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        if active_metric == "total_revenue":
            fig.update_yaxes(tickformat="$,.0s", automargin=True)
        else:
            fig.update_yaxes(automargin=True)
            
        fig.update_xaxes(tickangle=0, automargin=True)
        return fig
    
    # --- Dynamic UI Headers ---
    @output
    @render.ui
    def trend_header(): 
        metric_label = "Revenue" if input.input_metric() == "total_revenue" else "Quantity"
        return ui.card_header(f"{metric_label} Trends by Category")

    @output
    @render.ui
    def season_header(): 
        metric_label = "Revenue" if input.input_metric() == "total_revenue" else "Quantity"
        return ui.card_header(f"Total {metric_label} by Season")

    @output
    @render.ui
    def payment_header(): 
        metric_label = "Revenue" if input.input_metric() == "total_revenue" else "Quantity"
        return ui.card_header(f"{metric_label} by Payment Method")

app = App(app_ui, server)