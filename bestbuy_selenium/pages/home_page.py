# pages/home_page.py

from typing import List

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from config.config import BASE_URL
from pages.base_page import BasePage, Locator
from utils.logger import get_logger

logger = get_logger(__name__)


class HomePage(BasePage):

    # ── Locators ──────────────────────────────────────────────────────── #

    SEARCH_INPUT: Locator = (
        By.CSS_SELECTOR,
        "#gh-search-input, input[name='st'], [placeholder*='Search'], "
        "#autocomplete-search-bar",
    )
    SEARCH_BUTTON: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='header-search-button'], .header-search-btn, button[type='submit']",
    )

    FEEDBACK_CLOSE: Locator = (
        By.CSS_SELECTOR,
        "#fsrFocusFirst, .fsrButton, [id*='fsrFocus'], "
        "[class*='fsr-button'], [id*='fsr'] button",
    )
    FEEDBACK_NO_THANKS: Locator = (
        By.XPATH,
        "//a[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'no thank')] | "
        "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),'no thank')]",
    )

    _COUNTRY_SELECTORS: List[Locator] = [
        (By.CSS_SELECTOR, "[data-testid='us-link']"),
        (By.CSS_SELECTOR, ".us-link"),
        (
            By.XPATH,
            "//a[contains(@href,'bestbuy.com') and "
            "contains(translate(.,'us','US'),'United States')]",
        ),
        (By.XPATH, "//a[normalize-space()='United States']"),
        (By.XPATH, "//button[normalize-space()='United States']"),
        (
            By.XPATH,
            "//*[contains(@class,'us') and "
            "(normalize-space()='United States' or "
            "contains(normalize-space(),'United States'))]",
        ),
    ]

    # ── Actions ───────────────────────────────────────────────────────── #

    def open_bestbuy(self) -> None:
        logger.info("Opening Best Buy home page …")
        self.open(BASE_URL)
        # Wait for the search bar to confirm page loaded — no fixed sleep
        self.wait_for_element_visible(self.SEARCH_INPUT, timeout=15)
        self._handle_country_modal()
        self._dismiss_feedback_popup()

    def _handle_country_modal(self) -> None:
        # Reduced to 2s per selector — 6 selectors × 2s = max 12s wasted when absent
        for locator in self._COUNTRY_SELECTORS:
            try:
                element = self.wait_for_element_clickable(locator, timeout=2)
                logger.info(f"Country modal found: {locator}. Selecting United States …")
                element.click()
                # Wait for search bar to confirm modal dismissed — no fixed sleep
                self.wait_for_element_visible(self.SEARCH_INPUT, timeout=10)
                logger.info("United States selected successfully.")
                return
            except TimeoutException:
                continue
            except WebDriverException as exc:
                logger.debug(f"Selector {locator} raised WebDriverException: {exc}")
                continue

        logger.info("No country-selection modal detected — proceeding directly.")

    def _dismiss_feedback_popup(self) -> None:
        for locator in [self.FEEDBACK_NO_THANKS, self.FEEDBACK_CLOSE]:
            try:
                element = self.wait_for_element_clickable(locator, timeout=3)
                element.click()
                logger.info("Feedback popup dismissed.")
                return
            except TimeoutException:
                continue
            except WebDriverException as exc:
                logger.debug(f"Feedback popup dismissal error: {exc}")
                continue

        logger.debug("No feedback popup detected.")

    def is_home_page_loaded(self) -> bool:
        return self.is_element_visible(self.SEARCH_INPUT, timeout=10)

    def get_search_input(self) -> WebElement:
        return self.wait_for_element_visible(self.SEARCH_INPUT, timeout=10)
