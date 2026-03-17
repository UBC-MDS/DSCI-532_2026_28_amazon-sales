## [0.4.0] - 2026-03-17

### Added
- Integrated DuckDB to execute filtered queries directly on Parquet data
- Converted dataset from CSV to Parquet format to improve performance and reduce I/O overhead
- Implemented interactive map feature where clicking a region dynamically filters the dashboard
- Added Playwright tests to validate key user interactions, including:
  - year filter selection
  - region filtering impact on dashboard outputs
  - season toggle behavior
  - metric selection updates
  - reset button restoring defaults
  - value box updates on metric change
- Added pytest unit tests for `get_metric_info` to validate:
  - correct configuration for revenue and order metrics
  - presence of required keys
  - fallback behavior for unknown metrics

### Changed
- Refactored dashboard filtering logic to use DuckDB queries instead of pandas filtering
- Updated environment configuration (`environment.yml`) to include DuckDB and Parquet dependencies
- Improved AI Assistant interface by adding scrollable chat history and clearer conversation display
- Improved map logic to ensure consistent rendering of all regions and allow interaction-based filtering
- Updated [CONTRIBUTING.md](CONTRIBUTING.md) with M3 retrospective and M4 collaboration improvements
- Addressed peer feedback from 4 reviewers by creating and prioritizing GitHub issues (M4 Feedback Prioritization), including improvements to:
  - bar chart readability (grouped bars instead of stacked where appropriate)
  - handling of empty filtered datasets across visualizations
  - UI clarity and labeling
  - overall dashboard usability and consistency

### Fixed
- Fixed issues with empty dataset handling causing plots to break
- Fixed inconsistencies in region filtering between map and dashboard outputs

