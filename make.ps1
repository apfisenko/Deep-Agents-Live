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
$EvalsDir = Join-Path $RepoRoot "evals"

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

function Test-QdrantHealth {
    param([string]$BaseUrl)
    try {
        $uri = "$($BaseUrl.TrimEnd('/'))/healthz"
        $response = Invoke-WebRequest -Uri $uri -UseBasicParsing -TimeoutSec 3
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Test-Neo4jBoltPort {
    param([string]$HostName, [int]$Port = 7687)
    try {
        $client = New-Object System.Net.Sockets.TcpClient
        $async = $client.BeginConnect($HostName, $Port, $null, $null)
        $ok = $async.AsyncWaitHandle.WaitOne(3000, $false)
        if (-not $ok) {
            $client.Close()
            return $false
        }
        $client.EndConnect($async)
        $client.Close()
        return $true
    } catch {
        return $false
    }
}

function Resolve-Neo4jUriForWindows {
    $configured = if ($env:NEO4J_URI) { $env:NEO4J_URI } else { "bolt://localhost:7687" }
    if ($configured -notmatch 'localhost|127\.0\.0\.1') {
        return $configured
    }

    if (Test-Neo4jBoltPort "127.0.0.1") {
        return "bolt://127.0.0.1:7687"
    }

    $wslIp = (wsl hostname -I).Split()[0].Trim()
    if ($wslIp -and (Test-Neo4jBoltPort $wslIp)) {
        Write-Host "Neo4j: using WSL host bolt://${wslIp}:7687 (localhost unreachable from Windows)"
        return "bolt://${wslIp}:7687"
    }

    return $configured
}

function Resolve-QdrantUrlForWindows {
    $configured = if ($env:QDRANT_URL) { $env:QDRANT_URL } else { "http://localhost:6333" }
    if ($configured -notmatch 'localhost|127\.0\.0\.1') {
        return $configured
    }

    if (Test-QdrantHealth "http://127.0.0.1:6333") {
        return "http://127.0.0.1:6333"
    }

    $wslIp = (wsl hostname -I).Split()[0].Trim()
    if ($wslIp -and (Test-QdrantHealth "http://${wslIp}:6333")) {
        Write-Host "Qdrant: using WSL host http://${wslIp}:6333 (localhost unreachable from Windows)"
        return "http://${wslIp}:6333"
    }

    return $configured
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
    Write-Host "  index          - index data/ into vector DB (Qdrant); --force to reindex all"
    Write-Host "  up             - docker compose up -d (WSL)"
    Write-Host "  down           - docker compose down (WSL)"
    Write-Host "  graph-up       - docker compose up -d neo4j only"
    Write-Host "  graph-down     - stop Neo4j container"
    Write-Host "  graph-status   - neo4j container status + Connection OK smoke"
    Write-Host "  graph-shell    - interactive cypher-shell in neo4j container"
    Write-Host "  graph-init-readonly - create text2cypher read-only user"
    Write-Host "  graph-index    - seed Neo4j from data/graph/seed.cypher; --full for full pipeline"
    Write-Host "  graph-qa       - gates + graph-qa.cypher report; --gates-only to skip report"
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
    Write-Host "  check-traces   - verify Langfuse traces for web+telegram chat"
    Write-Host "  langfuse-upload-dataset - upload/reload JSONL to Langfuse"
    Write-Host "  check-telegram - TCP/getMe to api.telegram.org (VPN/proxy)"
    Write-Host "  check-api      - all checks above"
    Write-Host "  check-rag-search-e2e - RAG search smoke (Qdrant up + index; task 04 p.3)"
    Write-Host "  check-rag-audience-filter - b2b/b2c filter smoke (task 04 p.4)"
    Write-Host "  chat-telegram  - POST /api/v1/chat (telegram JSON, raw output)"
    Write-Host "  chat-stream    - POST /api/v1/chat/stream (web SSE, raw output)"
    Write-Host "  eval-help      - eval contour help (see evals/README.md)"
    Write-Host "  eval-build     - build dataset manifest (env DATASET=)"
    Write-Host "  eval-validate  - pytest + dry-run all configs/datasets"
    Write-Host "  eval-sync      - sync datasets to Langfuse (env DATASET=)"
    Write-Host "  eval-experiment - run experiment (env CONFIG=, DATASET=)"
    Write-Host "  eval-analyze   - error analysis (env RUN=, EMIT_ITEMS=1)"
    Write-Host "  eval-compare   - compare runs (env RUN_A=, RUN_B=)"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\make.ps1 ps"
    Write-Host "  .\make.ps1 compose logs -f langfuse-web"
    Write-Host "  .\make.ps1 docker ps -a"
    Write-Host "  .\make.ps1 check-api"
}

function Invoke-LangfuseUploadDataset {
    $datasetJsonl = if ($env:DATASET_JSONL) { $env:DATASET_JSONL } else { "datasets/dataset-v1.jsonl" }
    $datasetName = if ($env:DATASET_NAME) { $env:DATASET_NAME } else { "llmstart-agent-v1" }
    $venvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"
    $python = if (Test-Path $venvPython) { $venvPython } else { (Get-Command python -ErrorAction SilentlyContinue).Source }
    if (-not $python) {
        Write-Error "Python not found. Run: cd backend; uv sync"
    }

    & $python -c "import httpx" 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Installing httpx for upload script..."
        & $python -m pip install httpx
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    }

    Push-Location $BackendDir
    try {
        & $python scripts/upload_langfuse_dataset.py `
            --input (Join-Path $RepoRoot $datasetJsonl) `
            --dataset-name $datasetName `
            --reload
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
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

function Get-GnuMakePath {
    foreach ($name in @("make.exe", "gmake.exe")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source -and (Test-Path -LiteralPath $cmd.Source)) {
            return $cmd.Source
        }
    }
    return $null
}

function Set-MakeEnvFromArgs {
    param([string[]]$ArgList)
    $known = @("CONFIG", "DATASET", "RUN", "RUN_A", "RUN_B", "EMIT_ITEMS")
    foreach ($arg in $ArgList) {
        if ($arg -match "^([^=]+)=(.*)$") {
            $key = $matches[1]
            $value = $matches[2]
            if ($known -contains $key) {
                Set-Item -Path "env:$key" -Value $value
            }
        }
    }
}

function Invoke-EvalMake {
    param(
        [string]$EvalTarget,
        [string[]]$ExtraArgs = @()
    )
    Set-MakeEnvFromArgs -ArgList $ExtraArgs
    Push-Location $EvalsDir
    try {
        $makePath = Get-GnuMakePath
        if ($makePath) {
            & $makePath $EvalTarget
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
            return
        }

        $config = if ($env:CONFIG) { $env:CONFIG } else { "configs/baseline-react-inmemory.yaml" }
        $dataset = if ($env:DATASET) { $env:DATASET } else { "e2e/e2e-qa" }

        switch ($EvalTarget) {
            "help" {
                Write-Host "Eval contour (native Windows path, no GNU make):"
                Write-Host "  validate, build, sync, experiment, analyze, compare"
                Write-Host "Env or args: CONFIG=, DATASET=, RUN=, RUN_A=, RUN_B=, EMIT_ITEMS=1"
            }
            "validate" {
                uv sync --quiet 2>$null
                uv run pytest tests/ -q
                if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                uv run python scripts/run_experiment.py --config $config --dataset all --dry-run
            }
            "build" {
                uv run python scripts/build_dataset.py --dataset $dataset
            }
            "sync" {
                Invoke-EvalMake "validate"
                if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                uv run python scripts/sync_datasets.py --dataset $dataset
            }
            "experiment" {
                Invoke-EvalMake "sync"
                if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
                uv run python scripts/run_experiment.py --config $config --dataset $dataset
            }
            "analyze" {
                $run = if ($env:RUN) { $env:RUN } else { "baseline-react-inmemory--e2e-qa--5eedd7a1--20260615T191628Z" }
                $analyzeArgs = @(
                    "scripts/analyze_run.py",
                    "--run", $run,
                    "--out", "reports/"
                )
                if ($env:EMIT_ITEMS -eq "1") {
                    $analyzeArgs += "--emit-items"
                }
                uv run python @analyzeArgs
            }
            "compare" {
                if (-not $env:RUN_A -or -not $env:RUN_B) {
                    Write-Error "Set RUN_A and RUN_B environment variables"
                }
                uv run python scripts/compare_runs.py --a $env:RUN_A --b $env:RUN_B --out reports/
            }
            default {
                Write-Error "Unknown eval target: $EvalTarget"
            }
        }
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

function Invoke-CheckNeo4j {
    Push-Location $BackendDir
    try {
        $env:NEO4J_URI = Resolve-Neo4jUriForWindows
        uv run python scripts/check_neo4j.py status
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
}

function Invoke-GraphCli {
    param(
        [string]$Module,
        [string[]]$ExtraArgs = @()
    )
    Push-Location $BackendDir
    try {
        $env:NEO4J_URI = Resolve-Neo4jUriForWindows
        uv run python -m $Module @ExtraArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
}

function Invoke-CheckRagSearch {
    param([string]$Command)
    Push-Location $BackendDir
    try {
        $env:QDRANT_URL = Resolve-QdrantUrlForWindows
        uv run python scripts/check_rag_search.py $Command
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
    "index" {
        Push-Location $BackendDir
        try {
            $env:QDRANT_URL = Resolve-QdrantUrlForWindows
            uv run python -m app.rag.index_cli @DockerArgs
            if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
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
    "graph-up" {
        Invoke-WslDocker "docker compose up -d neo4j"
    }
    "graph-down" {
        Invoke-WslDocker "docker compose stop neo4j"
    }
    "graph-status" {
        Invoke-WslDocker "docker compose ps neo4j"
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        Invoke-CheckNeo4j
    }
    "graph-shell" {
        Invoke-WslDocker "docker compose exec -it neo4j cypher-shell"
    }
    "graph-init-readonly" {
        Invoke-WslDocker "bash devops/neo4j/create-readonly-user.sh"
    }
    "graph-index" {
        Invoke-GraphCli -Module "app.graph.index_cli" -ExtraArgs $DockerArgs
    }
    "graph-qa" {
        Invoke-GraphCli -Module "app.graph.qa_cli" -ExtraArgs $DockerArgs
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
    "check-traces" { Invoke-CheckApi "traces" }
    "langfuse-upload-dataset" { Invoke-LangfuseUploadDataset }
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
    "check-rag-search-e2e" { Invoke-CheckRagSearch "e2e" }
    "check-rag-audience-filter" { Invoke-CheckRagSearch "audience-filter" }
    "chat-telegram" { Invoke-RequestChat "telegram" }
    "chat-stream" { Invoke-RequestChat "stream" }
    "eval-help" { Invoke-EvalMake "help" -ExtraArgs $DockerArgs }
    "eval-build" { Invoke-EvalMake "build" -ExtraArgs $DockerArgs }
    "eval-validate" { Invoke-EvalMake "validate" -ExtraArgs $DockerArgs }
    "eval-sync" { Invoke-EvalMake "sync" -ExtraArgs $DockerArgs }
    "eval-experiment" { Invoke-EvalMake "experiment" -ExtraArgs $DockerArgs }
    "eval-analyze" { Invoke-EvalMake "analyze" -ExtraArgs $DockerArgs }
    "eval-compare" { Invoke-EvalMake "compare" -ExtraArgs $DockerArgs }
    default {
        Write-Error "Unknown target: $Target. Run: .\make.ps1 help"
    }
}
