# Balatro Bench: AI launcher. Launches one bot/sandbox instance on a given port.
# Used to stand up parallel instances (e.g. 12346 and 12347) for two AI runs.
param([int]$Port = 12346)

$ErrorActionPreference = 'Stop'

$ModsDir       = "$env:APPDATA\Balatro\Mods"
$BlacklistLive = "$ModsDir\lovely\blacklist.txt"
$BenchDir      = "$PSScriptRoot"
$BenchList     = "$BenchDir\blacklist.bench.txt"
$Backup        = "$ModsDir\lovely\blacklist.prebench.bak"
$BalatroExe    = "C:\Program Files (x86)\Steam\steamapps\common\Balatro\Balatro.exe"
$BalatroDir    = "C:\Program Files (x86)\Steam\steamapps\common\Balatro"

if ((Test-Path $BlacklistLive) -and (-not (Test-Path $Backup))) {
  Copy-Item $BlacklistLive $Backup -Force
}
# Generate the bench blacklist from the live Mods folder: everything except the
# three harness mods. A static list rots as soon as a mod is added or renamed.
$Allowed = @('smods', 'lovely', 'balatrobot')
$Blocked = Get-ChildItem $ModsDir -Directory |
  Where-Object { $Allowed -notcontains $_.Name } |
  Select-Object -ExpandProperty Name
$Blocked | Set-Content $BenchList -Encoding ASCII
$Blocked | Set-Content $BlacklistLive -Encoding ASCII
Write-Host ("Bench blacklist: {0} mods disabled, allowed: {1}" -f $Blocked.Count, ($Allowed -join ', '))

$env:BALATROBOT_BENCH     = '1'   # sandbox: server refuses set / add / load
$env:BALATROBOT_VANILLA   = '0'   # bot mode
$env:BALATROBOT_AUDIO     = '0'   # muted (two instances would clash)
$env:BALATROBOT_GAMESPEED = '4'
$env:BALATROBOT_HOST      = '127.0.0.1'
$env:BALATROBOT_PORT      = "$Port"

Write-Host ("Launching Balatro Bench AI instance on port {0} (BENCH sandbox ON)" -f $Port)
Start-Process -FilePath $BalatroExe -WorkingDirectory $BalatroDir
