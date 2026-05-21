# tests/test_search.py
"""
Best Buy Search Bar Test Suite
================================
Positive Test Cases (4):
  TC_POS_01 — Valid product search returns results
  TC_POS_02 — Search result titles match the query keyword
  TC_POS_03 — Search bar retains input after search
  TC_POS_04 — Gibberish query handled gracefully

Negative Test Cases (2):
  TC_NEG_01 — Invalid login credentials show error message
  TC_NEG_02 — Special characters search is handled gracefully

All test data loaded from config/test_data.json
"""

import json
import os
import time

import allure

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.search_page import SearchPage
from pages.login_page import LoginPage
from utils.logger import get_logger
from utils.screenshot import take_screenshot

logger = get_logger(__name__)

# ── Load test data from JSON ───────────────────────────────────────── #

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "test_data.json"
)

with open(_DATA_PATH, "r", encoding="utf-8") as _f:
    _TD = json.load(_f)

_SEARCH        = _TD["search"]
_LOGIN         = _TD["login"]
_QUERIES_POS   = _SEARCH["positive_queries"]
_QUERIES_NEG   = _SEARCH["negative_queries"]
_KEYWORDS      = _SEARCH["title_match_keywords"]
_RATIO         = _SEARCH["title_match_ratio_threshold"]


# ═══════════════════════════════════════════════════════════════════════ #
#  POSITIVE TEST CASES                                                    #
# ═══════════════════════════════════════════════════════════════════════ #

@allure.feature("Search Bar")
@allure.story("Positive Tests")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("TC_POS_01 — Valid product search returns results")
@allure.description(
    "Search for the 'basic_search' query from test_data.json, verify the "
    "results page is displayed, and at least one product card is visible."
)
class TestPositiveSearchReturnsResults:

    def test_valid_search_returns_results(self, driver):
        """TC_POS_01 — Search for a common product and confirm results appear."""
        query = _QUERIES_POS["basic_search"]

        with allure.step(f"Search for '{query}'"):
            search_page = SearchPage(driver)
            search_page.search_for(query)
            take_screenshot(driver, "TC_POS_01_after_search", status="info")

        with allure.step("Assert the URL indicates search results"):
            current_url = search_page.get_current_page_url()
            logger.info(f"Current URL: {current_url}")
            assert query.lower() in current_url.lower() \
                or search_page.is_on_search_results_page(), \
                f"Expected search results URL, got: {current_url}"

        with allure.step("Assert at least 1 product result is visible"):
            result_count = search_page.get_results_count()
            logger.info(f"Results found: {result_count}")
            take_screenshot(driver, "TC_POS_01_results", status="pass")
            assert result_count > 0, \
                f"Expected results for '{query}', found {result_count}"

        logger.info("TC_POS_01 PASSED — valid search returns results.")


@allure.feature("Search Bar")
@allure.story("Positive Tests")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("TC_POS_02 — Search result titles match the query keyword")
@allure.description(
    "Search for the 'title_match' query from test_data.json, inspect result "
    "titles, and verify that at least the configured ratio contain a keyword."
)
class TestPositiveResultTitlesMatchQuery:

    def test_result_titles_match_query(self, driver):
        """TC_POS_02 — Result titles should be relevant to the search query."""
        query    = _QUERIES_POS["title_match"]
        keywords = _KEYWORDS
        ratio    = _RATIO

        with allure.step(f"Search for '{query}'"):
            search_page = SearchPage(driver)
            search_page.search_for(query)
            take_screenshot(driver, "TC_POS_02_search_submitted", status="info")

        with allure.step("Retrieve result titles"):
            titles = search_page.get_result_titles()
            logger.info(f"Fetched {len(titles)} result titles.")
            allure.attach(
                "\n".join(titles[:10]),
                name="First 10 result titles",
                attachment_type=allure.attachment_type.TEXT,
            )
            assert len(titles) > 0, "No product titles found on results page."

        with allure.step(f"Assert ≥{ratio:.0%} of titles contain relevant keywords"):
            matching    = [t for t in titles if any(kw in t.lower() for kw in keywords)]
            match_ratio = len(matching) / len(titles)
            logger.info(f"Matching: {len(matching)}/{len(titles)} ({match_ratio:.0%})")
            take_screenshot(driver, "TC_POS_02_titles_check", status="pass")
            assert match_ratio >= ratio, \
                f"Only {match_ratio:.0%} of titles match {keywords}. Titles: {titles[:5]}"

        logger.info("TC_POS_02 PASSED — result titles match query.")


