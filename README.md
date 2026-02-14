# DSCI-532_2026_28_appname

## Environment Setup

1. Clone this repository:

    ```bash
    git clone https://github.com/UBC-MDS/DSCI-532_2026_28_appname.git
    cd DSCI-532_2026_28_appname
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

2. Open the URL shown in the terminal (e.g., `http://127.0.0.1:8000`) in your browser.
