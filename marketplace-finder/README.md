# Marketplace Finder

Searches Facebook Marketplace for items you define, reads each listing, and has Claude
judge value (price vs. fair used price, description, condition, scam red flags). Produces
an HTML report ranked by value that opens in your browser. Runs **on demand** from your Mac.

> ⚠️ Automating Facebook violates Meta's terms of service. Use a **dedicated throwaway
> Facebook account** — never your work or main account. Keep volumes low (the defaults
> are deliberately small). Selectors are scraped from the page and may need maintenance.

## Setup (macOS, personal machine)

```bash
cd marketplace-finder
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp config.example.yaml config.yaml     # edit your searches
export ANTHROPIC_API_KEY=sk-ant-...    # optional; without it a price-only heuristic is used
python finder.py login                 # one-time: sign in to the dedicated FB account
```

## Use

```bash
python finder.py run            # visible browser (recommended), opens report when done
python finder.py run --headless # hidden browser (more likely to be flagged)
python finder.py run --no-ai    # skip Claude scoring
```

Reports land in `results/` (HTML + JSON). Listings seen before are not marked NEW.
The login session lives in `.profile/` (git-ignored — treat it like a password).

## Twice-daily run with a macOS notification (and optional email)

1. `cp .env.example .env`, then fill in `ANTHROPIC_API_KEY`. Email settings are optional.
2. `./install_schedule.sh` - runs at about 08:20 and 18:20 each day (plus a random 0-15 min delay).
   The Mac must be awake and logged in; Chrome opens briefly. Log: `logs/scheduled.log`.
3. Each run shows a notification ("iMacs: 3 new (1 buy)") and refreshes `results/latest.html`;
   `open results/latest.html` shows the full ranked report. A failed run (e.g. "Not logged in")
   shows an "iMac search FAILED" notification.
4. `./uninstall_schedule.sh` removes it.

Optional email: set `SMTP_USER`, `SMTP_PASSWORD` (a Gmail **App Password**) and `EMAIL_TO` in `.env`,
check with `python finder.py test-email`, and the scheduled run will email as well.
`.env` is git-ignored and set to owner-only.

## Optional: schedule with cron

`crontab -e` → `0 8 * * * cd ~/claude-personal/marketplace-finder && .venv/bin/python finder.py run --headless --no-open`
(headless runs are more likely to be flagged by Facebook; manual runs are safer).
