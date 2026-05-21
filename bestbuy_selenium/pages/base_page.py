# pages/base_page.py

import time
from typing import List, Tuple

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config.config import EXPLICIT_WAIT
from utils.logger import get_logger

logger = get_logger(__name__)

Locator = Tuple[str, str]


class BasePage:

    def __init__(self, driver: WebDriver) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, EXPLICIT_WAIT)

    # ── Navigation ──────────────────────────────────────────────────── #

    def open(self, url: str) -> None:
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

    def get_current_url(self) -> str:
        return self.driver.current_url

    def get_title(self) -> str:
        return self.driver.title

    # ── Wait helpers ────────────────────────────────────────────────── #

    def wait_for_element_visible(
        self, locator: Locator, timeout: int = EXPLICIT_WAIT
    ) -> WebElement:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
        except TimeoutException:
            logger.warning(f"Element not visible after {timeout}s: {locator}")
            raise

    def wait_for_element_clickable(
        self, locator: Locator, timeout: int = EXPLICIT_WAIT
    ) -> WebElement:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
        except TimeoutException:
            logger.warning(f"Element not clickable after {timeout}s: {locator}")
            raise

    def wait_for_elements_visible(
        self, locator: Locator, timeout: int = EXPLICIT_WAIT
    ) -> List[WebElement]:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_all_elements_located(locator)
            )
        except TimeoutException:
            logger.warning(f"Elements not visible after {timeout}s: {locator}")
            return []

    def wait_for_elements_present(
        self, locator: Locator, timeout: int = EXPLICIT_WAIT
    ) -> List[WebElement]:
        """
        Waits for elements to be present in the DOM (not necessarily visible).
        Better for dynamic/lazy-loaded content like Best Buy product listings.
        """
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located(locator)
            )
        except TimeoutException:
            logger.warning(f"Elements not present after {timeout}s: {locator}")
            return []

    def wait_for_url_contains(self, text: str, timeout: int = EXPLICIT_WAIT) -> bool:
        try:
            return bool(
                WebDriverWait(self.driver, timeout).until(EC.url_contains(text))
            )
        except TimeoutException:
            return False

    # ── Interaction helpers ─────────────────────────────────────────── #

    def click(self, locator: Locator) -> None:
        element = self.wait_for_element_clickable(locator)
        try:
            element.click()
            logger.debug(f"Clicked: {locator}")
        except ElementClickInterceptedException:
            logger.warning(f"Click intercepted, trying JS click: {locator}")
            self.driver.execute_script("arguments[0].click();", element)

    def send_keys(self, locator: Locator, text: str) -> None:
        element = self.wait_for_element_visible(locator)
        element.clear()
        element.send_keys(text)
        logger.debug(f"Typed '{text}' into: {locator}")

    def get_text(self, locator: Locator) -> str:
        element = self.wait_for_element_visible(locator)
        return element.text.strip()

    def is_element_present(self, locator: Locator) -> bool:
        try:
            self.driver.find_element(*locator)
            return True
        except NoSuchElementException:
            return False

    def is_element_visible(self, locator: Locator, timeout: int = 5) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def scroll_to_bottom(self) -> None:
        self.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )
        WebDriverWait(self.driver, 5).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )

    def scroll_to_element(self, element: WebElement) -> None:
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});", element
        )

    def get_elements(self, locator: Locator) -> List[WebElement]:
        try:
            return self.driver.find_elements(*locator)
        except (NoSuchElementException, WebDriverException) as exc:
            logger.debug(f"get_elements failed for {locator}: {exc}")
            return []