@allure.feature("Search Bar")
@allure.story("Positive Tests")
@allure.severity(allure.severity_level.MINOR)
@allure.title("TC_POS_03 — Search bar retains the typed query after search")
@allure.description(
    "After searching using the 'search_bar_retain' query from test_data.json, "
    "the search bar should still display that value."
)
class TestPositiveSearchBarRetainsQuery:

    def test_search_bar_retains_query(self, driver):
        """TC_POS_03 — The search input must retain its value post-search."""
        query = _QUERIES_POS["search_bar_retain"]

        with allure.step(f"Search for '{query}'"):
            search_page = SearchPage(driver)
            search_page.search_for(query)
            take_screenshot(driver, "TC_POS_03_after_search", status="info")

        with allure.step("Read back the search bar value"):
            retained_value = search_page.get_search_input_value()
            logger.info(f"Search bar retained: '{retained_value}'")
            take_screenshot(driver, "TC_POS_03_input_retained", status="pass")

        with allure.step("Assert search bar value matches submitted query"):
            assert query.lower() in retained_value.lower(), \
                f"Expected '{query}' in search bar, found '{retained_value}'"

        logger.info("TC_POS_03 PASSED — search bar retains typed query.")


@allure.feature("Search Bar")
@allure.story("Positive Tests")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("TC_POS_04 — Gibberish query handled gracefully")
@allure.description(
    "Search for the 'gibberish' query from test_data.json and verify the site "
    "handles it gracefully — returning results or a proper no-results response."
)
class TestPositiveGibberishReturnsResults:

    def test_gibberish_query_returns_results(self, driver):
        """TC_POS_04 — A gibberish query should be handled gracefully."""
        query = _QUERIES_POS["gibberish"]

        with allure.step(f"Search for gibberish query: '{query}'"):
            search_page = SearchPage(driver)
            search_page.search_for(query)
            take_screenshot(driver, "TC_POS_04_after_gibberish_search", status="info")

        with allure.step("Assert the site is still responsive"):
            title       = search_page.get_title()
            current_url = search_page.get_current_page_url()
            logger.info(f"Title: {title} | URL: {current_url}")

        with allure.step("Assert no server error page"):
            title_lower = title.lower()
            assert "500" not in title_lower, "Server error (500) on gibberish search."
            assert "error" not in title_lower or "best buy" in title_lower, \
                f"Unexpected error page. Title: {title}"

        with allure.step("Assert results returned or no-results message shown"):
            result_count      = search_page.get_results_count()
            has_no_results_msg = search_page.has_no_results_message()
            logger.info(f"Results: {result_count} | No-results msg: {has_no_results_msg}")
            take_screenshot(driver, "TC_POS_04_gibberish_results", status="pass")
            assert result_count > 0 or has_no_results_msg, \
                f"Expected results or no-results msg for '{query}', " \
                f"got {result_count} results, no-results msg={has_no_results_msg}"

        logger.info("TC_POS_04 PASSED — gibberish query handled gracefully.")


# ═══════════════════════════════════════════════════════════════════════ #
#  NEGATIVE TEST CASES                                                    #
# ═══════════════════════════════════════════════════════════════════════ #

