# Sentry — Aircraft Tracker Bot

Project: `rosenberg-digital/aircraft-tracker-bot` · platform `python`

## Activation

Set `AIRCRAFT_TRACKER_SENTRY_DSN` in the bot's environment:

```sh
export AIRCRAFT_TRACKER_SENTRY_DSN="https://1746c089b62a395b6a6d13c15316cebf@o4507525754060800.ingest.us.sentry.io/4511429854756864"
```

Errors are reported automatically. Sentry is a no-op if the var is unset.
