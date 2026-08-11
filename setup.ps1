# Balatro Bench setup. Prerequisite: Balatro installed (Steam) and git on PATH.
# Installs everything else: the lovely injector, Steamodded, and the
# balatrobot fork (fable branch) with the bench sandbox and API fixes.
#
#   powershell -ExecutionPolicy Bypass -File setup.ps1
#   powershell -ExecutionPolicy Bypass -File setup.ps1 -BalatroDir "D:\Games\Balatro"

param(
  [string]$BalatroDir = "C:\Program Files (x86)\Steam\steamapps\common\Balatro"
)

$ErrorActionPreference = 'Stop'

# 1. Balatro itself (the one thing you must install yourself)
if (-not (Test-Path (Join-Path $BalatroDir "Balatro.exe"))) {
  throw "Balatro.exe not found at $BalatroDir. Install Balatro (Steam) or pass -BalatroDir."
}
Write-Host "Balatro found at $BalatroDir"

if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
  throw "git is required (used to fetch Steamodded and balatrobot). Install Git for Windows first."
}

# 2. lovely injector (version.dll next to Balatro.exe)
$LovelyDll = Join-Path $BalatroDir "version.dll"
if (Test-Path $LovelyDll) {
  Write-Host "lovely injector already present"
} else {
  $zip = Join-Path $env:TEMP "lovely-bench-setup.zip"
  $url = "https://github.com/ethangreen-dev/lovely-injector/releases/latest/download/lovely-x86_64-pc-windows-msvc.zip"
  Write-Host "Downloading lovely injector..."
  Invoke-WebRequest -Uri $url -OutFile $zip
  Expand-Archive -Path $zip -DestinationPath $BalatroDir -Force
  Remove-Item $zip -Force
  if (-not (Test-Path $LovelyDll)) { throw "lovely install failed: version.dll missing after extract" }
  Write-Host "lovely injector installed"
}

# 3. Mods directory
$ModsDir = "$env:APPDATA\Balatro\Mods"
New-Item -ItemType Directory -Force $ModsDir | Out-Null

# 4. Steamodded
if (Test-Path (Join-Path $ModsDir "smods")) {
  Write-Host "Steamodded already present"
} else {
  Write-Host "Cloning Steamodded..."
  git clone --depth 1 https://github.com/Steamodded/smods (Join-Path $ModsDir "smods")
}

# 5. balatrobot fork, fable branch (bench sandbox + API reliability fixes)
if (Test-Path (Join-Path $ModsDir "balatrobot")) {
  Write-Host "balatrobot already present; ensure it is the fable branch of the fork:"
  Write-Host "  https://github.com/Michael-Andrzejewski/balatrobot"
} else {
  Write-Host "Cloning balatrobot (fable branch)..."
  git clone --depth 1 -b fable https://github.com/Michael-Andrzejewski/balatrobot (Join-Path $ModsDir "balatrobot")
}

Write-Host ""
Write-Host "Setup complete. Next:"
Write-Host "  1. Launch a sandboxed instance:  .\bench-launch-ai.ps1 -Port 12347 -BalatroDir `"$BalatroDir`""
Write-Host "  2. Verify the sandbox: a 'set' call must return 'disabled in benchmark mode'."
Write-Host "  3. Give your agent a prompt like runs\fable5-cold-prompt.txt with YOUR paths substituted,"
Write-Host "     launched from a fresh empty working directory (see PROTOCOL.md, context isolation)."
