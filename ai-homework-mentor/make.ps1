#Requires -Version 5.1
<#
.SYNOPSIS
  Dev entrypoint for AI Homework Mentor (Windows / PowerShell).

.EXAMPLE
  .\make.ps1 sync
  .\make.ps1 lint
  .\make.ps1 test
  .\make.ps1 run -- -Message "ping"
#>
param(
    [Parameter(Position = 0)]
    [ValidateSet("help", "sync", "run", "lint", "format", "test")]
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

  sync     uv sync --all-groups
  run      uv run homework-mentor [args...]
  lint     ruff check + ruff format --check
  format   ruff format + ruff check --fix
  test     pytest

Examples:
  .\make.ps1 sync
  .\make.ps1 run -- -Message "ping"
  .\make.ps1 lint
  .\make.ps1 test
"@
}

function Invoke-Sync {
    uv sync --all-groups
}

function Invoke-Run {
    if ($Rest.Count -gt 0) {
        & uv run homework-mentor @Rest
    }
    else {
        & uv run homework-mentor
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

switch ($Target) {
    "help" { Show-Help }
    "sync" { Invoke-Sync }
    "run" { Invoke-Run }
    "lint" { Invoke-Lint }
    "format" { Invoke-Format }
    "test" { Invoke-Test }
}
