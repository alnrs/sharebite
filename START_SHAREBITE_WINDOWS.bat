@echo off
setlocal
cd /d "%~dp0"
title ShareBite - AWS connected local website
where py >nul 2>nul
if not errorlevel 1 (
  py -3 "tools\run_local.py"
  goto :end
)
where python >nul 2>nul
if not errorlevel 1 (
  python "tools\run_local.py"
  goto :end
)
echo Python 3 is not installed. Install Python 3 or use VS Code ^> Open Folder ^> index.html ^> Open with Live Server.
echo Do not test Cognito or API from a file:// URL.
pause
:end
