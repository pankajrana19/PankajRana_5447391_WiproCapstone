@echo off
REM run_tests.bat — BestBuy Selenium tests on Windows

echo ==============================================
echo   BestBuy Selenium Automation Framework
echo ==============================================

echo [1/5] Cleaning previous results...
if exist reports\allure-results rmdir /s /q reports\allure-results
if exist reports\allure-report  rmdir /s /q reports\allure-report
if exist screenshots            rmdir /s /q screenshots
mkdir reports\allure-results
mkdir reports\allure-report
mkdir screenshots
mkdir logs

echo [2/5] Installing Python dependencies...
pip install -r requirements.txt --quiet

echo [3/5] Running tests...
pytest tests/ --alluredir=reports/allure-results -v --tb=short

echo [4/5] Generating Allure report...
where allure >nul 2>&1
if %ERRORLEVEL%==0 (
    allure generate reports\allure-results --clean -o reports\allure-report
    echo Allure report: reports\allure-report\index.html
) else (
    echo [SKIP] allure CLI not found. Install via: scoop install allure
)

echo [5/5] Done!
echo.
echo   Screenshots : .\screenshots\
echo   Logs        : .\logs\
echo   Allure HTML : .\reports\allure-report\index.html
pause
