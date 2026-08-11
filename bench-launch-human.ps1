# Balatro Bench: HUMAN launcher (for a person playing with mouse/keyboard).
# Same clean vanilla mod set and same fixed seed as the AI runs, but launched in
# human mode: your own audio, graphics, and motion settings are left alone and
# only game speed is applied. The BalatroBot API still runs so the result can be
# read back, but a human never calls it.
#
# HOW TO PLAY YOUR BENCH RUN once the game opens:
#   1. Main menu -> New Run
#   2. Deck: Red Deck.  Stake: White Stake.
#   3. Click the seed field and enter:  BENCHMRK
#   4. Play. Furthest ante is your score; note your biggest single hand.
#   5. When the run ends, tell Claude and it records "michael" on the board.

$ErrorActionPreference = 'Stop'

$ModsDir       = "$env:APPDATA\Balatro\Mods"
$BlacklistLive = "$ModsDir\lovely\blacklist.txt"
$BenchDir      = "$PSScriptRoot"
$BenchList     = "$BenchDir\blacklist.bench.txt"
$Backup        = "$ModsDir\lovely\blacklist.prebench.bak"
$BalatroExe    = "C:\Program Files (x86)\Steam\steamapps\common\Balatro\Balatro.exe"
$BalatroDir    = "C:\Program Files (x86)\Steam\steamapps\common\Balatro"

# Ensure the clean bench mod set is active (idempotent; keeps any existing backup).
if ((Test-Path $BlacklistLive) -and (-not (Test-Path $Backup))) {
  Copy-Item $BlacklistLive $Backup -Force
  Write-Host "Backed up your blacklist to blacklist.prebench.bak"
}
Copy-Item $BenchList $BlacklistLive -Force
Write-Host "Clean bench mod set active (vanilla card pools)."

# Human-friendly: leave audio/graphics/motion alone, only apply game speed.
$env:BALATROBOT_VANILLA   = '1'
$env:BALATROBOT_GAMESPEED = '4'
$env:BALATROBOT_PORT      = '12346'
Remove-Item Env:\BALATROBOT_BENCH -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "Balatro Bench v1 - HUMAN run (michael)"
Write-Host "  New Run -> Red Deck -> White Stake -> seed: BENCHMRK"
Write-Host "  When done, run bench-restore.ps1 to get your normal mods back."
Write-Host ""
Start-Process -FilePath $BalatroExe -WorkingDirectory $BalatroDir
