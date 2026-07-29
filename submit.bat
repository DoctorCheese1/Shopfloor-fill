@echo off
setlocal EnableExtensions
cd /d "%~dp0"

if not exist ".venv\Scripts\shopfloor-import.exe" (
    echo ERROR: The importer is not installed. Run install.bat first.
    exit /b 1
)

set "WORKBOOK=%~1"
set "RECORD=%~2"
set "MACHINE=%~3"

if not defined WORKBOOK set /p "WORKBOOK=Full path to the Excel file: "
if not defined RECORD set /p "RECORD=Mold/report number, for example 9167: "
if not defined MACHINE set /p "MACHINE=Machine [A11 or A16]: "

if not exist "%WORKBOOK%" (
    echo ERROR: Excel file not found: "%WORKBOOK%"
    exit /b 1
)
if not defined RECORD (
    echo ERROR: A mold/report number is required.
    exit /b 1
)
if /I not "%MACHINE%"=="A11" if /I not "%MACHINE%"=="A16" (
    echo ERROR: Machine must be A11 or A16.
    exit /b 1
)

echo.
echo Excel file : %WORKBOOK%
echo Mold/report: %RECORD%
echo Machine    : %MACHINE%
echo.
echo Running validation preview. Nothing will be submitted...
echo.

".venv\Scripts\shopfloor-import.exe" "%WORKBOOK%" ^
  --config config\measurement-browser.yaml ^
  --record "%RECORD%" --machine "%MACHINE%"
if errorlevel 1 (
    echo.
    echo ERROR: Preview failed. Review the row errors above; nothing was submitted.
    exit /b 1
)

echo.
echo Preview passed. Review the preview and CSV report above.
echo Press Enter to stop without writing, or type SUBMIT to send these rows.
set "CONFIRM="
set /p "CONFIRM=Confirmation: "
if not "%CONFIRM%"=="SUBMIT" (
    echo Preview only; nothing was submitted.
    exit /b 0
)

echo.
echo Submitting mold/report %RECORD% for machine %MACHINE%...
".venv\Scripts\shopfloor-import.exe" "%WORKBOOK%" ^
  --config config\measurement-browser.yaml ^
  --record "%RECORD%" --machine "%MACHINE%" ^
  --submit --confirm SUBMIT
if errorlevel 1 (
    echo.
    echo ERROR: Submission did not complete. Review the per-row results above.
    echo Authentication is currently pending until the website login flow and
    echo stable page selectors are supplied.
    exit /b 1
)

echo Submission completed. Review the per-row CSV report before closing this window.
exit /b 0
