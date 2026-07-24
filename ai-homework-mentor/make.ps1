#Requires -Version 5.1
<#
.SYNOPSIS
  Dev entrypoint for AI Homework Mentor (Windows / PowerShell).

.EXAMPLE
  .\make.ps1 sync
  .\make.ps1 lint
  .\make.ps1 test
  .\make.ps1 run -- -Message "ping"
  .\make.ps1 compare-modes -- -Path tests/fixtures/local_hw -Message "Тема: python-cli"
#>
param(
    [Parameter(Position = 0)]
    [ValidateSet("help", "sync", "run", "compare-modes", "lint", "format", "test", "ci")]
    [string]$Target = "help",

    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
)

$ErrorActionPreference = "Stop"
$RepoRoot = $PSScriptRoot
Set-Location $RepoRoot

function Show-Help {
    @"
AI Homework Mentor — make.ps1

  sync            uv sync --all-groups
  run             uv run homework-mentor [args...]
  compare-modes   uv run homework-mentor-compare [args...] → docs/compare-modes-*.md
  lint            ruff check + ruff format --check
  format          ruff format + ruff check --fix
  test            pytest
  ci              lint + test

Examples:
  .\make.ps1 sync
  .\make.ps1 run -- -Message "ping"
  .\make.ps1 run -- -Path tests/fixtures/local_hw -Message "Тема: python-cli" -Mode single
  .\make.ps1 compare-modes -- -Path tests/fixtures/local_hw -Message "Тема: python-cli"
  .\make.ps1 lint
  .\make.ps1 test
  .\make.ps1 ci
"@
}

function Invoke-Sync {
    uv sync --all-groups
}

function Invoke-Run {
    $env:PYTHONIOENCODING = "utf-8"
    if ($Rest.Count -gt 0) {
        & uv run homework-mentor @Rest
    }
    else {
        & uv run homework-mentor
    }
}

function Invoke-CompareModes {
    $env:PYTHONIOENCODING = "utf-8"
    if ($Rest.Count -gt 0) {
        & uv run python -m homework_mentor.cli.compare @Rest
    }
    else {
        & uv run python -m homework_mentor.cli.compare
    }
}

function Invoke-Lint {
    uv run ruff format --check .
    uv run ruff check .
}

function Invoke-Format {
    uv run ruff format .
    uv run ruff check --fix .
}

function Invoke-Test {
    uv run pytest
}

function Invoke-Ci {
    Invoke-Lint
    Invoke-Test
}

switch ($Target) {
    "help" { Show-Help }
    "sync" { Invoke-Sync }
    "run" { Invoke-Run }
    "compare-modes" { Invoke-CompareModes }
    "lint" { Invoke-Lint }
    "format" { Invoke-Format }
    "test" { Invoke-Test }
    "ci" { Invoke-Ci }
}
