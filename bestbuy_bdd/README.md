# Best Buy BDD Selenium Framework (Python + Behave)

A **Behaviour-Driven Development (BDD)** Selenium automation framework for
Best Buy's search bar, built with **Behave** and **Gherkin** feature files.

---

## Project Structure

```
bestbuy_bdd/
├── features/
│   ├── search.feature              # 4 positive + 2 negative scenarios
│   ├── e2e_search_journey.feature  # 1 end-to-end scenario
│   ├── environment.py              # Browser setup/teardown (replaces conftest.py)
│   └── steps/
│       └── search_steps.py         # All step definitions (@given/@when/@then)
├── pages/
│   ├── base_page.py
│   ├── home_page.py
│   ├── search_page.py
│   ├── login_page.py
│   └── cart_page.py
├── utils/
│   ├── driver_factory.py
│   ├── logger.py
│   └── screenshot.py
├── config/
│   ├── config.py
│   ├── test_data.json              # All test data in one place
│   └── credentials.json           # Login credentials
├── screenshots/                    # Auto-created PNG files
├── logs/                           # Auto-created log files
├── reports/
│   ├── allure-results/             # Raw Allure JSON
│   └── allure-report/              # Generated HTML report
├── behave.ini                      # Behave configuration
└── requirements.txt
```

---

## How BDD Works Here

### Feature files (.feature)
Written in **Gherkin** — plain English that anyone can read:
```gherkin
Scenario: TC_POS_01 — Valid product search returns results
  Given I am on the Best Buy homepage
  When I search for the "basic_search" product query
  Then the URL should indicate a search results page
  And at least 1 product result should be visible
```

### Step definitions (steps/search_steps.py)
Each Gherkin line maps to a Python function:
```python
@when('I search for the "{query_key}" product query')
def step_search_positive(context, query_key):
    query = _POS_QUERIES[query_key]
    context.search_page.search_for(query)
```

### environment.py
Replaces pytest's conftest.py — handles browser setup before each
scenario and teardown + screenshot after each scenario.

---

## Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

Update credentials in `config/test_data.json`:
```json
"bestbuy": {
  "email": "your_actual_email@gmail.com",
  "password": "your_actual_password"
}
```

---

## Running Tests

### All scenarios
```bash
behave
```

### Only positive tests
```bash
behave --tags=@positive
```

### Only negative tests
```bash
behave --tags=@negative
```

### Only E2E test
```bash
behave --tags=@e2e
```

### Only critical tests
```bash
behave --tags=@critical
```

### Specific feature file
```bash
behave features/search.feature
behave features/e2e_search_journey.feature
```

### With Allure results
```bash
behave -f allure_behave.formatter:AllureFormatter -o reports/allure-results
allure serve reports/allure-results
```

### Stop on first failure
```bash
behave --stop
```

---

## Test Scenarios

### search.feature

| Tag | Scenario |
|-----|---------|
| @positive @critical | TC_POS_01 — Valid search returns results |
| @positive @normal | TC_POS_02 — Result titles match query |
| @positive @minor | TC_POS_03 — Search bar retains query |
| @positive @normal | TC_POS_04 — Gibberish handled gracefully |
| @negative @critical | TC_NEG_01 — Invalid login rejected |
| @negative @minor | TC_NEG_02 — Special characters handled |

### e2e_search_journey.feature

| Tag | Scenario |
|-----|---------|
| @e2e @blocker | E2E — Login → Search → Add to Cart |

---

## Key Difference from pytest Version

| pytest version | BDD Behave version |
|---|---|
| `conftest.py` | `features/environment.py` |
| `tests/test_search.py` | `features/search.feature` |
| `tests/test_e2e_search_journey.py` | `features/e2e_search_journey.feature` |
| Test methods | `features/steps/search_steps.py` |
| `@pytest.mark` | `@tags` in feature files |
| `assert` statements | Same `assert` statements in step definitions |
| `allure.step` blocks | Gherkin Given/When/Then steps |

Page objects, utils, config and test data are **identical** in both versions.
