param(
  [int]$Port = 8000,
  [string]$DbUrl = "postgresql+asyncpg://shifts:admin@localhost:5433/shifts"
)

$ErrorActionPreference = "Stop"

function Write-Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Write-Err($msg) { Write-Host "[ERR ] $msg" -ForegroundColor Red }

# Path al backend
$backendDir = "C:\Users\ati.ict\VSProjects\shifteR\apps\backend"
$venvActivate = Join-Path $backendDir ".venv\Scripts\Activate.ps1"

if (!(Test-Path $backendDir)) {
  Write-Err "Backend directory non trovata: $backendDir"
  exit 1
}

if (!(Test-Path $venvActivate)) {
  Write-Err "Virtualenv non trovato. Crea il venv prima con: python -m venv .venv"
  exit 1
}

Write-Info "Avvio backend da $backendDir sulla porta $Port"

# Vai nella cartella backend
Set-Location $backendDir

# Attiva venv
. $venvActivate

# Imposta variabili d’ambiente
$env:DATABASE_URL = $DbUrl
$env:PYTHONUNBUFFERED = "1"

# Avvia Uvicorn
uvicorn app.main:app --reload --port $Port --host 127.0.0.1
