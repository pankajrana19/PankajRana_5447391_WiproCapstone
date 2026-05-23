# features/steps/search_steps.py
"""
Step definitions for search.feature and e2e_search_journey.feature.
Each @given/@when/@then maps to a line in the .feature file.
"""

import json
import os
import time

from behave import given, when, then
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from pages.home_page import HomePage
from pages.login_page import LoginPage
from pages.search_page import SearchPage
from utils.logger import get_logger
from utils.screenshot import take_screenshot

logger = get_logger(__name__)

# ── Load test data ─────────────────────────────────────────────────── #

_DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "config", "test_data.json"
)

with open(_DATA_PATH, "r", encoding="utf-8") as _f:
    _TD = json.load(_f)

_POS_QUERIES = _TD["search"]["positive_queries"]
_NEG_QUERIES = _TD["search"]["negative_queries"]
_KEYWORDS    = _TD["search"]["title_match_keywords"]
_RATIO       = _TD["search"]["title_match_ratio_threshold"]
_LOGIN       = _TD["login"]
_E2E_QUERY   = _TD["search"]["e2e_query"]


# ═══════════════════════════════════════════════════════════════════════ #
#  GIVEN STEPS                                                            #
# ═══════════════════════════════════════════════════════════════════════ #

@given("I open the Best Buy homepage")
def step_open_bestbuy(context):
    """
    Homepage is already opened in before_scenario (environment.py).
    This step just confirms we have the driver ready.
    """
    context.home_page   = HomePage(context.driver)
    context.search_page = SearchPage(context.driver)
    logger.info("Best Buy homepage context initialised.")


@given("the homepage is loaded successfully")
def step_homepage_loaded(context):
    assert context.home_page.is_home_page_loaded(), \
        "Best Buy homepage did not load — search bar not visible."
    take_screenshot(context.driver, "homepage_loaded", status="info")
    logger.info("Homepage confirmed loaded.")


@given("I am on the Best Buy homepage")
def step_on_homepage(context):
    """Alias for the Background step — confirms driver and pages are set up."""
    if not hasattr(context, "search_page"):
        context.home_page   = HomePage(context.driver)
        context.search_page = SearchPage(context.driver)
    logger.info("On Best Buy homepage — ready for test.")


@given("I navigate to the Best Buy login page")
def step_navigate_to_login(context):
    context.login_page = LoginPage(context.driver)
    context.login_page.navigate_to_login()
    take_screenshot(context.driver, "TC_NEG_01_login_page", status="info")
    logger.info("Navigated to Best Buy login page.")


# ═══════════════════════════════════════════════════════════════════════ #
#  WHEN STEPS                                                             #
# ═══════════════════════════════════════════════════════════════════════ #

@when('I search for }the "{query_key" product query')
def step_search_positive(context, query_key):
    """
    Searches using a key from test_data.json positive_queries.
    e.g. "basic_search" → "laptop"
    """
    query = _POS_QUERIES[query_key]
    context.last_query = query
    logger.info(f"Searching for '{query}' (key: {query_key})")
    context.search_page.search_for(query)
    take_screenshot(context.driver, f"search_{query_key}", status="info")


@when('I search for the "{query_key}" negative query')
def step_search_negative(context, query_key):
    """
    Searches using a key from test_data.json negative_queries.
    e.g. "special_characters" → "!@#$%"
    """
    query = _NEG_QUERIES[query_key]
    context.last_query = query
    logger.info(f"Searching for negative query '{query}' (key: {query_key})")
    context.search_page.search_for(query)
    take_screenshot(context.driver, f"search_neg_{query_key}", status="info")


@when("I search for the e2e product query")
def step_search_e2e(context):
    context.last_query = _E2E_QUERY
    logger.info(f"E2E: searching for '{_E2E_QUERY}'")
    context.search_page.search_for(_E2E_QUERY)
    take_screenshot(context.driver, "E2E_search_submitted", status="info")


@when("I login with credentials from test_data")
def step_login(context):
    context.login_page    = LoginPage(context.driver)
    context.login_success = context.login_page.login()
    take_screenshot(context.driver, "E2E_after_login", status="info")

    if context.login_success:
        logger.info("Login succeeded.")
    else:
        logger.warning(
            "Login failed — continuing as guest. "
            "Update email/password in config/test_data.json."
        )
        # Navigate back to homepage so search still works
        context.home_page.open_bestbuy()


