# ============================================================================
# GTI ADMIN DASHBOARD — desktop shortcut installer (run this once)
#
# Creates a "GTI Admin Dashboard" shortcut on your Windows Desktop that
# points at start-admin.bat in this same folder. After running this
# once, double-clicking that desktop icon starts the backend, checks
# the database, and opens the admin login page — no terminal, VS Code,
# or manual commands needed.
#
# Safe to run more than once — it just overwrites the same shortcut.
# ============================================================================

$root = $PSScriptRoot
$batPath = Join-Path $root "start-admin.bat"

if (-not (Test-Path $batPath)) {
    Write-Host "start-admin.bat was not found next to this script. Nothing created." -ForegroundColor Red
    Read-Host "Press Enter to close"
    exit 1
}

$desktop = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktop "GTI Admin Dashboard.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $batPath
$shortcut.WorkingDirectory = $root
$shortcut.WindowStyle = 1
$shortcut.Description = "Start the GTI Admin Dashboard (checks the database, starts Flask, opens the admin login page)"

# Use the project's own logo as the shortcut icon if one exists, so it's
# recognizable on the desktop; falls back to the default .bat icon.
$iconCandidate = Join-Path $root "..\build10\assets\images\logo\favicon.ico"
if (Test-Path $iconCandidate) {
    $shortcut.IconLocation = $iconCandidate
}

$shortcut.Save()

Write-Host ""
Write-Host "Created desktop shortcut:" -ForegroundColor Green
Write-Host "  $shortcutPath"
Write-Host ""
Write-Host "Double-click 'GTI Admin Dashboard' on your Desktop any time to start it." -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to close"
