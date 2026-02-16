# start_shard.ps1 — Shard Alpha (West Node) Persistence Launcher
# Usage: powershell -File start_shard.ps1
# Keeps the Shard API alive on port 8001. Restarts on crash with backoff.

$ErrorActionPreference = "Stop"
$ShardDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$MaxRetries = 5
$BaseDelay = 2  # seconds

Set-Location $ShardDir

Write-Host "[SHARD] West Node launcher initialized" -ForegroundColor Cyan
Write-Host "[SHARD] Directory: $ShardDir"
Write-Host "[SHARD] Target: port 8001"

$retries = 0

while ($retries -lt $MaxRetries) {
    Write-Host "[SHARD] Starting shard_api.py (attempt $($retries + 1)/$MaxRetries)..." -ForegroundColor Yellow

    try {
        python shard_api.py
        $exitCode = $LASTEXITCODE
        Write-Host "[SHARD] Process exited with code $exitCode" -ForegroundColor Red
    }
    catch {
        Write-Host "[SHARD] Process crashed: $_" -ForegroundColor Red
    }

    $retries++

    if ($retries -lt $MaxRetries) {
        $delay = $BaseDelay * [Math]::Pow(2, $retries - 1)
        Write-Host "[SHARD] Restarting in $delay seconds..." -ForegroundColor Yellow
        Start-Sleep -Seconds $delay
    }
}

Write-Host "[SHARD] HALT: Max retries ($MaxRetries) exceeded. West Node is DOWN." -ForegroundColor Red
Write-Host "[SHARD] Manual intervention required." -ForegroundColor Red
exit 1
