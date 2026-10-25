@echo off
cd /d "%~dp0"
py -3 -m localcoder.web
if errorlevel 1 pause
