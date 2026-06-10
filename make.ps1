param(
    [Parameter(Position = 0)]
    [string]$Target = "help",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$DockerArgs
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
$BackendDir = Join-Path $RepoRoot "backend"
$FrontendDir = Join-Path $RepoRoot "frontend"
$BotDir = Join-Path $RepoRoot "frontend\bot"

function Get-WslRepoPath {
    if ($env:REPO_WSL_PATH) {
        return $env:REPO_WSL_PATH.TrimEnd("/")
    }
    $path = $RepoRoot -replace '\\', '/'
    if ($path -match '^([A-Za-z]):/(.*)$') {
        $drive = $matches[1].ToLower()
        return "/mnt/$drive/$($matches[2])"
    }
    return $path
}

function Invoke-WslDocker {
    param([string]$Command)
    $wslPath = Get-WslRepoPath
    wsl -e bash -lc "cd '$wslPath' && $Command"
}

function Stop-ProcessOnPort {
    param([int]$Port)
    $pids = @()
    netstat -ano | ForEach-Object {
        if ($_ -match ":\s*$Port\s+.*LISTENING\s+(\d+)\s*$") {
            $pids += [int]$matches[1]
        }
    }
    $pids = $pids | Select-Object -Unique
    foreach ($procId in $pids) {
        if ($procId -gt 0) {
            Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped PID $procId (port $Port)"
        }
    }
    if ($pids.Count -eq 0) {
        Write-Host "No process listening on port $Port"
    }
}

function Stop-ProcessByCommandPattern {
    param([string]$Pattern, [string]$Label)
    $matched = $false
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine -match $Pattern } |
        ForEach-Object {
            $matched = $true
            Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
            Write-Host "Stopped $Label (PID $($_.ProcessId))"
        }
    if (-not $matched) {
        Write-Host "No $Label process found"
    }
}

function Stop-BackendDev {
    Write-Host "Stopping backend..."
    Stop-ProcessOnPort -Port 8000
    Stop-ProcessByCommandPattern -Pattern "uvicorn.*app\.main:app" -Label "backend (uvicorn)"
}

function Stop-FrontendDev {
    Write-Host "Stopping frontend..."
    Stop-ProcessOnPort -Port 3000
    Stop-ProcessByCommandPattern -Pattern "next dev" -Label "frontend (next dev)"
}

function Stop-ProcessTree {
    param([int]$RootPid)
    $queue = [System.Collections.Generic.Queue[int]]::new()
    $queue.Enqueue($RootPid)
    $seen = @{}
    while ($queue.Count -gt 0) {
        $procId = $queue.Dequeue()
        if ($seen.ContainsKey($procId)) { continue }
        $seen[$procId] = $true
        Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
            Where-Object { $_.ParentProcessId -eq $procId } |
            ForEach-Object { $queue.Enqueue($_.ProcessId) }
    }
    foreach ($procId in $seen.Keys) {
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
        Write-Host "Stopped telegram bot process tree (PID $procId)"
    }
}

function Stop-BotDev {
    Write-Host "Stopping telegram bot..."
    $rootPids = @()
    Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | ForEach-Object {
        $cmd = $_.CommandLine
        if (-not $cmd) { return }
        if ($cmd -match "frontend[\\/]bot[\\/]\.venv" -or $cmd -match "uv\.exe.*run python main\.py") {
            $rootPids += $_.ProcessId
        }
    }
    $rootPids = $rootPids | Select-Object -Unique
    if ($rootPids.Count -eq 0) {
        Write-Host "No telegram bot process found"
        return
    }
    foreach ($rootPid in $rootPids) {
        Stop-ProcessTree -RootPid $rootPid
    }
}

