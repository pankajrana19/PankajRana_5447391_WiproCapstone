# features/environment.py
"""
Behave environment hooks — replaces conftest.py.
Runs before/after each scenario (equivalent to pytest fixture scope="function").
"""

import os

from pages.home_page import HomePage
from utils.driver_factory import get_driver
from utils.logger import get_logger
from utils.screenshot import take_screenshot

logger = get_logger("environment")


def before_all(context):
    """
    Runs once before the entire test suite.
    Sets up any suite-level configuration.
    """
    logger.info("=" * 60)
    logger.info("Best Buy BDD Test Suite starting …")
    logger.info("=" * 60)

    # Ensure output directories exist
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("reports/allure-results", exist_ok=True)


def before_scenario(context, scenario):
    """
    Runs before each scenario — equivalent to pytest driver fixture setup.
    Creates a fresh WebDriver, opens Best Buy, handles country modal.
    """
    logger.info("=" * 60)
    logger.info(f"Starting scenario: {scenario.name}")
    logger.info("=" * 60)

    # Create WebDriver — set headless=False to watch, True for silent
    context.driver = get_driver(headless=False)

    # Open Best Buy and handle country modal / feedback popup
    home = HomePage(context.driver)
    home.open_bestbuy()

    logger.info("Browser ready — Best Buy homepage loaded.")


def after_scenario(context, scenario):
    """
    Runs after each scenario — equivalent to pytest driver fixture teardown.
    Takes screenshot on pass/fail, then quits the driver.
    """
    driver = getattr(context, "driver", None)

    if driver is None:
        return

    scenario_name = scenario.name.replace(" ", "_").replace("/", "-")

    if scenario.status == "failed":
        logger.error(f"SCENARIO FAILED: {scenario.name}")
        take_screenshot(driver, scenario_name, status="fail")
    elif scenario.status == "passed":
        logger.info(f"SCENARIO PASSED: {scenario.name}")
        take_screenshot(driver, scenario_name, status="pass")

    logger.info("Tearing down WebDriver …")
    driver.quit()
    logger.info("WebDriver closed.")


def after_all(context):
    logger.info("=" * 60)
    logger.info("Best Buy BDD Test Suite complete.")
    logger.info("=" * 60)
