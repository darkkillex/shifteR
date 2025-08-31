
# Changelog — shifteR

Tutte le modifiche rilevanti al progetto verranno documentate in questo file.

Il formato è ispirato a [Keep a Changelog](https://keepachangelog.com/) e segue [Semantic Versioning](https://semver.org/).

---

## [0.1.0] — 2025-08-31
### Added
- Inizializzazione progetto **shifteR**
- Struttura monorepo con `apps/backend` (FastAPI) e `apps/frontend` (Vue 3 + Vite)
- Script PowerShell `start-local.ps1` e `start-frontend.ps1`
- Configurazione database PostgreSQL (utente `shifts`, db `shifts`)
- Endpoint API base:
  - `/api/health/live`
  - CRUD dipendenti
  - CRUD turni predefiniti
  - CRUD schedule entries
  - Rotations generatori (DAY_8_17, H16/H24 4on2off, H16/H24 7on7off)
  - Export/Import CSV
  - Publish (snapshot + diff + email/ICS)
- Seed dati demo (3 dipendenti + turni)

### Fixed
- Allineata connessione Postgres (porta 5433)
- Gestione `.env` con Pydantic v2

---

## [Unreleased]
- Autenticazione centralizzata (OIDC / SAML)
- GUI: drag&drop su planner
- Logging centralizzato
- Migrazioni Alembic