function Show-Help {
    Write-Host "Deep-Agents-Live - available targets:"
    Write-Host "  dev            - start backend + frontend + bot (3 windows)"
    Write-Host "  dev-backend    - Agent Core (uvicorn :8000)"
    Write-Host "  dev-frontend   - Next.js widget (sprint-03)"
    Write-Host "  dev-bot        - Telegram bot (sprint-04)"
    Write-Host "  stop-dev       - stop backend + frontend + bot"
    Write-Host "  stop-backend   - stop uvicorn on :8000"
    Write-Host "  stop-frontend  - stop Next.js on :3000"
    Write-Host "  stop-bot       - stop Telegram bot (main.py)"
    Write-Host "  lint           - ruff + eslint"
    Write-Host "  format         - ruff format backend"
    Write-Host "  typecheck      - mypy + tsc"
    Write-Host "  test           - backend + frontend + bot tests"
    Write-Host "  test-backend   - pytest backend"
    Write-Host "  test-frontend  - vitest frontend"
    Write-Host "  test-bot       - pytest bot"
    Write-Host "  up             - docker compose up -d (WSL)"
    Write-Host "  down           - docker compose down (WSL)"
    Write-Host "  ps / status    - docker compose ps (WSL)"
    Write-Host "  logs           - docker compose logs [--tail N] [service]"
    Write-Host "  compose        - docker compose <args>"
    Write-Host "  docker         - docker <args>"
    Write-Host "  ci             - lint + typecheck + test"
    Write-Host "  compose-dev    - full stack in compose (sprint-04)"
    Write-Host "  check-health   - GET /health (backend must be running)"
    Write-Host "  check-reindex  - POST /admin/reindex"
    Write-Host "  check-chat     - POST /api/v1/chat (telegram)"
    Write-Host "  check-chat-stream - POST /api/v1/chat/stream (SSE)"
    Write-Host "  check-langfuse - Langfuse /api/public/health"
    Write-Host "  check-telegram - TCP/getMe to api.telegram.org (VPN/proxy)"
    Write-Host "  check-api      - all checks above"
    Write-Host "  chat-telegram  - POST /api/v1/chat (telegram JSON, raw output)"
    Write-Host "  chat-stream    - POST /api/v1/chat/stream (web SSE, raw output)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\make.ps1 ps"
    Write-Host "  .\make.ps1 compose logs -f langfuse-web"
    Write-Host "  .\make.ps1 docker ps -a"
    Write-Host "  .\make.ps1 check-api"
}

