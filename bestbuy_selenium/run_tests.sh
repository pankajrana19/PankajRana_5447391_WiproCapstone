#!/usr/bin/env bash
# run_tests.sh — Run all BestBuy Selenium tests and generate Allure report

set -euo pipefail

echo "=============================================="
echo "  BestBuy Selenium Automation Framework"
echo "=============================================="

# 1. Clean previous results
echo "[1/5] Cleaning previous Allure results …"
rm -rf reports/allure-results/*
rm -rf reports/allure-report/*
mkdir -p reports/allure-results reports/allure-report screenshots logs

# 2. Install dependencies
echo "[2/5] Installing Python dependencies …"
pip install -r requirements.txt --quiet

# 3. Run the full test suite
echo "[3/5] Running tests …"
pytest tests/ \
  --alluredir=reports/allure-results \
  -v \
  --tb=short \
  || true   # continue even if some tests fail

# 4. Generate Allure HTML report
echo "[4/5] Generating Allure report …"
if command -v allure &> /dev/null; then
  allure generate reports/allure-results --clean -o reports/allure-report
  echo "      Allure report generated at: reports/allure-report/index.html"
else
  echo "      [SKIP] 'allure' CLI not found."
  echo "      Install via: brew install allure  OR  scoop install allure"
  echo "      Then run:  allure generate reports/allure-results -o reports/allure-report"
fi

# 5. Summary
echo "[5/5] Done!"
echo ""
echo "  Screenshots : ./screenshots/"
echo "  Logs        : ./logs/"
echo "  Allure JSON : ./reports/allure-results/"
echo "  Allure HTML : ./reports/allure-report/index.html"
echo ""
echo "  To open the report run:"
echo "    allure open reports/allure-report"
