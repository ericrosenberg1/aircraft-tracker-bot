# config.py
# Copy this file to config.py and fill in your own OpenSky credentials.
# config.py is git-ignored; never commit real credentials.

# OpenSky API credentials (https://opensky-network.org)
OPENSKY_API_USER = 'your_username'
OPENSKY_API_PASS = 'your_password'

# Aircraft type configuration
AIRCRAFT_TYPE = 'Boeing 747'

# ICAO typecodes counted as "passenger" for the 747 (freighter/BBJ variants are
# excluded on purpose, per the README's passenger-only filtering feature).
PASSENGER_TYPECODES = {'B741', 'B742', 'B743', 'B744', 'B748'}

# How often to poll OpenSky, in minutes. 10 is Pi-friendly per the README.
POLL_INTERVAL_MINUTES = 10

# Python logging level: DEBUG, INFO, WARNING, ERROR.
LOG_LEVEL = 'INFO'

# Database cleanup policy (see storage.cleanup_db).
RETENTION_DAYS = 30
COMPLETION_GRACE_HOURS = 6

# Per-window rate limit for posting to Twitter/X (see storage.can_post).
POST_WINDOW_SECONDS = 900
TWITTER_MAX_POSTS_PER_WINDOW = 5
