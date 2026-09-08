# trace-board

> Search a username across the web — confirmed automatically where possible, one click away everywhere else.

**▶ Live demo:** https://mechmukul.github.io/trace-board/ · runs in your browser, no install.

![trace-board screenshot](docs/screenshot.png)

## What it is
Type a username and trace-board searches for it across ~36 platforms, shown as a visual board with
each site's **logo**, grouped by category (Social, Developer, Professional, Content, Gaming,
Security/CTF). It **auto-confirms** accounts on sites that allow it, gives a **direct link** for the
rest, and can **import a Sherlock file** to confirm everything.

## Why it's useful
Pivoting on a username is a core OSINT / threat-intelligence technique — the same handle often
reappears across an actor's accounts. trace-board turns that into a fast, visual search: real
confirmations where the browser can get them, honest "open to check" links where it can't, and a
clean glass UI anyone can use.

## Who it's for / use cases
- **Threat-intel / SOC analysts** pivoting on an actor's handle during an investigation.
- **Incident response** — quickly locating where a compromised or impersonating handle appears.
- **Personal footprint checks** — see where *your own* handle exists and reduce exposure.
- **Anyone who runs Sherlock** and wants a readable, shareable visual of the results.

## Try it live (30 seconds)
1. Open the live demo, type a username, press **Search** (or Enter).
2. Read the badges:
   - **✓ found** (green) — confirmed automatically.
   - **✗ none** (red) — confirmed not present.
   - **open ↗** (grey) — the site can't be auto-checked from a browser; click the card to look yourself.
3. Want every site checked automatically? Run Sherlock (below) and click **Import Sherlock file**.

## How it works
- **Auto-check:** sites with a public, browser-accessible API are checked live — currently **GitHub, GitLab, npm, Chess.com, Mastodon** (200 = found, 404 = none).
- **Open to check:** most sites block cross-origin requests (**CORS**), so a browser can't confirm them automatically; trace-board gives you the exact profile link to open instead — it never guesses.
- **Sherlock import:** for full automatic coverage across hundreds of sites, run the free
  [Sherlock](https://github.com/sherlock-project/sherlock) tool and import its output:
  ```bash
  pip install sherlock-project
  sherlock <username>          # writes <username>.txt with the confirmed profile URLs
  ```
  Click **Import Sherlock file**, choose that file, and every matching card turns green.
- Everything runs client-side; no data leaves your browser.

## Responsible use
For **authorised** investigations only — your own accounts, threat intelligence, or incident
response — with respect for privacy and local law. An unconfirmed link is a lead, not a fact.

## Tech
Vanilla HTML/CSS/JS, zero dependencies, static-hostable. Glassmorphism UI, logos via favicon service.
Inspired by and interoperable with [Sherlock](https://github.com/sherlock-project/sherlock) (MIT).

---
MIT licensed · Built by **Mukul Mech** · Portfolio: [set-watchtower](https://github.com/mechmukul/set-watchtower) · [set-triage-atlas](https://github.com/mechmukul/set-triage-atlas) · [gvm-triage](https://github.com/mechmukul/gvm-triage)