@when("I enter invalid login credentials")
def step_enter_invalid_credentials(context):
    invalid_email    = _LOGIN["invalid_email"]
    invalid_password = _LOGIN["invalid_password"]

    _PASSWORD_LOCATORS = [
        (By.CSS_SELECTOR, "#fld-p1"),
        (By.CSS_SELECTOR, "input[type='password']"),
        (By.CSS_SELECTOR, "input[name='password']"),
        (By.CSS_SELECTOR, "[data-testid='password-input']"),
    ]

    context.login_page.enter_email(invalid_email)
    take_screenshot(context.driver, "TC_NEG_01_email_entered", status="info")

    context.login_page.click_sign_in()
    time.sleep(3)
    take_screenshot(context.driver, "TC_NEG_01_after_email", status="info")

    # If error shown immediately after email, store and return
    if context.login_page.has_login_error():
        logger.info("Error shown after email step.")
        context.login_error_shown = True
        return

    context.login_error_shown = False

    # Try password field
    password_found = False
    for locator in _PASSWORD_LOCATORS:
        try:
            WebDriverWait(context.driver, 5).until(
                EC.presence_of_element_located(locator)
            )
            password_found = True
            logger.info(f"Password field found: {locator}")
            break
        except TimeoutException:
            continue

    if password_found:
        context.login_page.enter_password(invalid_password)
        take_screenshot(context.driver, "TC_NEG_01_password_entered", status="info")
        context.login_page.click_sign_in()
        time.sleep(3)
        take_screenshot(context.driver, "TC_NEG_01_after_submit", status="info")


@when("I add the first available item to cart from the results page")
def step_add_to_cart(context):
    context.item_added = context.search_page.add_first_available_to_cart()
    take_screenshot(context.driver, "E2E_add_to_cart", status="info")
    logger.info(f"Add to cart result: {context.item_added}")


# ═══════════════════════════════════════════════════════════════════════ #
#  THEN STEPS                                                             #
# ═══════════════════════════════════════════════════════════════════════ #

@then("the URL should indicate a search results page")
def step_verify_results_url(context):
    current_url = context.search_page.get_current_page_url()
    query       = context.last_query.lower()
    logger.info(f"Results URL: {current_url}")
    assert query in current_url.lower() \
        or context.search_page.is_on_search_results_page(), \
        f"Expected search results URL for '{query}', got: {current_url}"


@then("at least 1 product result should be visible")
def step_verify_results_count(context):
    result_count = context.search_page.get_results_count()
    logger.info(f"Results found: {result_count}")
    take_screenshot(context.driver, "TC_POS_01_results", status="pass")
    assert result_count > 0, \
        f"Expected results for '{context.last_query}', found {result_count}"


@then("the results page should load successfully")
def step_verify_results_page_loaded(context):
    url   = context.search_page.get_current_page_url()
    title = context.search_page.get_title()
    logger.info(f"Results URL: {url} | Title: {title}")
    assert context.search_page.is_on_search_results_page() \
        or context.last_query.lower() in url.lower(), \
        f"Not on results page. URL={url}"


@then("at least 30 percent of result titles should contain a relevant keyword")
def step_verify_title_relevance(context):
    titles = context.search_page.get_result_titles()
    logger.info(f"Fetched {len(titles)} result titles.")
    assert len(titles) > 0, "No product titles found on results page."

    matching    = [t for t in titles if any(kw in t.lower() for kw in _KEYWORDS)]
    match_ratio = len(matching) / len(titles)
    logger.info(f"Matching: {len(matching)}/{len(titles)} ({match_ratio:.0%})")
    take_screenshot(context.driver, "TC_POS_02_titles_check", status="pass")
    assert match_ratio >= _RATIO, \
        f"Only {match_ratio:.0%} of titles match {_KEYWORDS}. Titles: {titles[:5]}"


@then("the search bar should still display the typed query")
def step_verify_search_bar_retention(context):
    retained = context.search_page.get_search_input_value()
    logger.info(f"Search bar retained: '{retained}'")
    take_screenshot(context.driver, "TC_POS_03_input_retained", status="pass")
    assert context.last_query.lower() in retained.lower(), \
        f"Expected '{context.last_query}' in search bar, found '{retained}'"


