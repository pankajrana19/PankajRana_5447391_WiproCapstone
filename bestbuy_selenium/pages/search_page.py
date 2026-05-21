# pages/search_page.py

import time
from typing import List

from selenium.common.exceptions import (
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from pages.base_page import BasePage, Locator
from utils.logger import get_logger

logger = get_logger(__name__)


class SearchPage(BasePage):
    """
    Page Object for Best Buy search functionality.
    Covers the search bar, results listing, pagination and no-results state.
    """

    # ── Locators ──────────────────────────────────────────────────────── #

    SEARCH_INPUT: Locator = (
        By.CSS_SELECTOR,
        "#gh-search-input, input[name='st'], [placeholder*='Search'], "
        "#autocomplete-search-bar",
    )
    SEARCH_BUTTON: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='header-search-button'], .header-search-btn, button.search-submit",
    )

    # Results — covers both page 1 (slContainer/sponsored) and page 2+ (sku-item)
    RESULT_ITEMS: Locator = (
        By.CSS_SELECTOR,
        "li.sku-item, div.sku-item, [class*='sku-item'], "
        "li.slContainer, .product-list-item, "
        "[data-testid='list-item']",
    )

    # Product titles
    RESULT_TITLES: Locator = (
        By.CSS_SELECTOR,
        "h4.sku-title a, h3.product-title, "
        ".product-list-item-link h3, "
        ".sku-block-content-title h3, "
        "h3[class*='product-title']",
    )

    RESULTS_COUNT_TEXT: Locator = (
        By.CSS_SELECTOR,
        "[class*='results-count'], .results-count span, "
        "[data-testid='resultsCount'], span.results-count",
    )

    # No-results state
    NO_RESULTS_MSG: Locator = (
        By.CSS_SELECTOR,
        "[class*='no-results'], .no-results, [class*='NoResults'], "
        "[data-testid='no-results']",
    )
    NO_RESULTS_XPATH: Locator = (
        By.XPATH,
        "//*[contains(text(),'no results') or contains(text(),'No results') or "
        "contains(text(),'did not match') or contains(text(),'0 Results')]",
    )

    # Pagination — aria-label='Next page' is what Best Buy actually uses
    NEXT_PAGE_BTN: Locator = (
        By.CSS_SELECTOR,
        "a[aria-label='Next page'], "
        "a[aria-label='Next Page'], "
        "a.sku-list-page-next, "
        "[data-testid='next-page-btn'], "
        ".pager-next a, "
        ".pagination-next",
    )
    NEXT_PAGE_XPATH: Locator = (
        By.XPATH,
        "//a[contains(@aria-label,'Next') or contains(@title,'Next') or "
        "contains(@class,'pagination-arrow')]",
    )

    PAGE_NUMBERS: Locator = (
        By.CSS_SELECTOR,
        ".pager-list li, [class*='pagination'] li, [data-testid='page-number']",
    )

    # Autocomplete suggestions
    SEARCH_SUGGESTIONS: Locator = (
        By.CSS_SELECTOR,
        ".suggestions-list li, [class*='suggestions'] li, "
        "[role='listbox'] [role='option'], .search-suggestions li",
    )

    _NEXT_PAGE_LOCATORS: List[Locator] = [
        (
            By.CSS_SELECTOR,
            "a[aria-label='Next page'], "
            "a[aria-label='Next Page'], "
            "a.sku-list-page-next, "
            "[data-testid='next-page-btn'], "
            ".pager-next a, "
            ".pagination-next",
        ),
        (
            By.XPATH,
            "//a[contains(@aria-label,'Next') or contains(@title,'Next') or "
            "contains(@class,'pagination-arrow')]",
        ),
    ]

    # ── Actions ───────────────────────────────────────────────────────── #

    def search_for(self, query: str) -> None:
        """Type query into the search bar, submit, and wait for results."""
        logger.info(f"Searching for: '{query}'")
        search_box = self.wait_for_element_visible(self.SEARCH_INPUT, timeout=10)
        search_box.clear()
        search_box.send_keys(query)
        search_box.send_keys(Keys.RETURN)
        # Wait for URL to update then wait for results to be present in DOM
        self.wait_for_url_contains("st=", timeout=10)
        self.wait_for_elements_present(self.RESULT_ITEMS, timeout=15)
        logger.info(f"Search submitted for: '{query}'")

    def search_via_button(self, query: str) -> None:
        """Type query and click the search button (falls back to Enter key)."""
        logger.info(f"Searching via button for: '{query}'")
        search_box = self.wait_for_element_visible(self.SEARCH_INPUT, timeout=10)
        search_box.clear()
        search_box.send_keys(query)
        try:
            self.click(self.SEARCH_BUTTON)
        except (TimeoutException, WebDriverException) as exc:
            logger.debug(f"Search button click failed ({exc}); falling back to Enter.")
            search_box.send_keys(Keys.RETURN)
        self.wait_for_url_contains("st=", timeout=10)
        self.wait_for_elements_present(self.RESULT_ITEMS, timeout=15)

    def get_search_results(self) -> list:
        """
        Return a list of visible search-result elements.
        Uses presence check (not visibility) for lazy-loaded Best Buy content,
        then filters to only visible items.
        """
        results = self.wait_for_elements_present(self.RESULT_ITEMS, timeout=15)
        return [el for el in results if el.is_displayed()]

    def get_results_count(self) -> int:
        try:
            return len(self.get_search_results())
        except TimeoutException:
            logger.warning(
                "get_results_count: results did not appear — page may not have loaded."
            )
            return 0

    def has_results(self) -> bool:
        return self.get_results_count() > 0

    def has_no_results_message(self) -> bool:
        return self.is_element_visible(
            self.NO_RESULTS_MSG, timeout=5
        ) or self.is_element_visible(self.NO_RESULTS_XPATH, timeout=5)

    def get_result_titles(self) -> List[str]:
        elements = self.get_elements(self.RESULT_TITLES)
        return [el.text.strip() for el in elements if el.text.strip()]

    def get_search_input_value(self) -> str:
        element = self.wait_for_element_visible(self.SEARCH_INPUT, timeout=5)
        return element.get_attribute("value") or ""

    def clear_search_bar(self) -> None:
        element = self.wait_for_element_visible(self.SEARCH_INPUT, timeout=5)
        element.clear()
        logger.info("Search bar cleared.")

    def get_suggestions(self) -> List[str]:
        try:
            elements = self.wait_for_elements_visible(
                self.SEARCH_SUGGESTIONS, timeout=5
            )
            return [el.text.strip() for el in elements if el.text.strip()]
        except TimeoutException:
            return []

    # ── Pagination ────────────────────────────────────────────────────── #

    def go_to_next_page(self) -> bool:
        """
        Click the Next pagination button using JS to bypass any overlay.
        Waits for URL to update to cp=N and results to load before returning.
        """
        for locator in self._NEXT_PAGE_LOCATORS:
            try:
                btn = self.wait_for_element_clickable(locator, timeout=8)
                self.scroll_to_element(btn)
                # JS click bypasses any overlay (e.g. sticky search bar) blocking the button
                self.driver.execute_script("arguments[0].click();", btn)
                # Wait for URL page parameter and results to confirm navigation
                self.wait_for_url_contains("cp=", timeout=10)
                self.wait_for_elements_present(self.RESULT_ITEMS, timeout=15)
                time.sleep(1)  # brief settle for dynamic content
                logger.info("Navigated to next page.")
                return True
            except TimeoutException:
                continue
            except WebDriverException as exc:
                logger.debug(f"Next-page click error ({locator}): {exc}")
                continue

        logger.warning("No 'Next' page button found.")
        return False

    def navigate_pages(self, num_pages: int) -> int:
        visited = 1
        logger.info(f"Will attempt to navigate {num_pages} total pages …")
        for page_num in range(2, num_pages + 1):
            if self.go_to_next_page():
                visited += 1
                logger.info(f"On page {page_num}")
            else:
                logger.warning(
                    f"Could not navigate to page {page_num}. "
                    f"Stopping at page {visited}."
                )
                break
        return visited

    def is_on_search_results_page(self) -> bool:
        url = self.get_current_url()
        return "searchpage=1" in url or "/s/" in url or "search" in url.lower()

    def get_current_page_url(self) -> str:
        return self.get_current_url()

    # ── Add to Cart from results page ─────────────────────────────────── #

    # Add to Cart button on the results listing
    ADD_TO_CART_BTN: Locator = (
        By.CSS_SELECTOR,
        "[data-testid^='plp-add-to-cart'], "
        "button[class*='add-to-cart'], "
        ".add-to-cart-button, "
        "button[data-sku-id]",
    )

    # "Go to Cart" / confirmation after adding
    GO_TO_CART_BTN: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='go-to-cart-button'], "
        "a[href='/cart'], "
        ".go-to-cart-button",
    )

    # Cart count badge in header (to confirm item was added)
    CART_COUNT_BADGE: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='cart-count'], .cart-count, [class*='CartCount']",
    )

    def add_first_available_to_cart(self) -> bool:
        """
        Clicks the Add to Cart button on the first available product
        directly from the search results page.
        Returns True if an item was added, False if none were available.
        """
        import time

        buttons = self.get_elements(self.ADD_TO_CART_BTN)
        logger.info(f"Found {len(buttons)} Add to Cart buttons on results page.")

        for i, btn in enumerate(buttons):
            try:
                if not btn.is_displayed() or not btn.is_enabled():
                    continue

                btn_text = btn.text.strip().lower()
                # Skip sold-out / coming-soon / check availability buttons
                if any(
                    skip in btn_text
                    for skip in ["sold out", "unavailable", "check stores", "coming soon"]
                ):
                    logger.info(f"Button {i+1} skipped: '{btn_text}'")
                    continue

                logger.info(f"Clicking Add to Cart button {i+1}: '{btn_text}'")
                self.scroll_to_element(btn)
                self.driver.execute_script("arguments[0].click();", btn)
                time.sleep(2)
                logger.info("Add to Cart clicked successfully.")
                return True

            except WebDriverException as exc:
                logger.debug(f"Button {i+1} click failed: {exc}")
                continue

        logger.warning("No available Add to Cart button found on results page.")
        return False

    def dismiss_add_to_cart_modal(self) -> None:
        """Dismiss the post-add-to-cart modal if it appears."""
        import time
        try:
            close_btn = self.wait_for_element_clickable(
                (By.CSS_SELECTOR,
                 "[data-testid='close-button'], .close-button, "
                 "button[aria-label='Close']"),
                timeout=4,
            )
            close_btn.click()
            time.sleep(1)
            logger.info("Add to Cart modal dismissed.")
        except (TimeoutException, WebDriverException):
            logger.debug("No Add to Cart modal to dismiss.")
