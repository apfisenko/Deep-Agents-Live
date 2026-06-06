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

function Show-Help {
    Write-Host "Deep-Agents-Live - available targets:"
    Write-Host "  dev            - start backend + frontend + bot (3 windows)"
    Write-Host "  dev-backend    - Agent Core (uvicorn :8000)"
    Write-Host "  dev-frontend   - Next.js widget (sprint-03)"
    Write-Host "  dev-bot        - Telegram bot (sprint-04)"
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
    "dev" {
        Start-Process powershell -ArgumentList "-NoExit", "-File", $PSCommandPath, "dev-backend"
        Start-Process powershell -ArgumentList "-NoExit", "-File", $PSCommandPath, "dev-frontend"
        Start-Process powershell -ArgumentList "-NoExit", "-File", $PSCommandPath, "dev-bot"
        Write-Host "Started dev-backend, dev-frontend, dev-bot in separate windows"
    }
    "dev-backend" {
        Push-Location $BackendDir
        try {
            uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
        } finally {
            Pop-Location
        }
    }
    "dev-frontend" {
        Push-Location $FrontendDir
        try {
            pnpm dev
        } finally {
            Pop-Location
        }
    }
    "dev-bot" {
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
