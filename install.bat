@echo off
setlocal EnableExtensions

rem Shop-floor importer installer for Windows.
rem Run this file from an ordinary Command Prompt; administrator rights are not needed.

cd /d "%~dp0"
echo.
echo === Shop-floor importer setup ===

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYTHON=py -3"
) else (
    where python >nul 2>nul
    if errorlevel 1 goto :missing_python
    set "PYTHON=python"
)

%PYTHON% -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)"
if errorlevel 1 goto :old_python

if not exist ".venv\Scripts\python.exe" (
    echo [1/5] Creating Python virtual environment...
    %PYTHON% -m venv .venv
    if errorlevel 1 goto :failed
) else (
    echo [1/5] Using existing Python virtual environment.
)

set "VENV_PYTHON=%CD%\.venv\Scripts\python.exe"

echo [2/5] Updating pip and build tools...
"%VENV_PYTHON%" -m pip install --upgrade pip setuptools wheel
if errorlevel 1 goto :failed

echo [3/5] Installing the importer and test tools...
"%VENV_PYTHON%" -m pip install -e ".[dev]"
if errorlevel 1 goto :failed

echo [4/5] Installing the Playwright Chromium browser...
"%VENV_PYTHON%" -m playwright install chromium
if errorlevel 1 goto :failed

echo [5/5] Generating anonymized example workbooks...
"%VENV_PYTHON%" examples\generate_workbooks.py
if errorlevel 1 goto :failed

echo.
echo Setup completed successfully.
echo.
echo Preview the measurement workbook with:
echo   .venv\Scripts\shopfloor-import.exe examples\anonymized_measurement_report.xlsx --config config\measurement-browser.yaml
echo.
echo IMPORTANT: Website submission is still blocked until authentication and the
echo real stable page selectors are configured. Do not put passwords in this file.
exit /b 0

:missing_python
echo.
echo ERROR: Python 3 was not found.
echo Install Python 3.11 or newer from https://www.python.org/downloads/windows/
echo Select "Add python.exe to PATH" during installation, then run install.bat again.
exit /b 1

:old_python
echo.
echo ERROR: Python 3.11 or newer is required.
echo Install a current version from https://www.python.org/downloads/windows/
echo and then run install.bat again.
exit /b 1

:failed
echo.
echo ERROR: Setup stopped because the command above failed.
echo Check the displayed error, your network/proxy settings, and available disk space.
exit /b 1
