@echo off
REM NoYou one-command dev launcher — runs dev.ps1 (backend :8000 + dashboard :3002)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0dev.ps1"
