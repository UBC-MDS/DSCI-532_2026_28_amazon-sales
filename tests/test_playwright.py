from shiny.playwright import controller
from shiny.run import ShinyAppProc
from shiny.pytest import create_app_fixture
from playwright.sync_api import Page, expect
from pathlib import Path

APP_PATH = Path(__file__).resolve().parents[1] / "src" / "app.py"
app = create_app_fixture(APP_PATH)

def get_checked_values(page: Page, input_name: str) -> list[str]:
    """Return the currently selected values of a checkbox group input."""
    return page.locator(f'input[name="{input_name}"]:checked').evaluate_all(
        "els => els.map(el => el.value)"
    )
    
def test_year_filter_selection_changes(page: Page, app: ShinyAppProc) -> None:
    """Selecting a single year updates the year checkbox selection."""
    page.goto(app.url)

    year_input = controller.InputCheckboxGroup(page, "input_year")

    year_input.set(["2023"])

    years = get_checked_values(page, "input_year")
    assert years == ["2023"]


def test_region_filter_updates_dashboard_outputs(page: Page, app: ShinyAppProc) -> None:
    """Selecting one region limits the dashboard summaries to the chosen region."""
    page.goto(app.url)

    region_input = controller.InputCheckboxGroup(page, "input_region")
    revenue_box = page.locator("#valuebox_revenue")
    orders_box = page.locator("#valuebox_orders")

    revenue_before = revenue_box.inner_text()
    orders_before = orders_box.inner_text()

    region_input.set(["Asia"])

    expect(revenue_box).not_to_have_text(revenue_before)
    expect(orders_box).not_to_have_text(orders_before)

def test_season_switch_toggle(page: Page, app: ShinyAppProc) -> None:
    """The season switch input can be toggled on and off."""
    page.goto(app.url)

    season_input = controller.InputSwitch(page, "input_season")

    season_input.expect_checked(True)
    season_input.set(False)
    season_input.expect_checked(False)
    season_input.set(True)
    season_input.expect_checked(True)

def test_metric_filter_updates_selection(page: Page, app: ShinyAppProc) -> None:
    """Selecting a different metric updates the radio button input."""
    page.goto(app.url)

    metric_input = controller.InputRadioButtons(page, "input_metric")

    metric_input.expect_selected("total_revenue")
    metric_input.set("order_id")
    metric_input.expect_selected("order_id")

def test_reset_button_restores_defaults(page: Page, app: ShinyAppProc) -> None:
    """Clicking reset restores year and region filters to default selections."""
    page.goto(app.url)

    year_input = controller.InputCheckboxGroup(page, "input_year")
    region_input = controller.InputCheckboxGroup(page, "input_region")

    year_input.set(["2023"])
    region_input.set(["Asia"])

    page.locator("#reset_btn").click()

    years = get_checked_values(page, "input_year")
    regions = get_checked_values(page, "input_region")

    assert "2023" in years
    assert "Asia" in regions

def test_metric_change_updates_valuebox(page: Page, app: ShinyAppProc) -> None:
    """Changing the metric updates the value box output."""
    page.goto(app.url)

    metric_input = controller.InputRadioButtons(page, "input_metric")
    value_box = page.locator("#valuebox_revenue")

    value_before = value_box.inner_text()

    metric_input.set("order_id")

    expect(value_box).not_to_have_text(value_before)