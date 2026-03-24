param(
    [string]$Branch = "main",
    [string]$Remote = "origin",
    [switch]$SkipBuild,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Invoke-External {
    param(
        [string]$FilePath,
        [string[]]$Arguments = @()
    )

    $display = ($Arguments | ForEach-Object {
        if ($_ -match "\s") {
            '"' + $_ + '"'
        } else {
            $_
        }
    }) -join " "

    Write-Host "> $FilePath $display"

    if ($DryRun) {
        return
    }

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $FilePath $display"
    }
}

if (-not (Test-Path ".git")) {
    throw "This folder is not a git repository. Clone the project from git first."
}

if (-not (Test-Command "git")) {
    throw "git is not installed or not available in PATH."
}

if (-not (Test-Command "docker")) {
    throw "docker is not installed or not available in PATH."
}

if (-not (Test-Path ".env")) {
    Write-Warning ".env was not found in the repository root. Docker Compose may fail to start."
}

$trackedChanges = @(& git status --porcelain --untracked-files=no) | Where-Object { $_ }
if ($trackedChanges.Count -gt 0) {
    throw "Tracked local changes detected. Commit, stash, or revert them before deployment."
}

$currentBranch = ((& git branch --show-current) | Select-Object -First 1).Trim()
if (-not $currentBranch) {
    throw "Could not determine the current git branch."
}

Invoke-External "git" @("fetch", $Remote, $Branch)

if ($currentBranch -ne $Branch) {
    Invoke-External "git" @("checkout", $Branch)
}

Invoke-External "git" @("pull", "--ff-only", $Remote, $Branch)

$composeArgs = @("compose", "up", "-d")
if (-not $SkipBuild) {
    $composeArgs += "--build"
}

Invoke-External "docker" $composeArgs
Invoke-External "docker" @("compose", "ps")

Write-Host ""
Write-Host "Deployment finished."
