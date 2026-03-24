param(
    [switch]$InstallDeps,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

$venvCandidates = @(
    (Join-Path $Root "venv311\Scripts\Activate.ps1"),
    (Join-Path $Root "venv\Scripts\Activate.ps1")
)
$VenvActivate = $venvCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if (-not $VenvActivate) {
    Write-Error "Virtual environment not found. Checked: $($venvCandidates -join ', ')"
}

$backendPrefix = "& '$VenvActivate'; Set-Location '$Root'; "
$botPrefix = "& '$VenvActivate'; Set-Location '$Root'; "
$adminPrefix = "Set-Location '$Root\admin-panel'; "
$sqlitePath = (Join-Path $Root "db.sqlite3").Replace("\", "/")
$backendEnv = '$env:DATABASE_URL=' + "'sqlite:///$sqlitePath'" + '; '
$botEnv = '$env:BACKEND_URL=' + "'http://127.0.0.1:8000'" + '; ' +
    '$env:REDIS_URL=' + "''" + '; ' +
    '$env:BOT_DELIVERY_MODE=' + "'polling'" + '; '
$adminEnv = '$env:VITE_API_URL=' + "'http://localhost:8000'" + '; '

$backendDeps = ""
$adminDeps = ""
if ($InstallDeps) {
    $backendDeps = "pip install -r requirements.txt; "
    $adminDeps = "if (!(Test-Path 'node_modules')) { npm install }; "
}

$backendCmd = $backendPrefix + $backendEnv + $backendDeps + "python -m alembic upgrade head; uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
$adminCmd = $adminPrefix + $adminEnv + $adminDeps + "npm run dev"
$botCmd = $botPrefix + $botEnv + "python -m bot.main"

Write-Host "Backend command: $backendCmd"
Write-Host "Admin command:   $adminCmd"
Write-Host "Bot command:     $botCmd"

if ($DryRun) {
    Write-Host "DryRun enabled: no new terminal windows were started."
    exit 0
}

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $backendCmd
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $adminCmd
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $botCmd

Write-Host "Started backend, admin-panel, and bot in separate terminals."
