
# shifteR — Shift Suite (Planner turni aziendali)

Applicazione web per la gestione dei turni (8–17, H16/H24 4on2off, 7on7off), ferie/permessi, pubblicazione con **diff intelligente** e **notifica email** solo ai dipendenti con modifiche.  
Stack: **FastAPI (Python)** + **Vue 3 (Vite, Naive UI)** + **PostgreSQL**.

## ✨ Funzionalità principali
- CRUD dipendenti (Nome, Cognome, **Ditta**, Email)
- Planner settimanale/mensile con:
  - turni predefiniti (8–17, H16/H24 4on2off, 7on7off)
  - ferie (VACATION) e permessi (PTO)
- Generazione automatica turnazioni (4on2off, 7on7off, 8–17 feriali)
- **Publish** con snapshot e invio email **solo a chi ha modifiche**
- Import/Export **CSV**
- Seed di **dati demo**
- Avvio locale semplificato con **PowerShell scripts**

---

## 📦 Struttura del progetto

```
shifteR/
├─ apps/
│  ├─ backend/          # FastAPI + SQLAlchemy (async) + Pydantic v2
│  │  └─ app/
│  │     ├─ routers/    # health, employees, shifts, schedule, rotation, import_export
│  │     ├─ services/   # rotation (generatori turni)
│  │     ├─ utils/      # mailer, ics, diff, seed
│  │     ├─ models.py   # Employee, ShiftTemplate, ScheduleEntry, PlanSnapshot(+Items)
│  │     ├─ schemas.py  # Pydantic schemas
│  │     ├─ database.py # engine async + session
│  │     ├─ settings.py # Pydantic Settings (env)
│  │     └─ main.py     # FastAPI app
│  └─ frontend/         # Vue 3 + Vite + Naive UI + Pinia
│     └─ src/pages/     # Planner.vue, Employees.vue
├─ infra/               # (facoltativo) docker compose, ecc.
├─ start-local.ps1      # Avvio locale completo (backend + frontend)
├─ start-frontend.ps1   # Solo frontend
└─ README.md
```

---

## 🧰 Prerequisiti
- **Windows + PowerShell**
- **Python 3.12+**
- **Node.js 20+**
- **PostgreSQL 16/17** (server **e** CLI tools `psql`)
  - Istanza in ascolto (nel nostro setup) su **porta 5433**
  - Superuser `postgres` con password nota

---

## 🗄️ Preparazione PostgreSQL (porta 5433)

Apri PowerShell e crea utente/db dell’app:

```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5433 -U postgres -d postgres -c "\du"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5433 -U postgres -d postgres -c "CREATE ROLE shifts WITH LOGIN PASSWORD 'admin';"
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5433 -U postgres -d postgres -c "CREATE DATABASE shifts OWNER shifts;"
```

Verifica:
```powershell
& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -p 5433 -U shifts -d shifts -c "SELECT current_user, current_database();"
```

---

## 🚀 Avvio locale (one-click)

Dalla **root** del progetto:

```powershell
.\start-local.ps1
# oppure con seed iniziale
.\start-local.ps1 -Seed
```

Lo script:
- crea `.env` in `apps\backend` (se manca)
- attiva venv, installa dipendenze backend
- installa dipendenze frontend
- esegue seed (se `-Seed`)
- apre 2 finestre:
  - **shifteR - BACKEND** → http://localhost:8000
  - **shifteR - FRONTEND** → http://localhost:5173
- apre il browser

> Varianti:
> ```powershell
> .\start-local.ps1 -BackendPort 9000 -FrontendPort 5174 -DbUrl "postgresql+asyncpg://shifts:admin@localhost:5433/shifts"
> ```

Avvio solo frontend:
```powershell
.\start-frontend.ps1
```

---

## ⚙️ Configurazione (env)

File: `apps/backend/.env` (creato dallo script)

```env
DATABASE_URL=postgresql+asyncpg://shifts:admin@localhost:5433/shifts
SMTP_HOST=localhost
SMTP_PORT=25
SMTP_FROM=no-reply@shifts.local
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173
```

---

## 🧪 Seed demo (manuale)

```powershell
cd apps\backend
.\.venv\Scripts\Activate
python -m app.seed_demo
```

Crea:
- Dipendenti: Mario Rossi (ACME), Luca Bianchi (ACME), Giulia Verdi (BetaSpa)
- 1 settimana di turni 8–17 per Mario

---

## 🧭 Endpoints principali (API)

- `GET /api/health/live` → `{"status":"ok"}`
- `GET/POST /api/employees` → lista/crea dipendenti
- `GET /api/shifts` → elenco turni predefiniti
- `GET /api/schedule/entries?range_start=YYYY-MM-DD&range_end=YYYY-MM-DD`
- `POST /api/schedule/entries`
- `POST /api/rotation/generate`
- `POST /api/schedule/publish`
- `GET /api/io/export.csv?range_start=...&range_end=...`
- `POST /api/io/import.csv`

---

## 📧 Notifiche email
- In `publish`, invia email **solo ai dipendenti con modifiche**
- Allegato `.ics` calendario personale

---

## 🧯 Troubleshooting rapido

**role "shifts" does not exist** → crea ruolo/db su porta giusta  
**DATABASE_URL missing** → controlla `.env`  
**SMTP error** → in dev usa mail catcher  
**uvicorn non trovato** → attiva `.venv`  
**npm Missing script: dev** → `cd apps\frontend && npm install && npm run dev`

---

## 🔐 Note sicurezza (prod)
- `.env` separati per ambiente  
- Protezione con OIDC/SAML (Keycloak/Azure AD)  
- HTTPS e reverse proxy (Nginx/Traefik)  
- Migrazioni Alembic  
- Logging centralizzato  

---

## 📜 Licenza
TBD (MIT consigliata). Inserisci la tua preferita in `LICENSE`.
