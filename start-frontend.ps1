param(
  [int]$Port = 5173
)

$ErrorActionPreference = "Stop"
function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Err ($m){ Write-Host "[ERR ] $m" -ForegroundColor Red }

$root        = $PSScriptRoot
$frontendDir = Join-Path $root "apps\frontend"

if (!(Test-Path $frontendDir)) { Err "Cartella frontend non trovata: $frontendDir"; exit 1 }

# install deps se manca node_modules
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
  Info "Installo dipendenze frontend…"
  Push-Location $frontendDir
  npm install
  Pop-Location
}

Info "Avvio FRONTEND su http://localhost:$Port …"
Push-Location $frontendDir
npm run dev -- --host --port $Port
Pop-Location
