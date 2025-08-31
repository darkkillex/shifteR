param(
  [switch]$Seed = $false,
  [int]$BackendPort = 8000,
  [int]$FrontendPort = 5173,
  [string]$DbUrl = "postgresql+asyncpg://shifts:admin@localhost:5433/shifts"
)

function Info($m){ Write-Host "[INFO] $m" -ForegroundColor Cyan }
function Warn($m){ Write-Host "[WARN] $m" -ForegroundColor Yellow }
function Err ($m){ Write-Host "[ERR ] $m" -ForegroundColor Red }

$ErrorActionPreference = "Stop"

# cartelle progetto
$root        = $PSScriptRoot
$backendDir  = Join-Path $root "apps\backend"
$frontendDir = Join-Path $root "apps\frontend"
$venvAct     = Join-Path $backendDir ".venv\Scripts\Activate.ps1"
$envFile     = Join-Path $backendDir ".env"

# check strumenti
try { python --version | Out-Null } catch { Err "Python non trovato nel PATH."; exit 1 }
try { node --version   | Out-Null } catch { Err "Node.js non trovato nel PATH."; exit 1 }
try { npm --version    | Out-Null } catch { Err "npm non trovato nel PATH."; exit 1 }

# .env del backend
if (-not (Test-Path $envFile)) {
  Info "Creo $envFile (porta PG 5433)…"
@"
DATABASE_URL=$DbUrl
SMTP_HOST=localhost
SMTP_PORT=25
SMTP_FROM=no-reply@shifts.local
BACKEND_URL=http://localhost:$BackendPort
FRONTEND_URL=http://localhost:$FrontendPort
"@ | Set-Content -LiteralPath $envFile -Encoding UTF8
} else {
  Info ".env esistente → ok"
}

# venv + deps backend
if (-not (Test-Path $venvAct)) {
  Info "Creo virtualenv…"
  Push-Location $backendDir
  python -m venv .venv
  Pop-Location
}
Info "Installo/aggiorno dipendenze backend…"
Push-Location $backendDir
. $venvAct
pip install -r requirements.txt
Pop-Location

# deps frontend
if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
  Info "Installo dipendenze frontend…"
  Push-Location $frontendDir
  npm install
  Pop-Location
}

# seed opzionale
if ($Seed) {
  Info "Eseguo seed demo (3 dipendenti + 1 settimana)…"
  Push-Location $backendDir
  . $venvAct
  python -m app.seed_demo
  Pop-Location
}

# backend window (usa placeholders + replace per evitare interpolazioni premature)
Info "Avvio BACKEND su http://localhost:$BackendPort …"
$backendCmd = @'
$host.UI.RawUI.WindowTitle = 'shifteR - BACKEND';
Set-Location "BACKEND_DIR_PLACEHOLDER";
. .\.venv\Scripts\Activate.ps1;
$env:PYTHONUNBUFFERED = '1';
$env:DATABASE_URL = 'DBURL_PLACEHOLDER';
uvicorn app.main:app --host 127.0.0.1 --port BACKEND_PORT_PLACEHOLDER --reload
'@
$backendCmd = $backendCmd.Replace("BACKEND_DIR_PLACEHOLDER", $backendDir)
$backendCmd = $backendCmd.Replace("BACKEND_PORT_PLACEHOLDER", "$BackendPort")
$backendCmd = $backendCmd.Replace("DBURL_PLACEHOLDER", $DbUrl)
Start-Process powershell -ArgumentList "-NoExit","-Command",$backendCmd

# frontend window
Info "Avvio FRONTEND su http://localhost:$FrontendPort …"
$frontendCmd = @'
$host.UI.RawUI.WindowTitle = 'shifteR - FRONTEND';
Set-Location "FRONTEND_DIR_PLACEHOLDER";
npm run dev -- --host --port FRONTEND_PORT_PLACEHOLDER
'@
$frontendCmd = $frontendCmd.Replace("FRONTEND_DIR_PLACEHOLDER", $frontendDir)
$frontendCmd = $frontendCmd.Replace("FRONTEND_PORT_PLACEHOLDER", "$FrontendPort")
Start-Process powershell -ArgumentList "-NoExit","-Command",$frontendCmd

# apri browser
Start-Process "http://localhost:$FrontendPort"
Start-Process "http://localhost:$BackendPort/docs"

Write-Host ""
Info "Tutto pronto!"
Write-Host " - Backend  → http://localhost:$BackendPort/docs"
Write-Host " - Frontend → http://localhost:$FrontendPort"
Write-Host ""