- **Feedback prioritization issue link:**  [#105](https://github.com/UBC-MDS/DSCI-532_2026_28_amazon-sales/issues/105)

### Known Issues
- Map selection and sidebar filters may briefly appear out of sync until all reactive components update; an optional "Apply" button for filters (suggested by instructor) could improve synchronization.

### Release Highlight: Interactive Map Filtering

This release introduces an interactive map feature where users can click on a region to dynamically filter the entire dashboard. This improves usability by enabling intuitive geographic exploration and tighter integration between visual components.

- **Option chosen:** D (Component click event interaction)
- **PR:** Implemented during Milestone 3 as part of dashboard interaction development (no dedicated PR)
- **Why this option over the others:** This option directly improves user interaction within the dashboard by turning a visualization into an input mechanism, making exploration more intuitive without adding additional UI complexity
- **Feature prioritization issue link:**  [#120](https://github.com/UBC-MDS/DSCI-532_2026_28_amazon-sales/issues/120)

### Collaboration
- **CONTRIBUTING.md:** Updated via [PR](https://github.com/UBC-MDS/DSCI-532_2026_28_amazon-sales/pull/116) to include M3 retrospective and M4 workflow improvements
- **M3 retrospective:** The team experienced issues merging from `dev` to `main`, which caused delays and highlighted the need for a more structured workflow
- **M4:** Adopted feature branches, scoped pull requests, peer reviews, and issue-based task tracking to improve coordination and reduce merge conflicts

### Reflection
**What the dashboard does well**
- Transitioning to DuckDB significantly improved scalability and performance by pushing filtering logic into the query layer
- Implementing Playwright tests improved confidence in UI behavior and ensured core interactions worked as expected
- Introducing interactive map filtering enhanced user experience by enabling intuitive geographic exploration
- Improving the AI Assistant interface (including scrollable chat history) enhanced usability and made interactions more intuitive
- Organizing peer feedback into structured GitHub issues improved team coordination and clarity of implementation

**Current limitations**
- Some reactive components (e.g., map and sidebar filters) may briefly appear out of sync due to the absence of an "Apply" mechanism for filters

**Trade-offs and learning**
- Trade-off: Prioritized critical feedback affecting usability and correctness, while deferring minor UI enhancements due to time constraints
- Most useful learning: Concepts from reactive programming and dashboard design (DSCI 531) were particularly valuable in structuring the app logic and ensuring consistent interactions across components
- Updating the collaboration workflow [CONTRIBUTING.md](CONTRIBUTING.md) helped reduce merge conflicts and improved team efficiency

## [0.3.0] - 2026-03-08

### Added
- Added an AI-powered tab with a QueryChat interface.
- Added a dataframe output component to display the query-filtered results.
- Added two visualizations based on the AI query-filtered dataframe.
- Added a download button to export the filtered dataframe.
- Added a reset button to clear all selections.

### Changed
- Set the seasonal plot to display by default.
- Replaced the year input with checkboxes.
- Updated charts to use an interactive plotting library with hover functionality.
- Renamed the metric input to be more intuitive.
- Updated the map style for better visualization.
- Moved and compacted value boxes.
- Allocated more space for the map visualization.
- Added the data link and citation in Section 2 of the proposal.
- Added group number and group name in the About section.

### Fixed
- Fixed the category selector issue where all categories appeared when none were selected.
- Fixed the aggregated trend line color so it remains consistent when categories change.

### Reflection

In this milestone, we extended the dashboard by integrating an AI-powered tab that allows users to interact with the dataset using natural language queries. This feature provides a more flexible way to explore the data compared to traditional dashboard filters. Users can generate filtered datasets through the AI interface and immediately visualize the results with interactive charts.

In addition to the AI functionality, we improved the usability of the dashboard by refining the layout, adding clearer input controls (such as checkbox selection for years), and improving the map and chart interactions. Using an interactive plotting library also enhanced the user experience by enabling hover tooltips and more responsive visualizations.

Through this milestone, we gained experience integrating LLM-based features into an interactive data application and learned how to balance AI-driven exploration with structured dashboard components. This process also highlighted the importance of clear UI design and careful handling of AI-generated outputs to maintain a consistent and reliable user experience.
## [0.2.0] - 2026-02-28

### Added
- **Global Sales Map**: Integrated an interactive Plotly Choropleth world map to visualize regional performance (Asia, Europe, Middle East, North America) using distinct categorical colors.
- **Seasonality Analysis**: Added a toggleable seasonal comparison chart to track average sales across Winter, Spring, Summer, and Fall.
- **KPI Value Boxes**: Implemented dynamic `ui.value_box()` components for Total Revenue and Total Orders to provide immediate context.
- **Metric Toggle**: Added a radio button to switch the entire dashboard's primary metric between "Revenue" and "Quantity Sold".
- **Footer**: Added a dashboard footer containing the app description, author credits, and a link to the GitHub repository.
- **Dependencies**: Added `plotly`, `shinywidgets`, and `anywidget` to `environment.yml` to support the new geographic visualization.

### Changed
- **Input Components**: Switched the "Month" and "Region" inputs from checkbox/slider groups to `ui.input_selectize()` dropdowns.
  - *Rationale*: Sliders force consecutive selections and are not circular. `Selectize` allows the flexibility needed for our core "Ski Season" job story, which requires selecting months that wrap around the calendar year. It also prevents vertical UI bloat in the sidebar.
- **Map Architecture**: Completely replaced the original M1 layout's Matplotlib regional bar chart placeholder with a `shinywidgets` Plotly map widget (`render_widget`).
  - *Rationale*: A map provides immediate, intuitive spatial context that a bar chart lacks. By using a categorical color scale and locking the zoom, it adheres to the 5-second rule and keeps the dashboard looking intentional.
- **KPI Layout**: Replaced standard text cards from the M2 spec with `ui.value_box()` for KPIs.
  - *Rationale*: Value boxes are native to modern Shiny UI and provide a much stronger visual hierarchy for primary metrics.

### Fixed
- **Reactivity Bottlenecks**: Refactored the server logic to use a single centralized `@reactive.calc` (`filtered_df()`) to handle all sidebar inputs, ensuring data is only filtered once per input change rather than once per output.
- **Empty State Crashes**: Added defensive safety checks (`if d.empty:` and `if not map_data:`) to the map and plot rendering logic to return blank visualizations instead of crashing when filters yield no data.
- **Missing Widget Dependency**: Resolved the `NameError` and missing `FigureWidget` class errors by correctly initializing the mapping array and installing `anywidget`.

### Known Issues
- **Incomplete Region Mapping**: The map currently is too small and does not include all countries even when all regions are checked, as the countries are mapped to regions manually via a hardcoded dictionary. 
- **Metric Formatting**: The "Quantity Sold" metric in value boxes currently displays with a dollar sign prefix; requires an updated conditional string formatter.

---

## Phase 3 Reflection

### Job Story Implementation Status
* **Fully Implemented**:
  * **Location Tracking (Regional Lead)**: Users can filter sales by *Region* and instantly view the geographic distribution on the interactive map to make logistics decisions (e.g., moving stock to Asia).
  * **Trend Spotting (Strategy Director)**: The Main Trend Chart successfully tracks *Total Sales* over several years. Users can filter by category (e.g., Electronics) to spot long-term growth or decline.

* **Partially Implemented**:
  * **Smart Ordering (Seasonal Planner)**: Users can toggle the primary metric to *Quantity Sold* and view the Seasonal Bar Chart to avoid overstocking. However, the originally planned "Pie Chart" to confirm seasonal budget shares was replaced by more precise bar charts. 

* **Pending M3**:
  * **Dynamic Region Mapping**: The map currently relies on a hardcoded dictionary. We need to explore a more robust, automated method to map all countries to their respective regions so no data is left off the map.
  * **Advanced KPI Formatting**: The "Quantity Sold" metric in value boxes currently displays with a dollar sign prefix; we need to implement a dynamic string formatter that changes based on the metric toggle.