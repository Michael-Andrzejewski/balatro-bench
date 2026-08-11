param(
  [Parameter(Mandatory=$true)][string]$Method,
  [string]$Params = '{}',
  [int]$Port = 12346,
  [switch]$Raw
)
$uri = "http://127.0.0.1:$Port"
$body = @{ jsonrpc='2.0'; id=1; method=$Method; params=($Params | ConvertFrom-Json) } | ConvertTo-Json -Compress -Depth 20
try {
  $resp = Invoke-RestMethod -Uri $uri -Method Post -Body $body -ContentType 'application/json' -TimeoutSec 70
} catch {
  Write-Host "HTTP ERROR: $_"; exit 1
}
if ($resp.error) { Write-Host ("API ERROR: {0}" -f $resp.error.message); exit 0 }
$g = $resp.result
if ($Raw) { $g | ConvertTo-Json -Depth 12; exit 0 }

function CardStr($c) {
  $v = $c.value; $m = $c.modifier
  $rank = $v.rank; $suit = $v.suit
  $tags = @()
  if ($m.enhancement) { $tags += $m.enhancement }
  if ($m.edition) { $tags += $m.edition }
  if ($m.seal) { $tags += ($m.seal + 'SEAL') }
  $t = if ($tags.Count) { '(' + ($tags -join ',') + ')' } else { '' }
  if ($rank) { "$rank$suit$t" } else { $c.label + $t }
}

$pausedNote = if ($g.paused) { ' PAUSED(waiting for operator)' } else { '' }
Write-Host ("state={0} ante={1} round={2} money=`${3} won={4}{5}" -f $g.state,$g.ante_num,$g.round_num,$g.money,$g.won,$pausedNote)
if ($g.round) {
  Write-Host ("  round: chips={0} hands_left={1} discards_left={2} reroll=`${3}" -f $g.round.chips,$g.round.hands_left,$g.round.discards_left,$g.round.reroll_cost)
}
if ($g.blinds) {
  foreach ($b in @($g.blinds.small,$g.blinds.big,$g.blinds.boss)) {
    if ($b.status -eq 'CURRENT') {
      Write-Host ("  BLIND: {0} [{1}] target={2} effect={3}" -f $b.name,$b.type,$b.score,$b.effect)
    }
  }
  if ($g.state -eq 'BLIND_SELECT') {
    Write-Host ("  choices: SMALL {0}(tag:{1}) | BIG {2}(tag:{3}) | BOSS {4}: {5}" -f $g.blinds.small.score,$g.blinds.small.tag_name,$g.blinds.big.score,$g.blinds.big.tag_name,$g.blinds.boss.name,$g.blinds.boss.effect)
  }
}
if ($g.hand -and $g.hand.cards -and $g.hand.cards.Count) {
  $i=0; $parts=@(); foreach($c in $g.hand.cards){ $parts += ("{0}:{1}" -f $i,(CardStr $c)); $i++ }
  Write-Host ("  HAND: " + ($parts -join '  '))
}
if ($g.jokers -and $g.jokers.cards -and $g.jokers.cards.Count) {
  $i=0; foreach($c in $g.jokers.cards){ Write-Host ("  JOKER {0}: {1} [{2}] {3}" -f $i,$c.label,$c.key,$c.value.effect); $i++ }
} elseif ($g.jokers) { Write-Host ("  JOKERS: 0/{0}" -f $g.jokers.limit) }
if ($g.consumables -and $g.consumables.cards -and $g.consumables.cards.Count) {
  $i=0; foreach($c in $g.consumables.cards){ Write-Host ("  CONSUMABLE {0}: {1} - {2}" -f $i,$c.label,$c.value.effect); $i++ }
}
if ($g.state -eq 'SHOP') {
  if ($g.shop -and $g.shop.cards) { $i=0; foreach($c in $g.shop.cards){ Write-Host ("  SHOP {0}: {1} `${2} [{3}] {4}" -f $i,$c.label,$c.cost.buy,$c.set,$c.value.effect); $i++ } }
  if ($g.vouchers -and $g.vouchers.cards) { $i=0; foreach($c in $g.vouchers.cards){ Write-Host ("  VOUCHER {0}: {1} `${2} {3}" -f $i,$c.label,$c.cost.buy,$c.value.effect); $i++ } }
  if ($g.packs -and $g.packs.cards) { $i=0; foreach($c in $g.packs.cards){ Write-Host ("  PACK {0}: {1} `${2}" -f $i,$c.label,$c.cost.buy); $i++ } }
}
if ($g.state -eq 'SMODS_BOOSTER_OPENED' -and $g.pack -and $g.pack.cards) {
  $i=0; foreach($c in $g.pack.cards){ Write-Host ("  PACKCARD {0}: {1} [{2}] {3}" -f $i,(CardStr $c),$c.set,$c.value.effect); $i++ }
}
