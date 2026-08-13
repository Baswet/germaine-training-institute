# ============================================================================
# GTI ADMIN DASHBOARD — one-click startup
#
# What this does, in order:
#   1. Locates this project's virtual environment (.venv) relative to this
#      script's own location, so it works no matter where it is launched
#      from — no manual "cd" required.
#   2. Verifies required Python dependencies are installed (installs them
#      from requirements.txt if missing — never touches anything outside
#      this project's own .venv).
#   3. Verifies a .env configuration file exists (refuses to guess or
#      fabricate DATABASE_URL / SECRET_KEY — those are yours to set).
#   4. Runs a lightweight PostgreSQL connectivity check BEFORE starting
#      Flask, so a database that is down produces one clear line instead
#      of a long Flask/SQLAlchemy traceback.
#   5. Checks whether the applied Alembic migration matches the latest
#      migration file. If the database is behind, this script STOPS and
#      tells you the exact command to run — it never runs a migration for
#      you automatically.
#   6. Starts the Flask dev server (if one isn't already running on the
#      configured port) in its own window, waits for /health to report
#      "ok", then opens http://127.0.0.1:<port>/admin/login in your
#      default browser.
#
# This script never creates, modifies, or deletes database data, never
# hardcodes credentials, and never weakens the existing admin
# authentication. It only automates the steps you'd otherwise type by
# hand every time.
# ============================================================================

$ErrorActionPreference = "Stop"

function Write-Banner($text) {
    Write-Host ""
    Write-Host $text -ForegroundColor Cyan
}

function Fail($message) {
    Write-Host ""
    Write-Host $message -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to close this window"
    exit 1
}

# ---------------------------------------------------------------------------
# 1. Locate the project root (this script's own folder) and the venv.
# ---------------------------------------------------------------------------
$root = $PSScriptRoot
Set-Location $root

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Fail @"
GTI ADMIN DASHBOARD — cannot start

No virtual environment was found at:
  $root\.venv

Create it first (one-time setup), from a terminal in this folder:
  python -m venv .venv
  .venv\Scripts\pip install -r requirements.txt

Then double-click start-admin.bat again.
"@
}

Write-Banner "GTI ADMIN DASHBOARD — starting..."
Write-Host "Project folder : $root"
Write-Host "Python (venv)  : $venvPython"

# ---------------------------------------------------------------------------
# 2. Verify required dependencies are installed; install if missing.
# ---------------------------------------------------------------------------
& $venvPython -c "import flask, flask_sqlalchemy, flask_migrate, psycopg, dotenv" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Some dependencies are missing — installing from requirements.txt ..." -ForegroundColor Yellow
    & $venvPython -m pip install -r (Join-Path $root "requirements.txt")
    if ($LASTEXITCODE -ne 0) {
        Fail "GTI ADMIN DASHBOARD — dependency installation failed. Check the output above."
    }
}

# ---------------------------------------------------------------------------
# 3. Verify configuration exists. Never fabricate secrets.
# ---------------------------------------------------------------------------
$envFile = Join-Path $root ".env"
if (-not (Test-Path $envFile)) {
    Fail @"
GTI ADMIN DASHBOARD — cannot start

No .env file was found at:
  $envFile

Copy .env.example to .env and fill in your real values
(SECRET_KEY, DATABASE_URL, etc.) — this script will not guess or
create these for you.
"@
}

# Read DATABASE_URL / FLASK_RUN_PORT out of .env without executing it.
$envLines = Get-Content $envFile | Where-Object { $_ -match "^\s*[A-Za-z_][A-Za-z0-9_]*\s*=" }
$envMap = @{}
foreach ($line in $envLines) {
    $parts = $line -split "=", 2
    $envMap[$parts[0].Trim()] = $parts[1].Trim()
}

$port = 5000
if ($envMap.ContainsKey("FLASK_RUN_PORT") -and $envMap["FLASK_RUN_PORT"]) {
    $port = $envMap["FLASK_RUN_PORT"]
}
$baseUrl = "http://127.0.0.1:$port"

