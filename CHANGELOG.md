## [0.2.0] - 2026-02-28

### Added
- **Global Sales Map**: Integrated a Plotly Choropleth world map to visualize regional performance with constant zoom and highlighting.
- **Seasonality Analysis**: Added a toggleable seasonal comparison chart to track average sales across Winter, Spring, Summer, and Fall.
- **KPI Value Boxes**: Implemented dynamic `ui.value_box` components for Total Revenue and Total Orders.
- **Metric Toggle**: Added a radio button to switch the entire dashboard between "Revenue" and "Quantity Sold" metrics.
- **Footer**: Added a professional footer with app description, authors, GitHub link, and last updated date.

### Changed
- **Input Types**: Converted Month and Region filters from long checkbox groups to `ui.input_selectize` dropdowns to eliminate "scroll of death" and improve sidebar space management.
- **UI Labels**: Shortened all input labels (e.g., "Select Year Range" to "Years") to comply with the "5-second rule" for intuitive design.
- **Map Implementation**: Replaced the initial Matplotlib bar chart placeholder with a real geographic `shinywidgets` output.

### Fixed
- **Reactivity Bottlenecks**: Implemented a centralized `@reactive.calc` for `filtered_df` to ensure the data is only filtered once per input change rather than once per output.
- **Empty State Handling**: Added defensive checks to the reactive logic to prevent app crashes when no categories or regions are selected.

### Known Issues
- **Metric Formatting**: The "Quantity Sold" metric in value boxes currently displays with a dollar sign prefix; needs a conditional string formatter.
- **Map Labels**: Some custom region names in the dataset may not perfectly align with standard ISO country names in Plotly.

---

## Phase 3 Reflection

### Job Story Implementation Status
* **Fully Implemented**:
    * *High-Level Overview*: Users can filter by years/months to see overall revenue and orders.
    * *Geographic Focus*: Users can filter by region and see performance on a global map.
    * *Seasonality Check*: Users can toggle a comparison of sales spikes across different seasons.
* **Partially Implemented**:
    * *Category Trends*: Users can compare categories to the aggregate, though the "Aggregate" line is currently limited to the Trend Chart.
* **Pending M3 (Milestone 3)**:
    * *AOV Tracking*: The Average Order Value KPI was removed in this phase to prioritize the Revenue/Quantity toggle logic.

### Layout Deviations & Rationale
* **Deviation**: Switched from `input_checkbox_group` to `input_selectize` for Months/Regions.
    * *Rationale*: The original M1/M2 sketches resulted in a sidebar that was too long for standard laptop screens. Selectize dropdowns provide a cleaner UI while maintaining the "multi-select" functionality.
* **Deviation**: Replaced the Regional Bar Chart with a Choropleth Map.
    * *Rationale*: To improve geographic "intentionality." A bar chart showed the numbers but failed to show the spatial relationship between markets, which was a core part of the "Ski Season" job story.
* **Deviation**: Use of `ui.value_box` instead of standard text cards.
    * *Rationale*: Modern Shiny design principles favor `value_box` for KPIs as they provide better visual hierarchy and built-in theming (Primary/Info) compared to the basic cards outlined in M2.