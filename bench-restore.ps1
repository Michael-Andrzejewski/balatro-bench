# Restores the mod set you had before running bench-launch.ps1.
# Run this after a benchmarking session to get your normal mods back.

$ErrorActionPreference = 'Stop'

$ModsDir       = "$env:APPDATA\Balatro\Mods"
$BlacklistLive = "$ModsDir\lovely\blacklist.txt"
$Backup        = "$ModsDir\lovely\blacklist.prebench.bak"

if (Test-Path $Backup) {
  Copy-Item $Backup $BlacklistLive -Force
  Remove-Item $Backup -Force
  Write-Host "Restored your original blacklist. Restart Balatro to load your normal mods."
} else {
  Write-Host "No pre-bench backup found. Your blacklist was not changed."
  Write-Host "If Balatro is still on the bench mod set, edit blacklist.txt by hand."
}
