# conftest.py

import pytest

from utils.driver_factory import get_driver
from utils.screenshot import take_screenshot
from utils.logger import get_logger
from pages.home_page import HomePage

logger = get_logger("conftest")


# ── Driver fixture ─────────────────────────────────────────────────── #

@pytest.fixture(scope="function")
def driver():
    """
    Provides a fresh WebDriver instance for each test.
    Automatically opens Best Buy and selects United States.
    Captures a screenshot and quits the driver after every test.

    Set headless=False below to watch the browser run during debugging.
    Set headless=True for faster, silent execution (may trigger bot checks).
    """
    logger.info("=" * 60)
    logger.info("Setting up WebDriver …")

    # headless=False — visible browser; more reliable against bot detection
    # headless=True  — no UI window; faster but Best Buy may block it
    web_driver = get_driver(headless=False)

    # Open Best Buy and handle the country selector
    home = HomePage(web_driver)
    home.open_bestbuy()

    yield web_driver

    # ── Teardown ──────────────────────────────────────────────────── #
    logger.info("Tearing down WebDriver …")
    web_driver.quit()
    logger.info("WebDriver closed.")


# ── Screenshot on failure hook ─────────────────────────────────────── #

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):  # noqa: ANN001 — pytest hook signature
    outcome = yield
    report = outcome.get_result()

    # Attach screenshot to Allure for both PASS and FAIL
    if report.when == "call":
        web_driver = item.funcargs.get("driver")
        if web_driver is None:
            return

        test_name = item.name
        if report.failed:
            logger.error(f"TEST FAILED: {test_name}")
            take_screenshot(web_driver, test_name, status="fail")
        elif report.passed:
            logger.info(f"TEST PASSED: {test_name}")
            take_screenshot(web_driver, test_name, status="pass")
