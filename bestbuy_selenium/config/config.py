# config/config.py

BASE_URL = "https://www.bestbuy.com"
BROWSER = "chrome"
IMPLICIT_WAIT = 10
EXPLICIT_WAIT = 15
PAGE_LOAD_TIMEOUT = 30

# Directories
SCREENSHOTS_DIR = "screenshots"
LOGS_DIR = "logs"
ALLURE_RESULTS_DIR = "reports/allure-results"

# Test Data - Search Terms (Positive)
VALID_SEARCH_TERMS = [
    "laptop",
    "Samsung TV",
    "iPhone 15",
    "headphones",
    "gaming mouse"
]

# Test Data - Search Terms (Negative)
INVALID_SEARCH_TERMS = [
    "xyzabc123notaproduct",
    "!@#$%^&*()"
]

# Pagination
MIN_PAGES_TO_NAVIGATE = 3
