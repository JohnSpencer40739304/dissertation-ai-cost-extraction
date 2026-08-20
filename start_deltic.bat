@echo off
title DelticAI

set "APP_DIR=%~dp0"

echo ========================================
echo        Starting DelticAI
echo ========================================
echo.

echo Starting FastAPI backend...
start "DelticAI Backend" cmd /k "cd /d "%APP_DIR%" && uvicorn backend.app.main:app"

timeout /t 3 /nobreak >nul

echo Starting Excel Add-in...
start "DelticAI Excel Add-in" cmd /k "cd /d "%APP_DIR%client\excel-addin\deltic-excel-addin" && npm.cmd start"

echo.
echo DelticAI startup commands launched.
echo Excel should open automatically.
echo.