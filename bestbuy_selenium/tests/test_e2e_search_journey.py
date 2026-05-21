# tests/test_e2e_search_journey.py
"""
Best Buy Search Bar — End-to-End Test
=======================================
Flow:
  1.  Open Best Buy homepage
  2.  Select "United States" on the country modal
  3.  Verify home page loaded
  4.  Login with credentials from config/test_data.json
  5.  Verify login succeeded / continue as guest
  6.  Search for the e2e_query from test_data.json
  7.  Verify search results page loaded
  8.  Verify results are returned on page 1
  9.  Add first available item to cart directly from results page
  10. Final summary

All test data loaded from config/test_data.json
"""

import json
import os

import allure

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.logger import get_logger
from utils.screenshot import take_screenshot

logger = get_logger(__name__)

# ── Load test data from JSON ───────────────────────────────────────── #

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "test_data.json"
)

with open(_DATA_PATH, "r", encoding="utf-8") as _f:
    _TD = json.load(_f)

_SEARCH_QUERY = _TD["search"]["e2e_query"]


@allure.feature("End-to-End Search & Cart Journey")
@allure.story("Login → Search → Add to Cart")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title(f"E2E — Login, search for '{_SEARCH_QUERY}', add first available item to cart")
@allure.description(
    "Simulates a real signed-in user: opens Best Buy, selects United States, "
    "logs in using credentials from test_data.json, searches for the e2e_query, "
    "then adds the first available item to cart directly from the results page."
)
class TestE2ESearchJourney:

    def test_e2e_full_search_journey(self, driver):
        """E2E: Open → Select US → Login → Search → Add to Cart."""

        # ── Step 1: Confirm homepage is loaded ─────────────────────── #
        with allure.step("Step 1 — Confirm Best Buy homepage is loaded"):
            home_page   = HomePage(driver)
            search_page = SearchPage(driver)

            assert home_page.is_home_page_loaded(), \
                "Best Buy homepage did not load — search bar not visible."

            current_url = search_page.get_current_page_url()
            page_title  = search_page.get_title()
            logger.info(f"[E2E Step 1] URL: {current_url}")
            logger.info(f"[E2E Step 1] Title: {page_title}")
            take_screenshot(driver, "E2E_01_homepage_loaded", status="pass")

            assert "bestbuy" in current_url.lower() or "bestbuy" in page_title.lower(), \
                f"Not on Best Buy. URL={current_url}, Title={page_title}"

        # ── Step 2: Login ──────────────────────────────────────────── #
        with allure.step("Step 2 — Login with credentials from test_data.json"):
            login_page = LoginPage(driver)
            logger.info("[E2E Step 2] Attempting login …")

            login_success = login_page.login()
            take_screenshot(driver, "E2E_02_after_login", status="info")

            if login_success:
                logger.info("[E2E Step 2] Login succeeded.")
                allure.attach(
                    "Login: SUCCESS",
                    name="Login Status",
                    attachment_type=allure.attachment_type.TEXT,
                )
            else:
                logger.warning(
                    "[E2E Step 2] Login failed — continuing as guest. "
                    "Update email/password in config/test_data.json."
                )
                allure.attach(
                    "Login: SKIPPED (invalid/missing credentials) — running as guest.",
                    name="Login Status",
                    attachment_type=allure.attachment_type.TEXT,
                )
                home_page.open_bestbuy()

        # ── Step 3: Search ─────────────────────────────────────────── #
        with allure.step(f"Step 3 — Search for '{_SEARCH_QUERY}'"):
            logger.info(f"[E2E Step 3] Searching for '{_SEARCH_QUERY}' …")
            search_page.search_for(_SEARCH_QUERY)
            take_screenshot(driver, "E2E_03_search_submitted", status="info")

        # ── Step 4: Verify results page ────────────────────────────── #
        with allure.step("Step 4 — Verify search results page loaded"):
            results_url   = search_page.get_current_page_url()
            results_title = search_page.get_title()
            logger.info(f"[E2E Step 4] URL: {results_url}")
            logger.info(f"[E2E Step 4] Title: {results_title}")
            take_screenshot(driver, "E2E_04_results_page", status="pass")

            assert (
                _SEARCH_QUERY.lower() in results_url.lower()
                or _SEARCH_QUERY.lower() in results_title.lower()
                or search_page.is_on_search_results_page()
            ), f"Not on results page. URL={results_url}"

        # ── Step 5: Verify results on page 1 ──────────────────────── #
        with allure.step("Step 5 — Verify results present on page 1"):
            page1_count  = search_page.get_results_count()
            page1_titles = search_page.get_result_titles()
            logger.info(f"[E2E Step 5] Page 1: {page1_count} results")

            allure.attach(
                "\n".join(page1_titles[:10]) if page1_titles else "No titles found",
                name="Page 1 — first 10 result titles",
                attachment_type=allure.attachment_type.TEXT,
            )
            take_screenshot(driver, "E2E_05_results_present", status="pass")
            assert page1_count > 0, \
                f"No results found for '{_SEARCH_QUERY}' on page 1."

        # ── Step 6: Add first available item to cart ───────────────── #
        with allure.step("Step 6 — Add first available item to cart from results page"):
            logger.info("[E2E Step 6] Adding first available item to cart …")
            added = search_page.add_first_available_to_cart()
            take_screenshot(driver, "E2E_06_add_to_cart_clicked", status="info")

            assert added, \
                "Could not add any item to cart — all items may be sold out or unavailable."

            logger.info("[E2E Step 6] Item added to cart successfully.")
            take_screenshot(driver, "E2E_06_item_added", status="pass")

        # ── Step 7: Final summary ──────────────────────────────────── #
        with allure.step("Step 7 — Final summary"):
            summary = (
                f"Query           : {_SEARCH_QUERY}\n"
                f"Login succeeded : {login_success}\n"
                f"Page 1 results  : {page1_count}\n"
                f"Item added      : {added}\n"
            )
            logger.info(f"\n{'=' * 50}\nE2E SUMMARY\n{summary}\n{'=' * 50}")
            allure.attach(
                summary,
                name="E2E Test Summary",
                attachment_type=allure.attachment_type.TEXT,
            )
            take_screenshot(driver, "E2E_07_journey_complete", status="pass")

        logger.info("E2E TEST PASSED — Login → Search → Add to Cart.")
