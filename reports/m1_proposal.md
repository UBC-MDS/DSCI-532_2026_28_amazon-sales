# Project Proposal: Amazon Sales Intelligence Dashboard

## Section 1: Motivation and Purpose

**Target Audience:** I am acting as a **Lead Data Consultant** for an **Amazon Third-Party Seller**. My primary audience is the business owner and their inventory management team.

**Problem:** The company currently lacks clear insight into regional and seasonal demand patterns. This data gap leads to a cycle of **overstocking** (wasted capital and high storage fees) or **understocking** (lost revenue and damaged search rankings). Without data-driven forecasting, the business suffers from inconsistent cash flow and unpredictable profit margins.

**Solution:** The proposed dashboard will transform historical Amazon sales data into a strategic planning tool. By visualizing trends of quantity or revenue across **Regions**, **Categories**, and **Order Dates**, the dashboard will help the user synchronize procurement with seasonal peaks and optimize stock distribution to maximize profit.

## Section 2: Description of the Data

### Dataset Overview

The dataset contains 50,000 rows and 13 columns. Each row represents an individual Amazon order record.

The dataset includes: - Order information (`order_id`, `order_date`) - Product details (`product_id`, `product_category`, `price`, etc) - Sales performance (`quantity_sold`, `total_revenue`, `rating`, `review_count`) - Customer & transaction info (`customer_region`, `payment_method`)

The data spans from December 31, 2021 to December 30, 2023 based on the `order_date`, covering approximately three years. The geographic scope is defined by the `customer_region`, including regions such as Asia, North America, Middle East, and Europe.

### Relevance to the Problem

Relevant variables include `order_date`, which helps identify how demand changes over time, including yearly and seasonal patterns. They also include `customer_region` for analyzing regional differences and `product_category` for tracking performance across product groups. In addition, `quantity_sold` and `total_revenue` measure actual demand.

## Section 3: Research Questions & Usage Scenarios

### Personas

| Persona | Role | Focus | Dashboard Feature |
|:---|:---|:---|:---|
| **Seasonal Planner** | Inventory Manager | Ordering the right stock for peaks | **Seasonal Sub-plots** |
| **Regional Lead** | Logistics Manager | Moving stock to the busiest warehouses. | **Regional Map** |
| **Strategy Director** | Product Lead | Spotting long-term growth for new products. | **Main Trend Chart** |

### Usage Scenarios

**Scenario 1:**

The Seasonal Planner needs to order stock for the ski season. They select "Winter" in the Season Selector. The Seasonal Bar Chart shows them exactly how many units sold last year, so they know how much to buy. The Pie Chart confirms that winter is their biggest sales season, justifying a larger budget.

**Scenario 2:**

The Regional Lead sees the "Asia" warehouse is empty. They click "Asia" on the Region Filter. The Seasonal Bar Chart confirms demand is high there. They check the "Europe" region and see low demand. They immediately move stock from "Europe" to "Asia" to prevent running out.

**Scenario 3:**

The Strategy Director wants to know if "Electronics" is a dying category. They look at the Main Trend Chart at the top. It shows a steady decline over 3 years. They decide to stop investing in electronics and focus on growing categories instead.

### User Stories / Jobs to be Done (JTBD)

1.  **Smart Ordering:** As an inventory manager, I want to see **Quantity Sold** for a specific season so I don't overstock or understock.
2.  **Location Tracking:** As a logistics lead, I want to filter sales by **Region** so I can put inventory closer to the customers who buy it.
3.  **Trend Spotting:** As a director, I want to see the **Total Sales** trend over several years so I can identify which products are actually growing.

## Section 4: Exploratory Data Analysis

To address **User Story 3 (Trend Spotting)**, we analyzed total monthly sales across product categories for 2022–2023.

### Analysis

The time-series visualization in `notebooks/eda_analysis.ipynb` shows that while average monthly sales levels are relatively similar across categories (approximately **\$225k–\$231k per month**), volatility differs noticeably.

For example:

-   **Sports** and **Home & Kitchen** exhibit higher month-to-month fluctuations.
-   **Books** remains comparatively more stable over time.
-   Seasonal peaks are visible across multiple categories, confirming that demand varies throughout the year.

### Reflection

These findings support the inclusion of a **multi-category trend visualization** in the dashboard.

By enabling the *Strategy Director* to view category performance over time, the dashboard allows identification of:

-   Seasonal demand patterns\
-   Relative category stability\
-   Potential performance shifts

This confirms that the dataset contains sufficient temporal variation to justify a dynamic time-series component for strategic decision-making.

## Section 5: App Sketch & Description

### Dashboard Sketch

![Sketch](../img/sketch.png)

### Interface Description: Control Impact Matrix

The following table outlines the interaction logic for each dashboard control and which specific visualizations are updated upon selection.

| Control | Affects |
|:---|:---|
| **Time Slider** | KPI Section, Trend Chart, Sales by Region (Map), Average Sales by Season, Revenue by Payment Method |
| **Category** (Multi-select, Max 3) | KPI Section, Trend Chart, Sales by Region (Map), Average Sales by Season, Revenue by Payment Method |
| **Region** (Multi-select) | KPI Section, Trend Chart, Sales by Region (Map), Average Sales by Season, Revenue by Payment Method |
| **Metric** (Revenue / Quantity / Avg Order) | Trend Chart, Sales by Region (Map) |
| **3-Month Rolling Average** | Trend Chart (Only) |

------------------------------------------------------------------------

### Interaction Logic

The dashboard is designed with a **Top-Down** discovery flow. Users set high-level parameters (Metric, Category, Timeframe) at the top to see the "Big Picture" before using specific selectors to drill down into seasonal and regional performance.

**The 9 Functional Components:**

1.  **Category Dropdown:** Filters the entire dashboard to specific product categories (e.g., *Fashion* & *Beauty*).
2.  **Metric Switch:** A toggle to update charts between `quantity_sold` (Logistics View), `total_revenue` (Financial View), or `avg_order_value`.
3.  **Timeframe Slider:** Sets the specific date range for the analysis (e.g., "2022–2025").
4.  **Main Trend Chart:** A bar/line chart showing the trend of the selected Metric and Category over time. Includes a **3-Month Rolling Average** toggle to smooth out volatility.
5.  **Season Selector:** Filters the bottom-row visualizations to focus on specific time segments (e.g., *Winter*).
6.  **Region Selector:** Filters the dashboard to focus on specific geographic areas (e.g., *Asia*).
7.  **Average Sales by Season (Bar):** Compares performance across different times of the year to identify peak demand.
8.  **Revenue by Payment Method (Pie):** Breaks down transaction types, assisting in financial reconciliation and payment preference analysis.
9.  **Regional Map:** A geographic heatmap visualizing the density of the selected Metric and Category across the globe.
