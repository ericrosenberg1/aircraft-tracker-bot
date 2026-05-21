# Sentry — Aircraft Tracker Bot

Project: `rosenberg-digital/aircraft-tracker-bot` · platform `python`

## Activation

Set `AIRCRAFT_TRACKER_SENTRY_DSN` in the bot's environment:

```sh
export AIRCRAFT_TRACKER_SENTRY_DSN="https://..."
```

Errors are reported automatically. Sentry is a no-op if the var is unset.
