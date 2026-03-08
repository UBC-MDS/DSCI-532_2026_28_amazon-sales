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