# pages/login_page.py

import json
import os
from typing import Optional

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator
from utils.logger import get_logger

logger = get_logger(__name__)

CREDENTIALS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "config", "credentials.json"
)


def load_credentials() -> dict:
    """Load credentials from config/credentials.json."""
    try:
        with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("bestbuy", {})
    except FileNotFoundError:
        logger.error(f"credentials.json not found at: {CREDENTIALS_PATH}")
        raise
    except json.JSONDecodeError as exc:
        logger.error(f"credentials.json is not valid JSON: {exc}")
        raise


class LoginPage(BasePage):
    """
    Page Object for Best Buy account login.
    Handles navigating to the sign-in page, entering credentials,
    submitting the form, and verifying successful login.
    """

    SIGN_IN_URL = "https://www.bestbuy.com/identity/global/signin"

    # ── Locators ──────────────────────────────────────────────────────── #

    # Sign-in trigger in header
    ACCOUNT_BUTTON: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='account-menu-toggle'], "
        ".account-button, "
        "[aria-label*='Account'], "
        "[aria-label*='Sign In']",
    )

    # Sign-in page form fields
    EMAIL_INPUT: Locator = (
        By.CSS_SELECTOR,
        "#fld-e, input[type='email'], input[name='email'], "
        "[data-testid='email-input'], input[autocomplete='email']",
    )
    PASSWORD_INPUT: Locator = (
        By.CSS_SELECTOR,
        "#fld-p1, input[type='password'], input[name='password'], "
        "[data-testid='password-input']",
    )
    SIGN_IN_BUTTON: Locator = (
        By.CSS_SELECTOR,
        "button[data-testid='sign-in-button'], "
        "button[type='submit'], "
        ".cia-form__controls__submit, "
        "button.btn-primary",
    )

    # Post-login verification
    ACCOUNT_NAME: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='account-name'], .account-name, "
        "[class*='AccountName'], [aria-label*='My Account']",
    )
    SIGNED_IN_INDICATOR: Locator = (
        By.XPATH,
        "//*[contains(@class,'account') and not(contains(text(),'Sign In'))] | "
        "//span[contains(@class,'name')]",
    )

    # Error message on failed login
    LOGIN_ERROR: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='login-error'], .cia-form__error, "
        "[class*='error-message'], [role='alert']",
    )

    # ── Actions ───────────────────────────────────────────────────────── #

    def navigate_to_login(self) -> None:
        """Navigate directly to the Best Buy sign-in page."""
        logger.info("Navigating to Best Buy sign-in page …")
        self.open(self.SIGN_IN_URL)
        self.wait_for_element_visible(self.EMAIL_INPUT, timeout=15)
        logger.info("Sign-in page loaded.")

    def enter_email(self, email: str) -> None:
        logger.info(f"Entering email: {email}")
        self.send_keys(self.EMAIL_INPUT, email)

    def enter_password(self, password: str) -> None:
        logger.info("Entering password …")
        self.send_keys(self.PASSWORD_INPUT, password)

    def click_sign_in(self) -> None:
        logger.info("Clicking Sign In button …")
        self.click(self.SIGN_IN_BUTTON)

    def login(self, email: Optional[str] = None, password: Optional[str] = None) -> bool:
        """
        Full login flow:
        1. Load credentials from JSON if not provided
        2. Navigate to sign-in page
        3. Enter email and password
        4. Submit form
        5. Return True if login succeeded, False otherwise

        :param email:    Override email (uses credentials.json if None)
        :param password: Override password (uses credentials.json if None)
        :return:         True if login succeeded
        """
        if email is None or password is None:
            creds = load_credentials()
            email = email or creds.get("email", "")
            password = password or creds.get("password", "")

        if not email or not password:
            logger.error("No credentials provided and credentials.json is empty.")
            return False

        try:
            self.navigate_to_login()
            self.enter_email(email)
            self.enter_password(password)
            self.click_sign_in()

            # Wait for either successful redirect or error message
            import time
            time.sleep(3)

            if self.is_login_successful():
                logger.info("Login successful.")
                return True

            if self.has_login_error():
                error_text = self._get_error_text()
                logger.error(f"Login failed — error shown: {error_text}")
                return False

            # Fallback: if URL changed away from signin, assume success
            current_url = self.get_current_url()
            if "signin" not in current_url and "identity" not in current_url:
                logger.info(f"Login appears successful (redirected to: {current_url})")
                return True

            logger.warning("Login result unclear — no success or error indicator found.")
            return False

        except (TimeoutException, WebDriverException) as exc:
            logger.error(f"Login failed with exception: {exc}")
            return False

    def is_login_successful(self) -> bool:
        """Check if the user is now signed in."""
        # Check URL no longer contains signin
        current_url = self.get_current_url()
        if "signin" not in current_url and "identity" not in current_url:
            return True
        # Check for account name element
        return self.is_element_visible(self.ACCOUNT_NAME, timeout=3)

    def has_login_error(self) -> bool:
        return self.is_element_visible(self.LOGIN_ERROR, timeout=3)

    def _get_error_text(self) -> str:
        try:
            return self.get_text(self.LOGIN_ERROR)
        except (TimeoutException, WebDriverException):
            return "Unknown error"
