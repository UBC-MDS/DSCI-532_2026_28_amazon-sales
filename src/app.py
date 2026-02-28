from shiny import App, ui, reactive, render
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

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

        fig, ax = plt.subplots(figsize=(9, 4))
        for cat, g in by_cat.groupby("product_category"):
            ax.plot(g["month_start"], g[metric], marker="o", linewidth=1, label=str(cat))

        if input.input_aggregate():
            overall = d2.groupby("month_start", as_index=False)[metric].sum().sort_values("month_start")
            ax.plot(overall["month_start"], overall[metric], linewidth=2, label="Aggregate")

        ax.set_title("Monthly Trend by Category")
        ax.set_xlabel("Month")
        ax.set_ylabel("Revenue" if metric == "total_revenue" else "Quantity Sold")
        ax.tick_params(axis="x", rotation=45)
        ax.legend(loc="best", fontsize=8)
        fig.tight_layout()
        return fig

    # --- "Map" placeholder (reactive summary by region) ---
    @output
    @render.plot
    def plot_map():
        d = filtered_df()
        metric = _metric_col()

        fig, ax = plt.subplots(figsize=(6, 4))
        if d.empty:
            ax.set_title("Sales by Region")
            ax.text(0.5, 0.5, "No data for selected filters", ha="center", va="center")
            ax.axis("off")
            return fig

        region_summary = (
            d.groupby("customer_region", as_index=False)[metric]
             .sum()
             .sort_values(metric, ascending=True)
        )

        ax.barh(region_summary["customer_region"], region_summary[metric])
        ax.set_title("Sales by Region")
        ax.set_xlabel("Revenue" if metric == "total_revenue" else "Quantity Sold")
        fig.tight_layout()
        return fig

    # --- Season plot (reactive; shown only when input_season is ON in UI) ---
    @output
    @render.plot
    def plot_season():
        d = filtered_df()
        metric = _metric_col()

        fig, ax = plt.subplots(figsize=(8, 4))
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

        ax.set_xticks(x + width * (len(cats) - 1) / 2 if len(cats) else x)
        ax.set_xticklabels(seasons)
        ax.set_title("Average Sales by Season")
        ax.set_ylabel("Avg Revenue" if metric == "total_revenue" else "Avg Quantity Sold")
        ax.legend(fontsize=8)
        fig.tight_layout()
        return fig

    # --- Payment method bar (reactive) ---
    @output
    @render.plot
    def payment_method_bar():
        d = filtered_df()

        fig, ax = plt.subplots(figsize=(6, 4))
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
        ax.set_title("Revenue by Payment Method")
        ax.set_ylabel("Revenue")
        ax.tick_params(axis="x", rotation=20)
        fig.tight_layout()
        return fig


app = App(app_ui, server)