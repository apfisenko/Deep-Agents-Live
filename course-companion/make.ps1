param([string]$Target = "help")

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = $PSScriptRoot
$Logs = Join-Path $Root ".logs"
$Jobs = 10

function Ensure-LogsDir {
    if (-not (Test-Path $Logs)) {
        New-Item -ItemType Directory -Path $Logs | Out-Null
    }
}

$script:DockerLikeProcess = '^(docker|wslrelay|vmwp|com\.docker\.backend|Docker Desktop|vmmemWSL)$'
$script:ComposePorts = @(2024, 2025, 5173)

function Test-DockerOwnsComposePorts {
    foreach ($port in $script:ComposePorts) {
        $listeners = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
        if (-not $listeners) { return $false }
        $owns = $false
        foreach ($conn in $listeners) {
            if ($conn.OwningProcess -le 0) { continue }
            $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
            if ($proc -and $proc.ProcessName -match $script:DockerLikeProcess) {
                $owns = $true
                break
            }
        }
        if (-not $owns) { return $false }
    }
    return $true
}

function Stop-Port {
    param([int[]]$Ports)
    if (Test-DockerOwnsComposePorts) {
        Write-Host "Порты 2024/2025/5173 заняты Docker (compose) — stop пропущен." -ForegroundColor Yellow
        Write-Host "Используйте: .\make.ps1 compose-down" -ForegroundColor Yellow
        return
    }
    foreach ($port in $Ports) {
        Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
            ForEach-Object {
                if ($_.OwningProcess -le 0) { return }
                $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                if (-not $proc) { return }
                if ($proc.ProcessName -match $script:DockerLikeProcess) {
                    Write-Host "Порт $port занят $($proc.ProcessName) (compose/docker) — не трогаем." -ForegroundColor Yellow
                    return
                }
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
    }
}

function Clear-PortDevProcesses {
    param([int[]]$Ports)
    if (Test-DockerOwnsComposePorts) {
        Write-Host "Compose уже слушает 2024/2025/5173 — dev-процессы на портах не трогаем." -ForegroundColor DarkGray
        return
    }
    foreach ($port in $Ports) {
        Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
            ForEach-Object {
                if ($_.OwningProcess -le 0) { return }
                $proc = Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
                if (-not $proc) { return }
                if ($proc.ProcessName -match $script:DockerLikeProcess) { return }
                Write-Host "Освобождаем порт $port : $($proc.ProcessName) (pid $($proc.Id))"
                Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
            }
    }
}

function Assert-ComposeNotRunning {
    param([string]$TargetName)
    if (Test-ComposeRunning) {
        Write-Host "Compose активен — $TargetName конфликтует с портами 2024/2025/5173." -ForegroundColor Yellow
        Write-Host "Сначала: .\make.ps1 compose-down  или используйте compose-status" -ForegroundColor Yellow
        exit 1
    }
}

function Get-WslPath {
    param([string]$WinPath)
    $normalized = ($WinPath -replace '\\', '/').TrimEnd('/')
    if ($normalized -match '^([A-Za-z]):/(.*)$') {
        return "/mnt/$($Matches[1].ToLower())/$($Matches[2])"
    }
    throw "Cannot convert path to WSL: $WinPath"
}

function Invoke-Compose {
    param([string]$Command)
    $wslRoot = Get-WslPath $Root
    wsl bash -lc "cd '$wslRoot' && docker compose $Command"
}

function Test-ComposeRunning {
    $wslRoot = Get-WslPath $Root
    $ids = wsl bash -lc "cd '$wslRoot' && docker compose ps --status running -q 2>/dev/null"
    return -not [string]::IsNullOrWhiteSpace($ids)
}

function Start-BackgroundCmd {
    param(
        [string]$Command,
        [string]$WorkingDirectory = $Root
    )
    Start-Process -FilePath "cmd.exe" -ArgumentList @("/c", $Command) -WorkingDirectory $WorkingDirectory -WindowStyle Hidden
}

switch ($Target) {
    "dev" {
        Assert-ComposeNotRunning -TargetName "dev"
        Ensure-LogsDir
        if (-not (Test-Path (Join-Path $Root "frontend\node_modules"))) {
            Write-Host "Сначала: cd frontend && npm install" -ForegroundColor Yellow
            exit 1
        }
        $serverLog = Join-Path $Logs "server.log"
        $frontendLog = Join-Path $Logs "frontend.log"
        Start-BackgroundCmd "uv run langgraph dev --no-reload --no-browser --n-jobs-per-worker $Jobs > `"$serverLog`" 2>&1"
        Start-BackgroundCmd "npm run dev > `"$frontendLog`" 2>&1" (Join-Path $Root "frontend")
        Write-Host "Agent Server (оба графа): http://localhost:2024/info · лог: $serverLog"
        Write-Host "веб-чат:                  http://localhost:5173 · лог: $frontendLog"
        Write-Host "готовность: curl -s localhost:2024/info · погасить: .\make.ps1 stop"
    }
    "checker" {
        Assert-ComposeNotRunning -TargetName "checker"
        Ensure-LogsDir
        $checkerLog = Join-Path $Logs "checker.log"
        Start-BackgroundCmd "uv run langgraph dev --config langgraph.checker.json --port 2025 --no-reload --no-browser --n-jobs-per-worker $Jobs > `"$checkerLog`" 2>&1"
        Write-Host "checker: http://localhost:2025/info · лог: $checkerLog · погасить: .\make.ps1 stop"
    }
    "companion" {
        Assert-ComposeNotRunning -TargetName "companion"
        Ensure-LogsDir
        $companionLog = Join-Path $Logs "companion.log"
        Start-BackgroundCmd "set CHECKER_URL=http://localhost:2025&& uv run langgraph dev --config langgraph.companion.json --no-reload --no-browser --n-jobs-per-worker $Jobs > `"$companionLog`" 2>&1"
        Write-Host "companion: http://localhost:2024/info · лог: $companionLog · CHECKER_URL=http://localhost:2025"
    }
    "frontend" {
        Assert-ComposeNotRunning -TargetName "frontend"
        Ensure-LogsDir
        if (-not (Test-Path (Join-Path $Root "frontend\node_modules"))) {
            Write-Host "Сначала: cd frontend && npm install" -ForegroundColor Yellow
            exit 1
        }
        $frontendLog = Join-Path $Logs "frontend.log"
        Start-BackgroundCmd "set CHECKER_PROXY_TARGET=http://127.0.0.1:2025&& npm run dev > `"$frontendLog`" 2>&1" (Join-Path $Root "frontend")
        Write-Host "веб-чат: http://localhost:5173 · CHECKER_PROXY_TARGET=http://127.0.0.1:2025 · лог: $frontendLog"
    }
    "stop" {
        if (Test-ComposeRunning -or (Test-DockerOwnsComposePorts)) {
            Write-Host "Compose контейнеры активны — stop убьёт Docker-proxy на портах 2024/2025/5173." -ForegroundColor Yellow
            Write-Host "Используйте: .\make.ps1 compose-down" -ForegroundColor Yellow
            exit 1
        }
        Stop-Port -Ports $script:ComposePorts
        Write-Host "порты 2024/2025/5173 свободны"
    }
    "compose-ensure" {
        if (Test-ComposeRunning) {
            Write-Host "Compose уже running — OK"
            & "$Root\make.ps1" compose-status
            exit $LASTEXITCODE
        }
        & "$Root\make.ps1" compose-up
        exit $LASTEXITCODE
    }
    "compose-up" {
        Clear-PortDevProcesses -Ports @(2024, 2025, 5173)
        Invoke-Compose "up -d --remove-orphans"
        Write-Host "веб-чат: http://localhost:5173 · companion: :2024 · checker: :2025"
        Write-Host "проверка: .\make.ps1 compose-status"
    }
    "compose-up-build" {
        Clear-PortDevProcesses -Ports @(2024, 2025, 5173)
        Invoke-Compose "up -d --build --remove-orphans"
        Write-Host "веб-чат: http://localhost:5173 · companion: :2024 · checker: :2025"
        Write-Host "проверка: .\make.ps1 compose-status"
    }
    "compose-down" {
        Invoke-Compose "down"
    }
    "compose-status" {
        $wslRoot = Get-WslPath $Root
        wsl bash -lc "cd '$wslRoot' && bash scripts/compose-status.sh"
        exit $LASTEXITCODE
    }
    "cli" { uv run companion }
    "test" { uv run pytest tests/ -v }
    "lint" {
        uv run ruff check src/ tests/
        Push-Location (Join-Path $Root "frontend")
        npx tsc --noEmit
        Pop-Location
    }
    "format" { uv run ruff format src/ tests/ }
    "typecheck" { uv run mypy src/ }
    "ci" {
        & "$Root\make.ps1" lint
        & "$Root\make.ps1" typecheck
        & "$Root\make.ps1" test
    }
    default {
        Write-Host "Targets: dev  checker  companion  frontend  stop  compose-up  compose-up-build  compose-down  compose-ensure  compose-status  cli  test  lint  format  typecheck  ci"
    }
}
