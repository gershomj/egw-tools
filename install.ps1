# egw-tools Windows installer — one command, everything automated.
# irm https://raw.githubusercontent.com/gershomj/egw-tools/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

$Repo = "https://raw.githubusercontent.com/gershomj/egw-tools/main"
$InstallDir = "$env:USERPROFILE\.egw-tools"
$BinDir = "$env:USERPROFILE\AppData\Local\egw-tools"

Write-Host "egw-tools installer" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan

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
    Write-Host "Python 3 not found." -ForegroundColor Red
    Write-Host "Install it from https://python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during install."
    exit 1
}

Write-Host "Python: $(& $python --version)"

# ── Create directories ──
New-Item -ItemType Directory -Force -Path $InstallDir | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

# ── Download files ──
Write-Host "Downloading egw..."
Invoke-WebRequest -Uri "$Repo/egw" -OutFile "$InstallDir\egw"

Write-Host "Downloading build_kjv.py..."
Invoke-WebRequest -Uri "$Repo/build_kjv.py" -OutFile "$InstallDir\build_kjv.py"

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

# ── Start KJV build ──
Write-Host ""
Write-Host "Starting KJV Bible build in background..." -ForegroundColor Green
$proc = Start-Process -FilePath $python -ArgumentList "`"$InstallDir\build_kjv.py`"" -NoNewWindow -RedirectStandardOutput "$InstallDir\kjv-build.log" -RedirectStandardError "$InstallDir\kjv-build.log" -PassThru
$proc.Id | Out-File "$InstallDir\kjv-build.pid"

Write-Host ""
Write-Host "Done! egw is installed." -ForegroundColor Green
Write-Host ""
Write-Host "  KJV Bible is building in the background (~40 min)."
Write-Host "  Check progress:  egw --kjv-status"
Write-Host ""
Write-Host "  Try it now:"
Write-Host "    egw --version"
Write-Host "    egw --search `"sabbath`"        (needs EGW database)"
Write-Host "    egw --kjv `"John 3:16`"         (works once build finishes)"
Write-Host ""
Write-Host "  To use EGW features, place egw-corpus.db in $InstallDir"
Write-Host ""
Write-Host "  Restart your terminal to use 'egw' from anywhere."
