# DSCI-532_2026_28_appname

This interactive Amazon Sales Dashboard enables users to explore sales performance across time, product categories, customer regions, and payment methods through dynamic filters and visualizations. Key performance indicators (KPIs), trend analysis, and comparative charts provide insights into revenue, quantity sold, and average order value. The dashboard is designed to support data-driven decision-making through clear and responsive visual analytics.

## Environment Setup

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

## Running the Dashboard Locally

1. Run the app from the project root:

    ```bash
    shiny run src/app.py
    ```

2. Open the URL shown in the terminal (e.g., `http://127.0.0.1:8000`) in your browser to access the dashboard.

## Data Source

The dataset used in this project is the *Amazon Sales Dataset* from Kaggle:  
https://www.kaggle.com/datasets/aliiihussain/amazon-sales-dataset/data
