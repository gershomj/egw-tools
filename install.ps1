# egw-tools Windows installer — one command.
# irm https://raw.githubusercontent.com/gershomj/egw-tools/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo = "https://raw.githubusercontent.com/gershomj/egw-tools/main"
$InstallDir = "$env:USERPROFILE\.egw-tools"
$BinDir = "$env:USERPROFILE\AppData\Local\egw-tools"

Write-Host "╔══════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║       egw — EGW + KJV Bible Search      ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── Find Python ──
$python = $null
foreach ($cmd in @("python3", "python")) {
    try {
        $v = & $cmd --version 2>$null
        if ($v -match "Python 3") {
            $python = $cmd
            break
        }
    } catch {}
}

if (-not $python) {
    Write-Host "Python 3 is required but not found." -ForegroundColor Yellow
    Write-Host ""

    # Try winget
    $winget = Get-Command winget -ErrorAction SilentlyContinue
    if ($winget) {
        $response = Read-Host "Install Python 3 via winget now? [y/N]"
        if ($response -eq "y" -or $response -eq "Y") {
            Write-Host "Running: winget install python3"
            winget install python3 --accept-source-agreements --accept-package-agreements
            Write-Host ""
            Write-Host "Please restart this terminal and re-run the installer." -ForegroundColor Green
            Write-Host "  irm https://raw.githubusercontent.com/gershomj/egw-tools/main/install.ps1 | iex"
            exit 0
        }
    }

    Write-Host "Install Python 3 from: https://python.org/downloads/" -ForegroundColor Yellow
    Write-Host "Make sure to check 'Add Python to PATH' during install."
    Write-Host "Then re-run this installer."
    exit 1
}

Write-Host "Python: $(& $python --version)"
Write-Host ""

# ── Create directories ──
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

# ── Download egw ──
Write-Host "Downloading egw (~27 KB)..."
Invoke-WebRequest -Uri "$Repo/egw" -OutFile "$InstallDir\egw"

# ── Download pre-built KJV ──
Write-Host "Downloading KJV Bible database (~12 MB)..."
Invoke-WebRequest -Uri "$Repo/kjv.db" -OutFile "$InstallDir\kjv.db"

# ── Create batch wrapper ──
@"
@echo off
$python "$InstallDir\egw" %*
"@ | Out-File -FilePath "$BinDir\egw.bat" -Encoding ASCII

# ── Add to PATH ──
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$BinDir", "User")
    $env:PATH = "$env:PATH;$BinDir"
    Write-Host "Added to PATH. Restart terminal to use from anywhere."
}

Write-Host ""
Write-Host "Done! egw is installed." -ForegroundColor Green
Write-Host ""
Write-Host "  KJV Bible:  ready (pre-built, 31,009 verses)"
Write-Host "  EGW corpus: not downloaded yet (~1.3 GB, optional)"
Write-Host ""
Write-Host "  Quick start:"
Write-Host "    egw --kjv `"John 3:16`"      KJV verse lookup"
Write-Host "    egw --kjv-search `"faith`"   KJV keyword search"
Write-Host "    egw --egw-download          Download EGW writings"
Write-Host "    egw --search `"sabbath`"      Search EGW (after download)"
Write-Host ""
Write-Host "  Restart your terminal to use 'egw' from anywhere."
