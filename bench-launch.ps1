# Balatro Bench launcher.
# Swaps in a clean mod set (vanilla card pools only), enables the BalatroBot
# benchmark sandbox, and launches the game watchable (audio on, 2x speed).
#
# Reproducibility: the seed / deck / stake are FIXED here. Do not change them
# between recorded runs or scores stop being comparable. See BENCH.md.

$ErrorActionPreference = 'Stop'

# --- Fixed benchmark parameters (v1). Do not edit for a recorded run. ---
$Seed  = 'BENCHMRK'   # canonical Bench v1 seed
$Deck  = 'RED'        # Red Deck
$Stake = 'WHITE'      # White Stake
# -----------------------------------------------------------------------

$ModsDir      = "$env:APPDATA\Balatro\Mods"
$BlacklistLive = "$ModsDir\lovely\blacklist.txt"
$BenchDir     = "$PSScriptRoot"
$BenchList    = "$BenchDir\blacklist.bench.txt"
$Backup       = "$ModsDir\lovely\blacklist.prebench.bak"
$BalatroExe   = "C:\Program Files (x86)\Steam\steamapps\common\Balatro\Balatro.exe"
$BalatroDir   = "C:\Program Files (x86)\Steam\steamapps\common\Balatro"

if (-not (Test-Path $BalatroExe)) {
  throw "Balatro.exe not found at $BalatroExe. Edit the path in this script."
}
if (-not (Test-Path $BenchList)) {
  throw "blacklist.bench.txt not found next to this script."
}

# Back up the user's live blacklist ONCE, so bench-restore.ps1 can undo this.
if (Test-Path $BlacklistLive) {
  if (-not (Test-Path $Backup)) {
    Copy-Item $BlacklistLive $Backup -Force
    Write-Host "Backed up your blacklist to blacklist.prebench.bak"
  } else {
    Write-Host "A pre-bench backup already exists. Leaving it untouched."
  }
}

Copy-Item $BenchList $BlacklistLive -Force
Write-Host "Clean bench mod set is active. Content mods disabled for this launch."

# Sandbox + watchable settings.
$env:BALATROBOT_BENCH     = '1'   # server refuses set / add / load
$env:BALATROBOT_VANILLA   = '0'   # bot mode (perf tweaks ok, muted overridden below)
$env:BALATROBOT_AUDIO     = '1'   # audio on so a human can watch
$env:BALATROBOT_GAMESPEED = '2'
$env:BALATROBOT_HOST      = '127.0.0.1'
$env:BALATROBOT_PORT      = '12346'

Write-Host ""
Write-Host "Balatro Bench v1"
Write-Host ("  Seed  : {0}" -f $Seed)
Write-Host ("  Deck  : {0}  Stake: {1}" -f $Deck, $Stake)
Write-Host "  API   : http://127.0.0.1:12346  (BENCH sandbox ON)"
Write-Host ""
Write-Host "Launching. When you are done benchmarking, run bench-restore.ps1"
Write-Host "to put your normal mod set back."

Start-Process -FilePath $BalatroExe -WorkingDirectory $BalatroDir
