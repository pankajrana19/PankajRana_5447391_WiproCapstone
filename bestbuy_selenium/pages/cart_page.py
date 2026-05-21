# pages/cart_page.py

from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By

from pages.base_page import BasePage, Locator
from utils.logger import get_logger

logger = get_logger(__name__)


class CartPage(BasePage):
    """
    Page Object for Best Buy cart verification.
    Handles checking cart contents after adding a product.
    """

    CART_URL = "https://www.bestbuy.com/cart"

    # ── Locators ──────────────────────────────────────────────────────── #

    # Cart icon / count in header
    CART_COUNT: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='cart-count'], .cart-count, "
        "[class*='CartCount'], .cartCount",
    )

    # Items in cart
    CART_ITEMS: Locator = (
        By.CSS_SELECTOR,
        ".cart-item, [data-testid='cart-item'], "
        "[class*='CartItem'], .fluid-large-view__content",
    )

    # Cart item name
    CART_ITEM_NAME: Locator = (
        By.CSS_SELECTOR,
        ".cart-item__name, [data-testid='cart-item-name'], "
        "[class*='item-name'], .sku-title",
    )

    # Empty cart message
    EMPTY_CART_MSG: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='empty-cart'], .empty-cart, "
        "[class*='EmptyCart']",
    )

    # Add to cart confirmation modal / button
    ADD_TO_CART_MODAL: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='add-to-cart-modal'], "
        ".add-to-cart-overlay, "
        "[class*='AddToCartModal']",
    )
    VIEW_CART_BUTTON: Locator = (
        By.CSS_SELECTOR,
        "[data-testid='go-to-cart-button'], "
        "a[href='/cart'], "
        ".go-to-cart-button",
    )

    # ── Actions ───────────────────────────────────────────────────────── #

    def navigate_to_cart(self) -> None:
        logger.info("Navigating to cart …")
        self.open(self.CART_URL)

    def get_cart_item_count(self) -> int:
        """Return number of items in the cart."""
        items = self.get_elements(self.CART_ITEMS)
        return len(items)

    def is_cart_empty(self) -> bool:
        return self.is_element_visible(self.EMPTY_CART_MSG, timeout=5)

    def has_items_in_cart(self) -> bool:
        try:
            items = self.wait_for_elements_present(self.CART_ITEMS, timeout=10)
            return len(items) > 0
        except TimeoutException:
            return False

    def get_cart_item_names(self) -> list:
        elements = self.get_elements(self.CART_ITEM_NAME)
        return [el.text.strip() for el in elements if el.text.strip()]

    def get_cart_count_from_header(self) -> str:
        """Return the cart count badge text from the header."""
        try:
            element = self.wait_for_element_visible(self.CART_COUNT, timeout=5)
            return element.text.strip()
        except (TimeoutException, WebDriverException):
            return "0"
