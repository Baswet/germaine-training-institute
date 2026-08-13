@echo off
REM ============================================================================
REM GTI ADMIN DASHBOARD — double-click launcher
REM
REM Runs start-admin.ps1 from this same folder, regardless of where this
REM .bat file is double-clicked from. No manual "cd" or PowerShell window
REM needs to be opened first.
REM ============================================================================

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start-admin.ps1"
