<#
.SYNOPSIS
    PXOS Task Helper (PowerShell)
    Lightweight git worktree and modular spec manager for PXOS multi-agent development on Windows.

.EXAMPLE
    .\scripts\pxos-task.ps1 new feat/auth-oauth T-01
    .\scripts\pxos-task.ps1 list
    .\scripts\pxos-task.ps1 clean feat/auth-oauth
#>

[CmdletBinding()]
param (
    [Parameter(Position = 0, Mandatory = $false)]
    [ValidateSet("new", "list", "clean", "help")]
    [string]$Command = "help",

    [Parameter(Position = 1, Mandatory = $false)]
    [string]$Branch,

    [Parameter(Position = 2, Mandatory = $false)]
    [string]$TaskId = "T-01"
)

function Write-PxosLog([string]$message) {
    Write-Host "[PXOS-TASK] " -ForegroundColor Cyan -NoNewline
    Write-Host $message
}

function Write-PxosOk([string]$message) {
    Write-Host "[PXOS-TASK] " -ForegroundColor Green -NoNewline
    Write-Host $message
}

function Write-PxosWarn([string]$message) {
    Write-Host "[PXOS-TASK] " -ForegroundColor Yellow -NoNewline
    Write-Host $message
}

function Write-PxosErr([string]$message) {
    Write-Host "[PXOS-TASK] " -ForegroundColor Red -NoNewline
    Write-Host $message
}

switch ($Command) {
    "new" {
        if ([string]::IsNullOrWhiteSpace($Branch)) {
            Write-PxosErr "Missing branch name. Usage: .\scripts\pxos-task.ps1 new <branch-name> [task-id]"
            exit 1
        }

        $dirName = $Branch -replace '/', '-'
        $treesDir = "..\trees"
        $targetPath = Join-Path $treesDir $dirName
        $specSuffix = $Branch -replace '^(feat|fix|chore|refactor)/', ''
        $specFile = ".ai/specs/SPEC-$specSuffix.md"

        Write-PxosLog "Creating new parallel worktree for branch '$Branch'..."
        if (-not (Test-Path $treesDir)) {
            New-Item -ItemType Directory -Path $treesDir -Force | Out-Null
        }

        git show-ref --quiet --heads $Branch 2>$null
        if ($LASTEXITCODE -eq 0) {
            git worktree add $targetPath $Branch
        }
        else {
            git worktree add -b $Branch $targetPath
        }

        # Create modular spec
        if (-not (Test-Path $specFile)) {
            if (-not (Test-Path ".ai/specs")) {
                New-Item -ItemType Directory -Path ".ai/specs" -Force | Out-Null
            }

            $templatePath = "templates/.ai/specs/TEMPLATE_SPEC.md"
            if (-not (Test-Path $templatePath)) {
                $templatePath = ".ai/specs/TEMPLATE_SPEC.md"
            }

            if (Test-Path $templatePath) {
                Copy-Item $templatePath $specFile
                $specContent = Get-Content $specFile -Raw
                $specContent = $specContent -replace '\[Task ID\]', $TaskId
                $specContent = $specContent -replace '\[Task Title\]', $specSuffix
                $specContent = $specContent -replace '\[e\.g\. feat/auth-oauth\]', $Branch
                Set-Content $specFile $specContent
                Write-PxosOk "Created modular spec at $specFile"
            }
            else {
                New-Item -ItemType File -Path $specFile -Force | Out-Null
                Write-PxosOk "Created empty spec at $specFile"
            }
        }

        Write-PxosOk "Worktree successfully prepared at: $targetPath"
        Write-Host ""
        Write-Host "  Next steps:" -ForegroundColor White
        Write-Host "  1. Open workspace in worktree: cd $targetPath" -ForegroundColor Yellow
        Write-Host "  2. Launch your AI tool/agent in that folder (e.g. code ., cursor ., claude, gemini)."
        Write-Host "  3. Run /start — the agent will auto-resolve '$specFile'."
        Write-Host ""
    }

    "list" {
        Write-PxosLog "Active Git Worktrees:"
        git worktree list
    }

    "clean" {
        if ([string]::IsNullOrWhiteSpace($Branch)) {
            Write-PxosErr "Missing branch name. Usage: .\scripts\pxos-task.ps1 clean <branch-name>"
            exit 1
        }

        $dirName = $Branch -replace '/', '-'
        $targetPath = Join-Path "..\trees" $dirName

        if (Test-Path $targetPath) {
            Write-PxosLog "Removing worktree at $targetPath..."
            git worktree remove $targetPath --force
            Write-PxosOk "Worktree removed."
        }
        else {
            Write-PxosWarn "Worktree path $targetPath does not exist."
        }
    }

    Default {
        Write-Host "PXOS Task Manager (PowerShell)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Usage:"
        Write-Host "  .\scripts\pxos-task.ps1 new <branch-name> [task-id]   Create a new worktree and modular spec"
        Write-Host "  .\scripts\pxos-task.ps1 list                         List all active worktrees"
        Write-Host "  .\scripts\pxos-task.ps1 clean <branch-name>          Remove an active worktree"
        Write-Host ""
    }
}
