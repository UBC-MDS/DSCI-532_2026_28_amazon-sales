# Amazon Sales Dashboard

This interactive Amazon Sales Dashboard enables users to explore sales performance across time, product categories, customer regions, and payment methods through dynamic filters and visualizations. Key performance indicators (KPIs), trend analysis, and comparative charts provide insights into revenue, quantity sold, and average order value. The dashboard is designed to support data-driven decision-making through clear and responsive visual analytics.

## Live App

- **Stable version:** https://019ca71b-1cff-0f9a-8c6a-09744690589a.share.connect.posit.cloud/
- **Preview version:** https://019c9c06-2d43-6775-4b46-85423c0e732c.share.connect.posit.cloud/

## Motivation

Business stakeholders often need to monitor revenue trends, compare regional performance, and evaluate category-level sales over time. This dashboard enables users to:

- Track total revenue, orders, and average order value
- Compare monthly trends across product categories
- Analyze sales by region
- Explore the impact of payment methods
- Interactively filter data to support targeted insights

## Demo

![Dashboard Demo](img/demo.gif)

The demo above shows a full interaction cycle: adjusting filters and observing reactive updates across KPIs and visualizations.

## Key Features

- Reactive filtering by time, region, category, and payment method
- KPI value boxes summarizing performance
- Trend analysis visualizations
- Comparative regional charts
- Clean and responsive dashboard layout

## Tech Stack

- Shiny for Python
- Plotly
- Pandas
- Conda environment management
- Posit Connect Cloud deployment

## For Users

Simply visit the **stable deployment link** above to explore the dashboard (No installation required)

## For Contributors

### Environment Setup

1. Clone this repository:

    ```bash
    git clone https://github.com/UBC-MDS/DSCI-532_2026_28_amazon-sales.git
    cd DSCI-532_2026_28_amazon-sales
    ```

2. Create a conda environment based on the provided `environment.yml` file:

    ```bash
    conda env create --file environment.yml
    ```

3. Activate the environment:

    ```bash
    conda activate amazon-sales-dashboard
    ```

### Running the Dashboard Locally

1. Run the app from the project root:

    ```bash
    shiny run src/app.py
    ```

2. Open the URL shown in the terminal (e.g., `http://127.0.0.1:8000`) in your browser to access the dashboard.

For contribution guidelines and development workflow details, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Data Source

- Dataset: Amazon Sales Dataset
- Source: Kaggle
- Link: https://www.kaggle.com/datasets/aliihussain/amazon-sales-dataset
- Stored locally in: `data/raw/amazon_sales_dataset.csv`
- Size: ~4.2 MB

The dataset is included in the repository for reproducibility. No external download is required.