$env:FLASK_APP = "wsgi.py"

# ---------------------------------------------------------------------------
# 4 + 5. Database connectivity AND migration-state check, in one call.
#         See scripts/preflight_check.py — read-only, never alters
#         anything, never auto-runs a migration.
# ---------------------------------------------------------------------------
Write-Host "Checking database connectivity and migration state..."
$preflightScript = Join-Path $root "scripts\preflight_check.py"
$preflightOutput = & $venvPython $preflightScript 2>$null | Select-Object -Last 1
$preflightWords = "$preflightOutput" -split "\s+"
$preflightStatus = $preflightWords[0]

switch ($preflightStatus) {
    "NO_DATABASE_URL" {
        Fail @"
GTI ADMIN DASHBOARD — cannot start

DATABASE_URL is not set in .env. Set it to your PostgreSQL connection
string (see .env.example for the expected shape) and try again.
"@
    }
    "DB_UNAVAILABLE" {
        Fail @"
GTI DATABASE IS NOT AVAILABLE

Could not connect to PostgreSQL using the DATABASE_URL configured in
.env. Nothing was started, changed, or deleted.

Check that:
  - PostgreSQL is running
  - DATABASE_URL in .env points at the correct host/port/database
  - the database user/password are correct
"@
    }
    "MIGRATIONS_PENDING" {
        $foundRev = $preflightWords[1]
        $headRevOut = $preflightWords[2]
        Fail @"
Pending GTI database migrations detected.
Run the migration command before opening the dashboard:

  $venvPython -m flask db upgrade

Database revision found : $foundRev
Latest migration file   : $headRevOut

Nothing was changed automatically. This script only detects pending
migrations — it never runs them for you.
"@
    }
    "OK" {
        Write-Host "Database connection OK. Migrations up to date ($($preflightWords[1]))." -ForegroundColor Green
    }
    default {
        Fail @"
GTI ADMIN DASHBOARD — preflight check failed

scripts\preflight_check.py did not return a recognized result:
  $preflightOutput

Nothing was started. Run it directly for the full error:
  $venvPython scripts\preflight_check.py
"@
    }
}

# ---------------------------------------------------------------------------
# 6. Start Flask (skip if already running), wait for /health, open browser.
# ---------------------------------------------------------------------------
function Test-HealthOk {
    try {
        $resp = Invoke-WebRequest -Uri "$baseUrl/health" -UseBasicParsing -TimeoutSec 2
        return $resp.StatusCode -eq 200
    } catch {
        return $false
    }
}

if (Test-HealthOk) {
    Write-Host "A GTI backend server is already running on port $port — reusing it." -ForegroundColor Yellow
} else {
    Write-Host "Starting Flask server on port $port ..."
    $flaskArgs = @("-m", "flask", "run", "--port", "$port")
    Start-Process -FilePath $venvPython -ArgumentList $flaskArgs -WorkingDirectory $root -WindowStyle Normal

    $ready = $false
    for ($i = 0; $i -lt 40; $i++) {
        Start-Sleep -Seconds 1
        if (Test-HealthOk) { $ready = $true; break }
    }

    if (-not $ready) {
        Fail @"
GTI ADMIN DASHBOARD — server did not become ready

Flask was started but $baseUrl/health did not respond successfully
within 40 seconds. Check the newly opened server window for the
actual error.
"@
    }
}

Start-Process $baseUrl/admin/login

Write-Banner "GTI ADMIN DASHBOARD"
Write-Host "Server:       $baseUrl" -ForegroundColor Green
Write-Host "Admin Login:  $baseUrl/admin/login" -ForegroundColor Green
Write-Host ""
Write-Host "The Flask server keeps running in its own window — close that" -ForegroundColor DarkGray
Write-Host "window (or press Ctrl+C in it) to stop the GTI backend." -ForegroundColor DarkGray
Write-Host ""
Read-Host "This window can be closed (press Enter to close it now)"
