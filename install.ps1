<#
.SYNOPSIS
    PXOS Installer & Updater for Windows PowerShell.

.DESCRIPTION
    Standard installation:
        irm https://raw.githubusercontent.com/madebypx/PXOS/main/install.ps1 | iex

    Upgrade existing project:
        & ./install.ps1 -Update

    With flags:
        & ./install.ps1 -Ide cursor
        & ./install.ps1 -Ide claude
        & ./install.ps1 -Full
        & ./install.ps1 -Global -Ide cursor
#>

[CmdletBinding()]
param(
    [switch]$Version,
    [switch]$Update,
    [switch]$Full,
    [switch]$Global,
    [string]$Ide = "",
    [string]$TargetDir = ".ai"
)

$ErrorActionPreference = "Stop"

$PXOS_VERSION = "2.3.0"
$PXOS_REPO = "https://raw.githubusercontent.com/madebypx/PXOS/main"

function Write-PxosLog([string]$Message) {
    Write-Host "[PXOS] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Write-PxosOk([string]$Message) {
    Write-Host "[PXOS] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-PxosWarn([string]$Message) {
    Write-Host "[PXOS] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

if ($Version) {
    Write-Host "PXOS v$PXOS_VERSION"
    exit 0
}

function Download-Or-Copy([string]$Src, [string]$Dest, [bool]$Overwrite = $false) {
    if ((Test-Path $Dest) -and -not $Overwrite) {
        Write-PxosWarn "Skipping $(Split-Path $Dest -Leaf) — already exists."
        return
    }

    $destParent = Split-Path $Dest -Parent
    if ($destParent -and -not (Test-Path $destParent)) {
        New-Item -ItemType Directory -Path $destParent -Force | Out-Null
    }

    if (Test-Path $Src) {
        Copy-Item -Path $Src -Destination $Dest -Force
    } else {
        $url = "$PXOS_REPO/$Src"
        Invoke-RestMethod -Uri $url -OutFile $Dest
    }

    if ($Overwrite -and (Test-Path $Dest)) {
        Write-PxosOk "Updated $Dest"
    } else {
        Write-PxosOk "Created $Dest"
    }
}

function Append-PxosBlock([string]$Dest, [string]$Content) {
    $START_MARKER = "<!-- pxos:start -->"
    $END_MARKER = "<!-- pxos:end -->"

    $destParent = Split-Path $Dest -Parent
    if ($destParent -and -not (Test-Path $destParent)) {
        New-Item -ItemType Directory -Path $destParent -Force | Out-Null
    }

    if (Test-Path $Dest) {
        $existing = Get-Content -Path $Dest -Raw -Encoding utf8
        if ($existing -match [regex]::Escape($START_MARKER)) {
            $pattern = "(?s)" + [regex]::Escape($START_MARKER) + ".*?" + [regex]::Escape($END_MARKER)
            $replacement = "$START_MARKER`n$Content`n$END_MARKER"
            $updated = [regex]::Replace($existing, $pattern, $replacement)
            Set-Content -Path $Dest -Value $updated -Encoding utf8
            Write-PxosOk "Updated PXOS rules block in $Dest"
            return
        }
        $appended = "$existing`n`n---`n`n$START_MARKER`n$Content`n$END_MARKER`n"
        Set-Content -Path $Dest -Value $appended -Encoding utf8
        Write-PxosOk "Appended PXOS rules to $Dest"
    } else {
        $initial = "$START_MARKER`n$Content`n$END_MARKER`n"
        Set-Content -Path $Dest -Value $initial -Encoding utf8
        Write-PxosOk "Created $Dest"
    }
}

Write-Host ""
if ($Update) {
    Write-Host "Upgrading PXOS to v$PXOS_VERSION..." -ForegroundColor White
} else {
    Write-Host "Installing PXOS v$PXOS_VERSION..." -ForegroundColor White
}
Write-Host ""

if (-not $Global) {
    Write-PxosLog "Configuring $TargetDir/"

    if ($Update) {
        Download-Or-Copy "templates/.ai/AI_BASE.md" "$TargetDir/AI_BASE.md" $true
        Download-Or-Copy "templates/.ai/specs/TEMPLATE_SPEC.md" "$TargetDir/specs/TEMPLATE_SPEC.md" $true
        
        $null = New-Item -ItemType Directory -Path "$TargetDir/research" -Force
        $null = New-Item -ItemType Directory -Path "$TargetDir/audits" -Force
        
        Download-Or-Copy "templates/.ai/research/INDEX.md" "$TargetDir/research/INDEX.md" $false
        Download-Or-Copy "templates/.ai/audits/README.md" "$TargetDir/audits/README.md" $false
        Write-PxosLog "Preserved PROJECT_CONTEXT.md, DECISION_LOG.md, and all active specs."
    } else {
        Download-Or-Copy "templates/.ai/AI_BASE.md" "$TargetDir/AI_BASE.md"
        Download-Or-Copy "templates/.ai/PROJECT_CONTEXT.md" "$TargetDir/PROJECT_CONTEXT.md"
        Download-Or-Copy "templates/.ai/CURRENT_SPEC.md" "$TargetDir/CURRENT_SPEC.md"
        Download-Or-Copy "templates/.ai/DECISION_LOG.md" "$TargetDir/DECISION_LOG.md"
        Download-Or-Copy "templates/.ai/specs/TEMPLATE_SPEC.md" "$TargetDir/specs/TEMPLATE_SPEC.md"
        Download-Or-Copy "templates/.ai/research/INDEX.md" "$TargetDir/research/INDEX.md"
        Download-Or-Copy "templates/.ai/audits/README.md" "$TargetDir/audits/README.md"
    }
}

if ($Full) {
    Write-PxosLog "Installing optional planning files..."
    Download-Or-Copy "templates/ROADMAP.md" "ROADMAP.md"
    Download-Or-Copy "templates/SPRINT.md" "SPRINT.md"
}

# Auto-detect IDE if not specified
if ([string]::IsNullOrWhiteSpace($Ide)) {
    if (Test-Path ".cursor") {
        $Ide = "cursor"
    } elseif (Test-Path ".windsurf") {
        $Ide = "windsurf"
    } elseif (Test-Path "CLAUDE.md") {
        $Ide = "claude"
    } elseif (Test-Path "GEMINI.md") {
        $Ide = "gemini"
    } elseif (Test-Path ".github/copilot-instructions.md") {
        $Ide = "copilot"
    }
}

if (-not [string]::IsNullOrWhiteSpace($Ide)) {
    $ideContent = ""
    if (Test-Path "templates/rules/pxos.md") {
        $ideContent = Get-Content -Path "templates/rules/pxos.md" -Raw -Encoding utf8
    } elseif (Test-Path "$TargetDir/AI_BASE.md") {
        $ideContent = Get-Content -Path "$TargetDir/AI_BASE.md" -Raw -Encoding utf8
    } else {
        $ideContent = (Invoke-RestMethod -Uri "$PXOS_REPO/templates/rules/pxos.md")
    }

    $userHome = $HOME
    if ($env:USERPROFILE) { $userHome = $env:USERPROFILE }

    switch ($Ide.ToLowerInvariant()) {
        "cursor" {
            $rulesFile = if ($Global) { "$userHome/.cursor/rules/pxos.mdc" } else { ".cursor/rules/pxos.mdc" }
            $parent = Split-Path $rulesFile -Parent
            if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
            $cursorBody = "---`nalwaysApply: true`n---`n`n$ideContent"
            Set-Content -Path $rulesFile -Value $cursorBody -Encoding utf8
            Write-PxosOk "Configured Cursor rules at $rulesFile"
        }
        "windsurf" {
            $rulesFile = if ($Global) { "$userHome/.windsurf/rules/pxos.md" } else { ".windsurf/rules/pxos.md" }
            $parent = Split-Path $rulesFile -Parent
            if ($parent -and -not (Test-Path $parent)) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
            Set-Content -Path $rulesFile -Value $ideContent -Encoding utf8
            Write-PxosOk "Configured Windsurf rules at $rulesFile"
        }
        "claude" {
            $rulesFile = if ($Global) { "$userHome/.claude/CLAUDE.md" } else { "CLAUDE.md" }
            Append-PxosBlock $rulesFile $ideContent
        }
        "gemini" {
            $rulesFile = if ($Global) { "$userHome/.gemini/GEMINI.md" } else { "GEMINI.md" }
            Append-PxosBlock $rulesFile $ideContent
        }
        "copilot" {
            $rulesFile = ".github/copilot-instructions.md"
            Append-PxosBlock $rulesFile $ideContent
        }
        default {
            Write-PxosWarn "Unknown IDE: $Ide. Supported values: cursor, windsurf, claude, gemini, copilot."
        }
    }
}

Write-Host ""
if ($Update) {
    Write-Host "PXOS upgraded to v$PXOS_VERSION." -ForegroundColor Green
} else {
    Write-Host "PXOS v$PXOS_VERSION installed." -ForegroundColor Green
}
Write-Host ""

if (-not $Global) {
    Write-Host "  Next steps:"
    Write-Host "  1. Check .ai/AI_BASE.md for updated operating rules."
    Write-Host "  2. Run /start in any branch or worktree to auto-resolve specs."
    Write-Host "  3. Use /audit for codebase health and /decision for ADRs."
} else {
    Write-Host "  Global IDE rules configured for v$PXOS_VERSION."
}
Write-Host ""
Write-Host "  Docs: https://github.com/madebypx/PXOS"
Write-Host ""
