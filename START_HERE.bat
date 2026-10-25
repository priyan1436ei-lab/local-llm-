@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 -m localcoder.launch
    if errorlevel 1 pause
    exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
    python -m localcoder.launch
    if errorlevel 1 pause
    exit /b
)
echo Install Python 3.10 or newer from https://www.python.org/downloads/
echo Include the Windows launcher or select Add Python to PATH.
pause
