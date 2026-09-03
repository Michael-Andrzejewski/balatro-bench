param([Parameter(Mandatory=$true)][string]$Method,[string]$Params='{}',[switch]$Raw)
& "C:\Users\maaro\OneDrive\Desktop\balatro-bench\bench-rpc.ps1" -Port 12347 -Method $Method -Params $Params -Raw:$Raw
