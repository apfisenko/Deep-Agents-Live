param([string]$Target = "help")

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

switch ($Target) {
    "dev"       { uv sync --all-groups }
    "test"      { uv run pytest tests/ -v }
    "lint"      { uv run ruff check src/ tests/ }
    "format"    { uv run ruff format src/ tests/ }
    "typecheck" { uv run mypy src/ }
    "ci" {
        Write-Host "[lint]"      -ForegroundColor Cyan
        & "$PSScriptRoot\make.ps1" lint
        Write-Host "[typecheck]" -ForegroundColor Cyan
        & "$PSScriptRoot\make.ps1" typecheck
        Write-Host "[test]"      -ForegroundColor Cyan
        & "$PSScriptRoot\make.ps1" test
    }
    default {
        Write-Host "Targets: dev  test  lint  format  typecheck  ci"
    }
}
