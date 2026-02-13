# Project Proposal: Amazon Sales Intelligence Dashboard

## Section 1: Motivation and Purpose

**Target Audience:** I am acting as a **Lead Data Consultant** for an **Amazon Third-Party Seller**. My primary audience is the business owner and their inventory management team.

**Problem:** The company currently lacks clear insight into regional and seasonal demand patterns. This data gap leads to a cycle of **overstocking** (wasted capital and high storage fees) or **understocking** (lost revenue and damaged search rankings). Without data-driven forecasting, the business suffers from inconsistent cash flow and unpredictable profit margins.

**Solution:** The proposed dashboard will transform historical Amazon sales data into a strategic planning tool. By visualizing trends across **Regions**, **Categories**, and **Order Dates**, the dashboard will help the user synchronize procurement with seasonal peaks and optimize stock distribution to maximize profit.

## Section 2: Description of the Data

Place holder

## Section 3: Research Questions & Usage Scenarios

rubric={reasoning:10}

### Personas

| Persona | Role | Focus | Dashboard Feature |
|:-----------------|:-----------------|:-----------------|:-----------------|
| **Seasonal Planner** | Inventory Manager | Ordering the right stock for peaks | **Seasonal Sub-plots** (Bottom Left/Middle) |
| **Regional Lead** | Logistics Manager | Moving stock to the busiest warehouses. | **Regional Map** (Bottom Right) |
| **Strategy Director** | Product Lead | Spotting long-term growth for new products. | **Main Trend Chart** (Top Row) |

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

Place holder

## Section 5: App Sketch & Description

### Dashboard Sketch

![Sketch](../img/sketch.png)

### Interface Description

### Interaction Logic

-   The user sets the top filters `Metric`, `Catergory` and Timeframe to see the "Big Picture."
-   They then use the `Season` and `customer_region` selectors at the bottom to drill down (e.g., "Show me the *Revenue* for *Winter* in the *North* region").

**The 9 Functional Components:**

1.  **Category Dropdown:** Filters the entire dashboard to a specific `product_category` (e.g., `Fashion` & `Beauty`).
2.  **Metric Switch:** A dropdown to toggle all charts between `quantity_sold` (Logistics View) and `total_revenue` (Financial View).
3.  **Timeframe Slider:** Sets the specific year range for the analysis (e.g., "2022-2025").
4.  **Main Trend Chart (Top):** A broad bar chart showing the trend of the selected `Metric` and `Catergory` over the selected `Timeframe`.
5.  **Season Selector:** Filters the bottom row to focus on a specific `Season` (e.g., "Summer").
6.  **Region Selector:** Filters the bottom row to focus on a specific `customer_region` (e.g., "Asia").
7.  **Seasonal Sub-plots (Bar):** Shows the exact Quantity/Revenue for the selected season.
8.  **Seasonal Sub-plots (Pie):** Shows the selected season's contribution % to the yearly total.
9.  **Regional Map:** Visualizes the geographic density of the selected `Metric`, `Catergory`, `Season` and `customer_region`.

### 