function Invoke-RequestChat {
    param([string]$Command)
    Push-Location $BackendDir
    try {
        uv run python scripts/request_chat.py $Command
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
}

function Invoke-CheckApi {
    param([string]$Command)
    Push-Location $BackendDir
    try {
        uv run python scripts/check_api.py $Command
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
}

switch ($Target) {
    "help" { Show-Help }
    "stop-dev" {
        Stop-BackendDev
        Stop-FrontendDev
        Stop-BotDev
    }
    "stop-backend" { Stop-BackendDev }
    "stop-frontend" { Stop-FrontendDev }
    "stop-bot" { Stop-BotDev }
    "dev" {
        & $PSCommandPath stop-dev
        Start-Process powershell -ArgumentList "-NoExit", "-File", $PSCommandPath, "dev-backend"
        Start-Process powershell -ArgumentList "-NoExit", "-File", $PSCommandPath, "dev-frontend"
        Start-Process powershell -ArgumentList "-NoExit", "-File", $PSCommandPath, "dev-bot"
        Write-Host "Started dev-backend, dev-frontend, dev-bot in separate windows"
    }
    "dev-backend" {
        Stop-BackendDev
        Push-Location $BackendDir
        try {
            uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        } finally {
            Pop-Location
        }
    }
    "dev-frontend" {
        Stop-FrontendDev
        Push-Location $FrontendDir
        try {
            pnpm dev
        } finally {
            Pop-Location
        }
    }
    "dev-bot" {
        Stop-BotDev
        Push-Location $BotDir
        try {
            uv run python main.py
        } finally {
            Pop-Location
        }
    }
    "lint" {
        Push-Location $BackendDir
        try {
            uv run ruff check app tests
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } finally {
            Pop-Location
        }
        Push-Location $FrontendDir
        try {
            pnpm lint
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } finally {
            Pop-Location
        }
        Push-Location $BotDir
        try {
            uv run ruff check .
        } finally {
            Pop-Location
        }
    }
    "format" {
        Push-Location $BackendDir
        try {
            uv run ruff format app tests
        } finally {
            Pop-Location
        }
    }
    "typecheck" {
        Push-Location $BackendDir
        try {
            uv run mypy app
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } finally {
            Pop-Location
        }
        Push-Location $FrontendDir
        try {
            pnpm typecheck
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } finally {
            Pop-Location
        }
        Push-Location $BotDir
        try {
            uv run mypy .
        } finally {
            Pop-Location
        }
    }
    "test" {
        & $PSCommandPath test-backend
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $PSCommandPath test-frontend
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $PSCommandPath test-bot
    }
    "test-backend" {
        Push-Location $BackendDir
        try {
            uv run pytest
        } finally {
            Pop-Location
        }
    }
    "test-frontend" {
        Push-Location $FrontendDir
        try {
            pnpm test
        } finally {
            Pop-Location
        }
    }
    "test-bot" {
        Push-Location $BotDir
        try {
            uv run pytest
        } finally {
            Pop-Location
        }
    }
    "up" {
        Invoke-WslDocker "docker compose up -d"
    }
    "down" {
        Invoke-WslDocker "docker compose down"
    }
    "ps" {
        Invoke-WslDocker "docker compose ps"
    }
    "status" {
        Invoke-WslDocker "docker compose ps"
    }
    "logs" {
        if ($DockerArgs.Count -eq 0) {
            Invoke-WslDocker "docker compose logs --tail 50"
        } else {
            $cmd = "docker compose logs " + ($DockerArgs -join " ")
            Invoke-WslDocker $cmd
        }
    }
    "compose" {
        if ($DockerArgs.Count -eq 0) {
            Write-Error "Usage: .\make.ps1 compose <args>   e.g. .\make.ps1 compose ps"
        }
        $cmd = "docker compose " + ($DockerArgs -join " ")
        Invoke-WslDocker $cmd
    }
    "docker" {
        if ($DockerArgs.Count -eq 0) {
            Write-Error "Usage: .\make.ps1 docker <args>   e.g. .\make.ps1 docker ps -a"
        }
        $cmd = "docker " + ($DockerArgs -join " ")
        Invoke-WslDocker $cmd
    }
    "migrate" {
        Write-Error "Not implemented - Postgres is out of MVP scope (ADR-0002)"
    }
    "migrate-new" {
        Write-Error "Not implemented - Postgres is out of MVP scope (ADR-0002)"
    }
    "ci" {
        & $PSCommandPath lint
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $PSCommandPath typecheck
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & $PSCommandPath test
    }
    "compose-dev" {
        Invoke-WslDocker "docker compose --profile full up -d --build"
    }
    "compose-down" {
        Invoke-WslDocker "docker compose --profile full down"
    }
    "check-health" { Invoke-CheckApi "health" }
    "check-reindex" { Invoke-CheckApi "reindex" }
    "check-chat" { Invoke-CheckApi "chat" }
    "check-chat-stream" { Invoke-CheckApi "chat-stream" }
    "check-langfuse" { Invoke-CheckApi "langfuse" }
    "check-telegram" {
        Push-Location (Join-Path $RepoRoot "frontend\bot")
        try {
            uv sync --quiet 2>$null
            uv run python -m scripts.check_telegram
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        } finally {
            Pop-Location
        }
    }
    "check-api" { Invoke-CheckApi "api" }
    "chat-telegram" { Invoke-RequestChat "telegram" }
    "chat-stream" { Invoke-RequestChat "stream" }
    default {
        Write-Error "Unknown target: $Target. Run: .\make.ps1 help"
    }
}