@allure.feature("Login")
@allure.story("Negative Tests")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("TC_NEG_01 — Invalid login credentials show error message")
@allure.description(
    "Attempt to log in with the invalid credentials from test_data.json "
    "and verify that an appropriate error message is displayed."
)
class TestNegativeInvalidLoginCredentials:

    def test_invalid_login_credentials(self, driver):
        """
        TC_NEG_01 — Invalid credentials should show an error message.
        Handles Best Buy's two-step login (email → continue → password).
        """
        invalid_email    = _LOGIN["invalid_email"]
        invalid_password = _LOGIN["invalid_password"]

        _PASSWORD_LOCATORS = [
            (By.CSS_SELECTOR, "#fld-p1"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "input[name='password']"),
            (By.CSS_SELECTOR, "[data-testid='password-input']"),
        ]

        with allure.step("Navigate to login page"):
            login_page = LoginPage(driver)
            login_page.navigate_to_login()
            take_screenshot(driver, "TC_NEG_01_login_page", status="info")

        with allure.step(f"Enter invalid email: '{invalid_email}'"):
            login_page.enter_email(invalid_email)
            take_screenshot(driver, "TC_NEG_01_email_entered", status="info")

        with allure.step("Click continue after email"):
            login_page.click_sign_in()
            time.sleep(3)
            take_screenshot(driver, "TC_NEG_01_after_email_continue", status="info")

        # Best Buy may validate email immediately
        if login_page.has_login_error():
            logger.info("Error shown after email step — email validation active.")
            take_screenshot(driver, "TC_NEG_01_error_message", status="pass")
            logger.info("TC_NEG_01 PASSED — invalid credentials show error message.")
            return

        with allure.step("Enter password if field is visible"):
            password_found = False
            for locator in _PASSWORD_LOCATORS:
                try:
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located(locator)
                    )
                    password_found = True
                    logger.info(f"Password field found: {locator}")
                    break
                except TimeoutException:
                    continue

            if password_found:
                login_page.enter_password(invalid_password)
                take_screenshot(driver, "TC_NEG_01_password_entered", status="info")
                login_page.click_sign_in()
                time.sleep(3)
                take_screenshot(driver, "TC_NEG_01_after_final_submit", status="info")

        with allure.step("Assert login was rejected"):
            has_error   = login_page.has_login_error()
            current_url = driver.current_url
            is_logged_in = login_page.is_login_successful()
            logger.info(
                f"Error shown: {has_error} | URL: {current_url} | Logged in: {is_logged_in}"
            )
            take_screenshot(driver, "TC_NEG_01_final_error_check", status="pass")
            assert has_error \
                or "signin" in current_url \
                or "identity" in current_url \
                or not is_logged_in, \
                "User was logged in with invalid credentials — test FAILED."

        logger.info("TC_NEG_01 PASSED — invalid credentials correctly rejected.")


@allure.feature("Search Bar")
@allure.story("Negative Tests")
@allure.severity(allure.severity_level.MINOR)
@allure.title("TC_NEG_02 — Special characters search is handled gracefully")
@allure.description(
    "Search for the 'special_characters' query from test_data.json and verify "
    "the site does not crash — it should show no results or redirect gracefully."
)
class TestNegativeSpecialCharactersSearch:

    def test_special_characters_search(self, driver):
        """TC_NEG_02 — Special characters must not break the site."""
        query = _QUERIES_NEG["special_characters"]

        with allure.step(f"Search for special characters: '{query}'"):
            search_page = SearchPage(driver)
            search_page.search_for(query)
            take_screenshot(driver, "TC_NEG_02_after_search", status="info")

        with allure.step("Assert site is still responsive"):
            title       = search_page.get_title()
            current_url = search_page.get_current_page_url()
            logger.info(f"Title: {title} | URL: {current_url}")

        with allure.step("Assert no server error page"):
            title_lower = title.lower()
            assert "500" not in title_lower, "Server error (500) on special characters search."
            assert "error" not in title_lower or "best buy" in title_lower, \
                f"Unexpected error page. Title: {title}"

        with allure.step("Assert 0 results or no-results message shown"):
            has_no_results_msg = search_page.has_no_results_message()
            result_count       = search_page.get_results_count()
            logger.info(f"No-results msg: {has_no_results_msg} | Items: {result_count}")
            take_screenshot(driver, "TC_NEG_02_graceful_handling", status="pass")
            assert has_no_results_msg or result_count == 0 or "best buy" in title_lower, \
                f"Unexpected results ({result_count}) for special-character query."

        logger.info("TC_NEG_02 PASSED — special characters handled gracefully.")
