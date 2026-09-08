"""trace-board engine — FastAPI backend that checks a username across sites using Sherlock,
then enriches the result into a person "dossier" (avatar + display name + confirmed accounts).

Why a backend at all: browsers block cross-site reads (CORS), so a static page can only check a
handful of API-friendly sites. A server has no such limit and can use Sherlock's accurate,
per-site detection. This backend runs that engine and serves the static UI from the same origin.
"""
from __future__ import annotations

import asyncio
import csv
import os
import re
import tempfile
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Curated sites (exact Sherlock names) -> label + category shown in the UI.
SITES = [
    ("GitHub", "GitHub", "Developer"), ("GitLab", "GitLab", "Developer"),
    ("BitBucket", "Bitbucket", "Developer"), ("PyPi", "PyPI", "Developer"),
    ("npm", "npm", "Developer"), ("Docker Hub", "Docker Hub", "Developer"),
    ("Kaggle", "Kaggle", "Developer"), ("DEV Community", "Dev.to", "Developer"),
    ("Instagram", "Instagram", "Social"), ("Telegram", "Telegram", "Social"),
    ("Bluesky", "Bluesky", "Social"), ("Reddit", "Reddit", "Social"),
    ("YouTube", "YouTube", "Content"), ("SoundCloud", "SoundCloud", "Content"),
    ("Patreon", "Patreon", "Content"), ("Medium", "Medium", "Content"),
    ("Vimeo", "Vimeo", "Content"),
    ("Behance", "Behance", "Professional"), ("Dribbble", "Dribbble", "Professional"),
    ("Keybase", "Keybase", "Security / CTF"), ("HackerOne", "HackerOne", "Security / CTF"),
    ("BugCrowd", "Bugcrowd", "Security / CTF"), ("TryHackMe", "TryHackMe", "Security / CTF"),
    ("VirusTotal", "VirusTotal", "Security / CTF"),
    ("Chess", "Chess.com", "Gaming"),
]
LABEL = {s[0]: s[1] for s in SITES}
CATEGORY = {s[0]: s[2] for s in SITES}
VALID = re.compile(r"^[A-Za-z0-9._-]{1,40}$")

app = FastAPI(title="trace-board engine")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


async def run_sherlock(username: str) -> list[dict]:
    """Run Sherlock over the curated sites and parse its CSV output."""
    with tempfile.TemporaryDirectory() as tmp:
        cmd = ["sherlock", username, "--csv", "--print-all", "--no-color",
               "--timeout", "8", "--folderoutput", tmp]
        for name, _, _ in SITES:
            cmd += ["--site", name]
        proc = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.DEVNULL)
        try:
            await asyncio.wait_for(proc.wait(), timeout=90)
        except asyncio.TimeoutError:
            proc.kill()
            raise HTTPException(504, "Search timed out")
        csv_path = Path(tmp) / f"{username}.csv"
        if not csv_path.exists():
            return []
        out = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                name = row.get("name", "")
                out.append({
                    "site": LABEL.get(name, name),
                    "category": CATEGORY.get(name, "Other"),
                    "url": row.get("url_user", ""),
                    "found": row.get("exists", "").strip().lower() == "claimed",
                })
        return out


async def enrich(username: str, results: list[dict]) -> dict:
    """Best-effort person image + display name from a confirmed GitHub account."""
    dossier = {"avatar": None, "displayName": None}
    has_github = any(r["site"] == "GitHub" and r["found"] for r in results)
    if has_github:
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.get(f"https://api.github.com/users/{username}")
                if r.status_code == 200:
                    d = r.json()
                    dossier["avatar"] = d.get("avatar_url")
                    dossier["displayName"] = d.get("name") or username
        except httpx.HTTPError:
            pass
    return dossier


@app.get("/api/search")
async def search(username: str):
    username = username.strip().lstrip("@")
    if not VALID.match(username):
        raise HTTPException(400, "Username must be 1-40 chars: letters, digits, . _ -")
    results = await run_sherlock(username)
    dossier = await enrich(username, results)
    found = [r for r in results if r["found"]]
    return {
        "username": username,
        "avatar": dossier["avatar"],
        "displayName": dossier["displayName"] or username,
        "checked": len(results),
        "found_count": len(found),
        "results": results,
    }


@app.get("/api/health")
async def health():
    return {"ok": True, "sites": len(SITES)}


# Serve the static front-end from the same origin (so fetch('/api/...') just works).
STATIC_DIR = os.environ.get("STATIC_DIR", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
