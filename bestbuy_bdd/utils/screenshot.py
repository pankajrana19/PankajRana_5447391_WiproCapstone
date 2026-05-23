# utils/screenshot.py

import os
from datetime import datetime

import allure

from utils.logger import get_logger

logger = get_logger(__name__)


def take_screenshot(driver, name: str, status: str = "info") -> str:
    """
    Captures a screenshot and saves it to the screenshots/ directory.
    Also attaches it to the Allure report.

    :param driver:  WebDriver instance
    :param name:    Descriptive name for the screenshot
    :param status:  'pass', 'fail', or 'info'
    :return:        Path to the saved screenshot file
    """
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_name = name.replace(" ", "_").replace("/", "-")
    filename = f"{status}_{safe_name}_{timestamp}.png"
    filepath = os.path.join(screenshots_dir, filename)

    try:
        driver.save_screenshot(filepath)
        logger.info(f"Screenshot saved: {filepath}")

        # Attach to Allure report
        with open(filepath, "rb") as img_file:
            allure.attach(
                img_file.read(),
                name=f"{status.upper()} | {name}",
                attachment_type=allure.attachment_type.PNG
            )
    except Exception as e:
        logger.error(f"Failed to take screenshot '{name}': {e}")

    return filepath
