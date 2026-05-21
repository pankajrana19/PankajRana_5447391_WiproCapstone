# BestBuy Selenium Automation Framework (Python)

A complete **Page Object Model (POM)** based Selenium automation framework for BestBuy's search bar functionality, built with **pytest** and **Allure** reporting.

---

## Project Structure

```
bestbuy_selenium/
├── config/
│   ├── __init__.py
│   └── config.py               # All constants: URLs, timeouts, test data
├── pages/
│   ├── __init__.py
│   ├── base_page.py            # Reusable Selenium helpers (BasePage)
│   ├── home_page.py            # Home page + country-selector modal
│   └── search_page.py          # Search bar, results, pagination
├── tests/
│   ├── __init__.py
│   ├── test_search.py          # 4 positive + 2 negative test cases
│   └── test_e2e_search_journey.py  # 1 full end-to-end test
├── utils/
│   ├── __init__.py
│   ├── driver_factory.py       # ChromeDriver initialisation
│   ├── logger.py               # Timestamped file + console logger
│   └── screenshot.py           # Screenshot capture + Allure attachment
├── screenshots/                # Auto-created; PNG files saved here
├── logs/                       # Auto-created; .log files saved here
├── reports/
│   ├── allure-results/         # Raw Allure JSON results
│   └── allure-report/          # Generated HTML report
├── conftest.py                 # pytest fixtures + screenshot-on-fail hook
├── pytest.ini                  # pytest + logging configuration
├── requirements.txt            # Python dependencies
├── run_tests.sh                # One-command runner (Linux / macOS)
└── run_tests.bat               # One-command runner (Windows)
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| Google Chrome | Latest stable |
| Java (for Allure CLI) | 8+ |
| Allure CLI (optional) | 2.x |

### Install Allure CLI

**macOS** — `brew install allure`  
**Windows** — `scoop install allure`  
**Linux** — see [Allure docs](https://docs.qameta.io/allure/#_installing_a_commandline)

---

## Setup

```bash
# 1. Clone / download the project
cd bestbuy_selenium

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

`webdriver-manager` automatically downloads the correct ChromeDriver — no manual download needed.

---

## Running Tests

### All tests (recommended)

```bash
# Linux / macOS
bash run_tests.sh

# Windows
run_tests.bat
```

### pytest commands

```bash
# All tests
pytest tests/ -v

# Only the unit test file (4 positive + 2 negative)
pytest tests/test_search.py -v

# Only the E2E test
pytest tests/test_e2e_search_journey.py -v

# With Allure results
pytest tests/ --alluredir=reports/allure-results -v
```

### Generate & open the Allure HTML report

```bash
allure generate reports/allure-results --clean -o reports/allure-report
allure open reports/allure-report
```

---

## Test Cases

### `tests/test_search.py`

| ID | Type | Description |
|----|------|-------------|
| TC_POS_01 | ✅ Positive | Valid product search ("laptop") returns results |
| TC_POS_02 | ✅ Positive | Result titles match the query keyword ("Samsung TV") |
| TC_POS_03 | ✅ Positive | Search bar retains typed query after search |
| TC_POS_04 | ✅ Positive | Pagination navigates across 3+ pages ("gaming mouse") |
| TC_NEG_01 | ❌ Negative | Gibberish search shows no-results state |
| TC_NEG_02 | ❌ Negative | Special characters handled gracefully, no crash |

### `tests/test_e2e_search_journey.py`

| ID | Type | Description |
|----|------|-------------|
| E2E | 🔄 End-to-End | Open site → Select US → Search "laptop" → Navigate 3 pages → Back |

**E2E Steps:**
1. Confirm BestBuy homepage loaded
2. Type query into search bar (check autocomplete suggestions)
3. Submit search
4. Verify search results page
5. Verify results on page 1 + scroll
6. Navigate to page 2, verify results + URL change
7. Navigate to page 3, verify results + URL change
8. Verify URL progression across pages
9. Navigate back and verify state
10. Final summary attachment in Allure

---

## Output Artefacts

### Screenshots
- Saved to `screenshots/` as PNG files
- Naming: `{status}_{test_name}_{timestamp}.png`
- Automatically attached to Allure report
- Captured on **both pass and fail**

### Logs
- Console: INFO level and above
- File: `logs/test_run_{timestamp}.log` — DEBUG level and above
- `logs/pytest.log` — pytest's own log output

### Allure Report
- Raw results: `reports/allure-results/` (JSON)
- HTML report: `reports/allure-report/index.html`
- Shows: test steps, severity, screenshots, text attachments, pass/fail status

---

## Configuration

Edit `config/config.py` to adjust:

```python
BROWSER            = "chrome"
IMPLICIT_WAIT      = 10          # seconds
EXPLICIT_WAIT      = 15          # seconds
PAGE_LOAD_TIMEOUT  = 30          # seconds
MIN_PAGES_TO_NAVIGATE = 3        # minimum pages for pagination tests
```

### Headless mode
In `conftest.py`, change:
```python
web_driver = get_driver(headless=True)   # CI / server
web_driver = get_driver(headless=False)  # watch the browser
```

---

## Framework Design

```
Test File
   │
   ▼
Page Object (HomePage / SearchPage)
   │  uses
   ▼
BasePage  ──────────────►  Selenium WebDriver
   │
   ├── utils/logger.py      (logging)
   ├── utils/screenshot.py  (screenshots + Allure attachments)
   └── utils/driver_factory.py  (ChromeDriver setup)
```

- **Page Object Model** — locators and actions encapsulated in page classes
- **Explicit waits** everywhere — no `time.sleep` in test logic
- **Allure decorators** — `@allure.feature`, `@allure.story`, `@allure.step`, `@allure.severity`
- **Auto-screenshot** on pass/fail via `pytest_runtest_makereport` hook
- **webdriver-manager** — ChromeDriver auto-managed, no manual setup
