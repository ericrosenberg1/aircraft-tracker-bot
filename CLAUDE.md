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