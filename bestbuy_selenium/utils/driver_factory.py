# utils/driver_factory.py

import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions

from config.config import IMPLICIT_WAIT, PAGE_LOAD_TIMEOUT
from utils.logger import get_logger

logger = get_logger(__name__)

CHROMEDRIVER_PATH = (
    r"C:\Users\ACER\.wdm\chromedriver-win64\chromedriver-win64\chromedriver.exe"
)


def get_driver(headless: bool = False) -> webdriver.Chrome:
    logger.info("Initialising Chrome WebDriver …")
    logger.info(f"ChromeDriver path: {CHROMEDRIVER_PATH}")

    options = ChromeOptions()

    if headless:
        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
    else:
        options.add_argument("--start-maximized")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--remote-debugging-port=9222")

    user_data_dir = os.path.join(os.path.expanduser("~"), "selenium_chrome_profile")
    options.add_argument(f"--user-data-dir={user_data_dir}")

    prefs = {
        "profile.default_content_setting_values.geolocation": 2,
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.media_stream": 2,
        "profile.exit_type": "Normal",
        "profile.exited_cleanly": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    )

    service = ChromeService(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)

    driver.implicitly_wait(IMPLICIT_WAIT)
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)

    if not headless:
        driver.maximize_window()

    logger.info("Chrome WebDriver initialised successfully.")
    return driver
