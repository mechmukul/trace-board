# trace-board

> Search a username across the web and build a **person dossier** — who they are, their photo, and every confirmed account.

![trace-board screenshot](docs/screenshot.png)

trace-board has two modes:
- **Engine mode (recommended)** — a small backend runs [Sherlock](https://github.com/sherlock-project/sherlock) and checks **every** site *in-app* (accurate found / not-found), then builds a dossier with the person's **avatar + name**. Run it with Docker.
- **Quick mode** — the hosted static page checks a few API-friendly sites live and links the rest. No install, but limited. Live: https://mechmukul.github.io/trace-board/

## Why two modes
Browsers block cross-site reads (CORS), so a static page *cannot* check most sites — only a handful expose open APIs. A **server** has no such limit, so engine mode uses Sherlock's accurate, per-site detection to check everything. Quick mode is the honest best a browser-only page can do.

## Run the engine (Docker)
```bash
git clone https://github.com/mechmukul/trace-board && cd trace-board
docker compose up --build
# open http://localhost:8000
```
That's it — the UI shows "engine connected" and searches all sites in-app.

### Run without Docker
```bash
pip install -r backend/requirements.txt
mkdir -p static && cp index.html static/index.html
uvicorn backend.app:app --port 8000   # open http://localhost:8000
```

### Deploy to a server (e.g. Hostinger VPS with Docker)
```bash
docker compose up -d --build      # runs on port 8000; put it behind your reverse proxy / domain
```

## How it works
- **Backend** (`backend/app.py`, FastAPI): `/api/search?username=` runs Sherlock over a curated set of ~25 sites (`--csv`), parses `Claimed`/`Available`, maps each to a category, and enriches the dossier with the person's GitHub avatar + display name. It also serves the front-end.
- **Front-end** (`index.html`): calls the engine if present (full in-app results + dossier); otherwise falls back to quick mode automatically.
- Extend the site list in `SITES` in `backend/app.py` (use exact Sherlock site names).

## Use cases
- **Threat intel / IR** — pivot on an actor's or impersonator's handle and see every confirmed account with a photo.
- **Personal footprint** — find where *your* handle exists and reduce exposure.
- **Investigations** — a fast, visual front-end over Sherlock's proven detection.

## Responsible use
For **authorised** investigations only — your own accounts, threat intelligence, or incident
response — with respect for privacy and local law. A link is a lead, not proof.

## Tech
FastAPI · Sherlock · httpx · vanilla JS glass UI · Docker. Inspired by and powered by
[Sherlock](https://github.com/sherlock-project/sherlock) (MIT).

---
MIT licensed · Built by **Mukul Mech** · Portfolio: [set-watchtower](https://github.com/mechmukul/set-watchtower) · [set-triage-atlas](https://github.com/mechmukul/set-triage-atlas) · [gvm-triage](https://github.com/mechmukul/gvm-triage)