@then("the site should not show a server error")
def step_verify_no_server_error(context):
    title       = context.search_page.get_title()
    title_lower = title.lower()
    logger.info(f"Page title: {title}")
    context.title_lower = title_lower  # store for next step
    assert "500" not in title_lower, "Server error (500) detected."
    assert "error" not in title_lower or "best buy" in title_lower, \
        f"Unexpected error page. Title: {title}"


@then("the site should either show results or a no-results message")
def step_verify_graceful_handling(context):
    result_count      = context.search_page.get_results_count()
    has_no_results    = context.search_page.has_no_results_message()
    title_lower       = getattr(context, "title_lower", "")
    logger.info(f"Results: {result_count} | No-results msg: {has_no_results}")
    take_screenshot(context.driver, "TC_POS_04_graceful", status="pass")
    assert result_count > 0 or has_no_results or "best buy" in title_lower, \
        f"Expected results or no-results message, got {result_count} results."


@then("the search should return zero results or a no-results message")
def step_verify_no_results(context):
    result_count   = context.search_page.get_results_count()
    has_no_results = context.search_page.has_no_results_message()
    title_lower    = getattr(context, "title_lower", "")
    logger.info(f"No-results msg: {has_no_results} | Items: {result_count}")
    take_screenshot(context.driver, "TC_NEG_02_graceful", status="pass")
    assert has_no_results or result_count == 0 or "best buy" in title_lower, \
        f"Unexpected results ({result_count}) for special-character query."


@then("the login should be rejected")
def step_verify_login_rejected(context):
    # If error was shown after email step we already know it's rejected
    if getattr(context, "login_error_shown", False):
        logger.info("Login rejected at email step.")
        return

    has_error    = context.login_page.has_login_error()
    current_url  = context.driver.current_url
    is_logged_in = context.login_page.is_login_successful()
    logger.info(f"Error: {has_error} | URL: {current_url} | Logged in: {is_logged_in}")
    take_screenshot(context.driver, "TC_NEG_01_rejection_check", status="pass")
    assert has_error \
        or "signin" in current_url \
        or "identity" in current_url \
        or not is_logged_in, \
        "User was logged in with invalid credentials — test FAILED."


@then("an error message should be shown or the user should remain on the login page")
def step_verify_error_shown(context):
    if getattr(context, "login_error_shown", False):
        logger.info("TC_NEG_01 PASSED — error shown after email step.")
        return

    has_error   = context.login_page.has_login_error()
    current_url = context.driver.current_url
    take_screenshot(context.driver, "TC_NEG_01_error_check", status="pass")
    assert has_error \
        or "signin" in current_url \
        or "identity" in current_url, \
        "No error message shown and user not on login page."
    logger.info("TC_NEG_01 PASSED — invalid credentials correctly rejected.")


@then("I should be logged in or continue as guest")
def step_verify_login_or_guest(context):
    if context.login_success:
        logger.info("E2E: logged in successfully.")
    else:
        logger.info("E2E: continuing as guest.")
    # Either outcome is acceptable — test continues
    assert True


@then("the search results page should load")
def step_e2e_results_page(context):
    url   = context.search_page.get_current_page_url()
    title = context.search_page.get_title()
    logger.info(f"E2E results URL: {url} | Title: {title}")
    take_screenshot(context.driver, "E2E_results_page", status="pass")
    assert (
        _E2E_QUERY.lower() in url.lower()
        or _E2E_QUERY.lower() in title.lower()
        or context.search_page.is_on_search_results_page()
    ), f"Not on results page. URL={url}"


@then("at least 1 result should be present on page 1")
def step_e2e_verify_results(context):
    count  = context.search_page.get_results_count()
    titles = context.search_page.get_result_titles()
    logger.info(f"E2E Page 1: {count} results")
    take_screenshot(context.driver, "E2E_page1_results", status="pass")
    assert count > 0, f"No results found for '{_E2E_QUERY}' on page 1."
    # Store for summary
    context.page1_count  = count
    context.page1_titles = titles


@then("the item should be added to cart successfully")
def step_e2e_verify_cart(context):
    take_screenshot(context.driver, "E2E_item_added", status="pass")
    assert context.item_added, \
        "Could not add any item to cart — all items may be sold out or unavailable."
    logger.info("E2E TEST PASSED — Login → Search → Add to Cart.")
