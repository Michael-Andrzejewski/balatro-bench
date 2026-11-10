param([string]$M, [string]$P = "{}")
& powershell -NoProfile -ExecutionPolicy Bypass -File "C:\Users\maaro\OneDrive\Desktop\AI\Platforms\balatro-bench\bench-rpc.ps1" -Port 12347 -Method $M -Params $P
