param(
    [Parameter(Position = 0)]
    [string]$Target = "start",
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$ExtraArgs
)

$ErrorActionPreference = "Stop"
$ComparisonDir = $PSScriptRoot
#$RepoRoot = Split-Path $ComparisonDir -Parent
$RepoRoot = $PSScriptRoot
$MinFreeDiskGB = 10

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


function Get-WslPath {
    param([string]$WindowsPath)
    if ($env:COMPARISON_WSL_PATH) {
        return $env:COMPARISON_WSL_PATH.TrimEnd("/")
    }
    $path = $WindowsPath -replace '\\', '/'
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

function Get-WslComposeFile {
    return (Get-WslPath -WindowsPath $ComparisonDir) + "/docker-compose.yml"
}

function Invoke-WslBash {
    param(
        [string]$Command,
        [switch]$AllowFail
    )
    $output = wsl.exe -e bash -lc "$Command" 2>&1
    $code = $LASTEXITCODE
    if ($output) { $output | ForEach-Object { Write-Host $_ } }
    if (-not $AllowFail -and $code -ne 0) { exit $code }
    return @{ Output = ($output -join "`n"); ExitCode = $code }
}

function Invoke-WslCompose {
    param(
        [string]$Args,
        [switch]$AllowFail
    )
    $composeFile = Get-WslComposeFile
    return Invoke-WslBash "docker compose -f '$composeFile' $Args" -AllowFail:$AllowFail
}

function Invoke-WslInComparison {
    param(
        [string]$Command,
        [switch]$AllowFail
    )
    if ($Command -match '^docker compose ') {
        $args = $Command.Substring(14)
        return Invoke-WslCompose $args -AllowFail:$AllowFail
    }
    return Invoke-WslBash $Command -AllowFail:$AllowFail
}

function Get-CDiskFreeGB {
    $drive = Get-PSDrive -Name C
    return [math]::Round($drive.Free / 1GB, 2)
}

function Test-CDiskSpace {
    param([switch]$Required)
    $freeGB = Get-CDiskFreeGB
    Write-Host "C: free ${freeGB} GB (warn if < ${MinFreeDiskGB} GB)"
    if ($freeGB -lt $MinFreeDiskGB) {
        $msg = @(
            "WARNING: on C: only ${freeGB} GB free (threshold ${MinFreeDiskGB} GB)."
            "Docker pull and uv sync may fail or grow the WSL VHDX."
            "Run: docker system prune -a   or use smaller corpus (5000)."
        ) -join " "
        Write-Warning $msg
        if ($Required) {
            Write-Error "Not enough free space on C: (${freeGB} GB < ${MinFreeDiskGB} GB)."
        }
    }
}

function Test-DockerDaemon {
    $r = Invoke-WslBash "docker version --format '{{.Server.Version}}' 2>&1" -AllowFail
    if ($r.Output -notmatch "^\d+\.") {
        if ($r.Output -match "Cannot connect to the Docker daemon|Is the docker daemon running") {
            throw ((@(
                "Docker daemon in WSL is not running."
                "If repair was interrupted, open WSL and run:"
                "  sudo systemctl restart docker"
                "If restart fails (containerd snapshots), run:"
                "  .\make_u.ps1 repair"
            ) -join "`n"))
        }
        Write-Error "Docker daemon in WSL is not reachable. Start Docker/WSL and retry."
    }
}

function Invoke-DockerRepair {
    Write-Warning "Repair stops ALL WSL containers, prunes unused images/volumes, restarts docker."
    Write-Warning "Langfuse and other stacks will need: cd repo root; .\make.ps1 up"
    Write-Warning "sudo will ask for your WSL password."
    # Single-quoted here-string: PowerShell must not expand bash $variables.
    $cmd = @'
set -e

docker_ok() {
  docker info >/dev/null 2>&1
}

echo "==> phase 1: prune (if daemon is up)"
if docker_ok; then
  ids=$(docker ps -q 2>/dev/null || true)
  if [ -n "$ids" ]; then docker stop $ids; fi
  docker system prune -a --volumes -f || true
  sudo systemctl restart docker
  sleep 3
fi

if ! docker_ok; then
  echo "==> phase 2: daemon down — reset buildkit + orphaned snapshots (sudo)"
  sudo systemctl stop docker containerd 2>/dev/null || true
  sudo rm -rf /var/lib/docker/buildkit
  # Drop snapshot dirs whose fs layer is missing (common containerd corruption).
  snap_root=/var/lib/containerd/io.containerd.snapshotter.v1.overlayfs/snapshots
  if [ -d "$snap_root" ]; then
    for d in "$snap_root"/*; do
      [ -d "$d" ] || continue
      if [ ! -d "$d/fs" ]; then
        echo "Removing orphaned snapshot: $d"
        sudo rm -rf "$d"
      fi
    done
  fi
  sudo systemctl start containerd
  sudo systemctl start docker
  sleep 3
fi

if ! docker_ok; then
  echo "Docker daemon still not running. Last log lines:"
  journalctl -u docker.service -n 20 --no-pager || true
  exit 1
fi

echo "==> phase 3: prune after restart"
docker system prune -a --volumes -f || true
docker system df || docker ps
'@
    $r = Invoke-WslBash $cmd -AllowFail
    if ($r.ExitCode -ne 0) {
        throw ((@(
            "Docker repair failed (exit $($r.ExitCode))."
            "Open WSL and inspect: journalctl -u docker.service -n 30 --no-pager"
            "If buildkit reset was not enough, last resort in WSL:"
            "  sudo systemctl stop docker containerd"
            "  sudo rm -rf /var/lib/docker /var/lib/containerd"
            "  sudo systemctl start containerd docker"
            "Then: .\make_u.ps1 pull && .\make_u.ps1 up"
        ) -join "`n"))
    }
    Write-Host "Repair done. Run: .\make_u.ps1 pull && .\make_u.ps1 up"
}

function Test-DockerStorage {
    $r = Invoke-WslBash "docker system df 2>&1" -AllowFail
    if ($r.Output -match "TYPE\s+TOTAL\s+ACTIVE") {
        return
    }
    if ($r.Output -match "no such file or directory|failed to calculate") {
        throw ((@(
            "Docker storage in WSL looks corrupted (containerd snapshots)."
            "Run: .\make_u.ps1 repair"
            "Then: .\make_u.ps1 pull && .\make_u.ps1 up"
        ) -join "`n"))
    }
    # docker system df sometimes crashes WSL from PowerShell; fall back to lighter checks
    $fb = Invoke-WslBash "docker ps --format '{{.Names}}' 2>&1 | head -3" -AllowFail
    if ($fb.Output -and $fb.ExitCode -eq 0) {
        Write-Warning "docker system df skipped (WSL quirk); docker ps works, continuing."
        return
    }
    throw "Docker storage check failed (exit $($r.ExitCode)): $($r.Output)"
}

function Import-DotEnv {
    param([string[]]$Paths)
    foreach ($envPath in $Paths) {
        if (-not (Test-Path -LiteralPath $envPath)) { continue }
        Get-Content -LiteralPath $envPath | ForEach-Object {
            $line = $_.Trim()
            if (-not $line -or $line.StartsWith("#")) { return }
            if ($line -match '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {
                $name = $matches[1]
                $value = $matches[2].Trim().Trim('"').Trim("'")
                if (-not [string]::IsNullOrWhiteSpace($value)) {
                    Set-Item -Path "env:$name" -Value $value
                }
            }
        }
    }
}

function Test-OpenRouterKey {
    Import-DotEnv -Paths @(
        (Join-Path $ComparisonDir ".env"),
        (Join-Path $RepoRoot ".env")
    )
    if (-not $env:OPENROUTER_API_KEY) {
        Write-Error "OPENROUTER_API_KEY not found. Add it to comparison/.env or repo root .env"
    }
}

function Wait-ForPort {
    param(
        [int]$Port,
        [string]$Label,
        [int]$TimeoutSec = 120
    )
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        $ok = $false
        try {
            $client = New-Object System.Net.Sockets.TcpClient
            $client.Connect("127.0.0.1", $Port)
            $ok = $client.Connected
            $client.Close()
        } catch {
            $ok = $false
        }
        if ($ok) {
            Write-Host "$Label ready on port $Port"
            return
        }
        Start-Sleep -Seconds 2
    }
    Write-Error "Timeout: $Label did not respond on port $Port (${TimeoutSec}s). Run: .\make_u.ps1 ps"
}

function Invoke-Uv {
    param([string[]]$UvArgs)
    Push-Location $ComparisonDir
    try {
        & uv @UvArgs
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } finally {
        Pop-Location
    }
}

function Assert-ComposeServicesRunning {
    $r = Invoke-WslCompose "ps --status running --format '{{.Service}}'" -AllowFail
    $running = @($r.Output -split "`n" | ForEach-Object { $_.Trim() } | Where-Object { $_ })
    $need = @("qdrant", "pgvector")
    $missing = $need | Where-Object { $_ -notin $running }
    if ($missing.Count -gt 0) {
        throw ((@(
            "Containers not running after compose up. Missing: $($missing -join ', ')."
            "Images may not have been pulled (check network or docker storage)."
            "Diagnostics: .\make_u.ps1 doctor"
            "Manual pull: .\make_u.ps1 pull"
        ) -join "`n"))
    }
    Write-Host "Running services: $($running -join ', ')"
}

function Invoke-DockerPull {
    Test-CDiskSpace
    Test-DockerDaemon
    Test-DockerStorage
    Write-Host "==> docker compose pull (WSL, may take several minutes)"
    $r = Invoke-WslCompose "pull" -AllowFail
    if ($r.ExitCode -ne 0 -and $r.Output -notmatch "Pulled|Already up to date|Download complete") {
        throw ((@(
            "docker compose pull failed (exit $($r.ExitCode))."
            "Small images (hello-world) may work while large ones (qdrant/pgvector) fail:"
            "  - corrupted WSL docker storage -> .\make_u.ps1 doctor"
            "  - low disk on C: -> free space or docker system prune"
            "  - network/registry timeout -> retry or VPN"
        ) -join "`n"))
    }
}

function Invoke-DockerUp {
    Test-CDiskSpace
    Test-DockerDaemon
    Test-DockerStorage
    Invoke-DockerPull
    Write-Host "==> docker compose up -d (WSL)"
    Invoke-WslCompose "up -d"
    Assert-ComposeServicesRunning
}

function Show-Help {
    Write-Host "comparison - Qdrant + pgvector + Jupyter (Docker via WSL, Python via uv)"
    Write-Host ""
    Write-Host "  start          - up + sync + build + jupyter lab (default)"
    Write-Host "  up             - pull + compose up + verify containers"
    Write-Host "  pull           - docker compose pull only"
    Write-Host "  doctor         - disk + docker daemon + storage checks"
    Write-Host "  repair         - prune WSL docker storage (fixes snapshot corruption)"
    Write-Host "  down           - docker compose down"
    Write-Host "  down-v         - docker compose down -v (remove volumes)"
    Write-Host "  ps             - docker compose ps"
    Write-Host "  sync           - uv sync"
    Write-Host "  corpus [N]     - precompute embeddings (default 40000)"
    Write-Host "  build          - jupytext --to ipynb comparison.py"
    Write-Host "  lab            - jupyter lab comparison.ipynb"
    Write-Host "  check          - wait for Qdrant :6333 and pgvector :5433"
    Write-Host "  help           - this help"
    Write-Host ""
    Write-Host "Disk: warns if C: free < ${MinFreeDiskGB} GB"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\make_u.ps1 doctor"
    Write-Host "  .\make_u.ps1 pull"
    Write-Host "  .\make_u.ps1 up"
    Write-Host "  .\make_u.ps1 corpus 5000"
}

function Invoke-Doctor {
    Test-CDiskSpace
    Test-DockerDaemon
    Write-Host "==> docker system df"
    Test-DockerStorage
    Write-Host "==> docker compose ps"
    Invoke-WslCompose "ps" -AllowFail | Out-Null
    Write-Host "==> images for this stack"
    Invoke-WslBash "docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}' | grep -E 'qdrant|pgvector|REPOSITORY' || true" -AllowFail | Out-Null
    Write-Host "Doctor OK (if no errors above)."
}

function Invoke-Start {
    Invoke-WslDocker "docker compose up -d"
    Write-Host "==> waiting for Qdrant and pgvector"
    Wait-ForPort -Port 6333 -Label "Qdrant"
    Wait-ForPort -Port 5433 -Label "pgvector"
    Write-Host "==> uv sync"
    Invoke-Uv @("sync")
    Test-OpenRouterKey
    Write-Host "==> build comparison.ipynb"
    Invoke-Uv @("run", "jupytext", "--to", "ipynb", "comparison.py")
    Write-Host "==> jupyter lab (Ctrl+C to stop)"
    Invoke-Uv @("run", "jupyter", "lab", "comparison.ipynb")
}

function Invoke-CheckConnections {
    Wait-ForPort -Port 6333 -Label "Qdrant" -TimeoutSec 5
    Wait-ForPort -Port 5433 -Label "pgvector" -TimeoutSec 5
    Write-Host "Ports OK: Qdrant 6333, pgvector 5433"
}

switch ($Target) {
    "help" { Show-Help }
    "start" { Invoke-Start }
    "dev" { Invoke-Start }
    "doctor" { Invoke-Doctor }
    "repair" { Invoke-DockerRepair }
    "pull" { Invoke-DockerPull }
    "up" { Invoke-WslDocker "docker compose up -d" }
    "down" { Invoke-WslDocker "docker compose down" }
    "down-v" { Invoke-WslDocker "docker compose down -v" }
    "ps" { Invoke-WslDocker "docker compose ps" }    
    "sync" {
        Invoke-Uv @("sync")
    }
    "corpus" {
        Test-CDiskSpace
        Test-OpenRouterKey
        $n = if ($ExtraArgs.Count -gt 0) { $ExtraArgs[0] } else { "40000" }
        Invoke-Uv @("run", "python", "corpus.py", $n)
    }
    "build" {
        Invoke-Uv @("run", "jupytext", "--to", "ipynb", "comparison.py")
    }
    "lab" {
        Test-OpenRouterKey
        Invoke-Uv @("run", "jupytext", "--to", "ipynb", "comparison.py")
        Invoke-Uv @("run", "jupyter", "lab", "comparison.ipynb")
    }
    "check" { Invoke-CheckConnections }
    default {
        Write-Error "Unknown target: $Target. Run: .\make_u.ps1 help"
    }
}
