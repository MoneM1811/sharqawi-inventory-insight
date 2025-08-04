# Copilot Instructions for Sharqawi Reporting System

## Project Overview
This is a Streamlit-based reporting dashboard for Sharqawi Air Distribution Factory. The main entry point is `Reporting_System_3.py`, which orchestrates UI rendering and report selection. The project is modular, with reporting logic split into `modules/production.py` and `modules/sales.py`.

## Architecture & Data Flow
- **Main UI**: `Reporting_System_3.py` sets up the Streamlit page, sidebar navigation, and header/footer.
- **Report Modules**: The `modules` directory contains separate files for each report type. Each module exposes a `render_*` function (e.g., `render_production_report`, `render_sales_reports`) called from the main file based on sidebar selection.
- **Assets**: Images (e.g., `sharqawi_logo.png`) are loaded directly in the UI code.
- **External Dependencies**: Uses `streamlit` for UI and `PIL` for image handling. All other logic is custom.

## Developer Workflows
- **Run Locally**: Use `streamlit run Reporting_System_3.py` from the project root.
- **Debugging**: Modify the main file or modules and rerun the Streamlit app. No custom build or test scripts are present.
- **Adding Reports**: To add a new report type:
  1. Create a new module in `modules/` with a `render_*` function.
  2. Add the report name to the sidebar radio in `Reporting_System_3.py`.
  3. Call the new module's render function in the section logic.

## Project-Specific Patterns
- **Sidebar Navigation**: All report selection is handled via `st.sidebar.radio`. Each option maps to a module function.
- **UI Styling**: Uses inline HTML/CSS in markdown for custom headers.
- **Author Footer**: Standardized author info in the sidebar.
- **No Database/Backend**: All data handling is presumed to be in-memory or loaded within modules (not shown in main file).

## Example: Adding a New Report
```python
# In Reporting_System_3.py
section = st.sidebar.radio("Choose a report:", ["Production Reports", "Sales Reports", "Inventory Reports"])
if section == "Inventory Reports":
    inventory.render_inventory_report()
```

## Key Files
- `Reporting_System_3.py`: Main UI and routing logic
- `modules/production.py`, `modules/sales.py`: Report logic
- `sharqawi_logo.png`: Logo asset

## Conventions
- All report modules should expose a `render_*` function for UI integration.
- UI changes should be made in the main file; business logic in modules.
- Use Streamlit's markdown and layout primitives for UI consistency.

---
For questions or unclear patterns, review the main file and modules for examples. Update this guide as new workflows or conventions emerge.
