# aircraft-tracker-bot — Claude Code Instructions

## Tech stack
- Python bot tracking aircraft via OpenSky Network and posting to social media
- Single-entry main.py with helper modules

## Auto-fix guidelines
- **Test command:** `python -m py_compile main.py models.py opensky_api.py social_media_handler.py storage.py && echo "Syntax OK"`
- No pytest suite — syntax check only
- Only modify the file shown in the stack trace
- Credentials from `config-example.py` pattern (never hardcode)
- Sentry DSN loaded from `AIRCRAFT_TRACKER_SENTRY_DSN` env var

## File map
- `main.py` — entry point and main loop
- `opensky_api.py` — OpenSky Network client
- `social_media_handler.py` — posting logic
- `storage.py` — persistence
- `models.py` — data classes
- `update_aircraft_db.py` — builds `boeing_747_icao.csv` from OpenSky's aircraft database (lists the `s3.opensky-network.org/data-samples` bucket, the dataset web page is JavaScript-only)
- `update_airport_db.py` — refreshes `airport_db.json`

## CI and release
GitHub Actions is off fleet-wide (2026-09-03) and this repo has no workflow
files. `scripts/ci-gates.sh` runs py_compile, ruff's bug-class rules
(`E9,F63,F7,F82`, blocking) and the full ruff report (advisory).
`.githooks/pre-push` runs it after infra-leak-guard, wired with
`git config core.hooksPath .githooks` (run that once per clone). Bypass with
`git push --no-verify`.

The bot runs nowhere as of 2026-10-12, so a push to `main` is the whole
release. Reviving or archiving it is Eric's call.

