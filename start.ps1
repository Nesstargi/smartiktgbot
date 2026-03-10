param(
    [switch]$InstallDeps,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvActivate = Join-Path $Root "venv\Scripts\Activate.ps1"

if (-not (Test-Path $VenvActivate)) {
    Write-Error "Virtual environment not found: $VenvActivate"
}

$backendPrefix = "& '$VenvActivate'; Set-Location '$Root'; "
$botPrefix = "& '$VenvActivate'; Set-Location '$Root'; "
$adminPrefix = "Set-Location '$Root\admin-panel'; "

$backendDeps = ""
$adminDeps = ""
if ($InstallDeps) {
    $backendDeps = "pip install -r requirements.txt; "
    $adminDeps = "if (!(Test-Path 'node_modules')) { npm install }; "
}

$backendCmd = $backendPrefix + $backendDeps + "uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000"
$adminCmd = $adminPrefix + $adminDeps + "npm run dev"
$botCmd = $botPrefix + "python -m bot.main"

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
