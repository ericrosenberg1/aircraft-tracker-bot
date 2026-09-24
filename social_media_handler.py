import tweepy
import time
import logging
from twitter_config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)
from config import POST_WINDOW_SECONDS, TWITTER_MAX_POSTS_PER_WINDOW
from storage import can_post, record_post, make_message_hash, is_duplicate_message, record_message_hash

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Twitter API client
client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

def post_to_twitter(message) -> bool:
    """Attempt to post to Twitter/X. Returns True only on a confirmed successful
    post. The caller uses this to decide whether to record the post against the
    rate limit and dedupe hash — previously those were recorded unconditionally,
    so a failed post (auth error, bad request, exhausted retries) still marked
    the flight event as "posted", permanently losing it and needlessly eating
    into the rate-limit window."""
    max_retries = 3
    retry_delay = 60  # seconds

    for attempt in range(max_retries):
        try:
            response = client.create_tweet(text=message)
            if response.data:
                tweet_id = response.data['id']
                logger.info(f"Successfully posted to Twitter. Tweet ID: {tweet_id}")
            else:
                logger.warning("Tweet was created, but no data was returned.")
            return True
        except tweepy.TooManyRequests:
            if attempt < max_retries - 1:
                logger.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to post to Twitter after multiple attempts due to rate limiting.")
        except tweepy.TwitterServerError as e:
            if attempt < max_retries - 1:
                logger.warning(f"Twitter server error, retrying in {retry_delay} seconds: {e}")
                time.sleep(retry_delay)
            else:
                logger.error(f"Twitter server error after multiple attempts: {e}")
        # These are not transient: retrying immediately wastes API calls and can
        # never succeed, so fail fast instead of burning the remaining attempts.
        except tweepy.Forbidden as e:
            logger.error(f"Twitter authentication error (not retrying): {e}")
            return False
        except tweepy.BadRequest as e:
            logger.error(f"Bad request error (not retrying): {e}")
            return False
        except tweepy.NotFound as e:
            logger.error(f"Not found error (not retrying): {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error posting to Twitter: {e}")
            return False

    return False

def post_updates(flight, message):
    # Dedupe exact same message content
    msg_hash = make_message_hash(message)
    if is_duplicate_message(msg_hash):
        logger.info("Duplicate message detected; skipping post.")
        return

    # Enforce simple per-window rate limit
    if not can_post('twitter', POST_WINDOW_SECONDS, TWITTER_MAX_POSTS_PER_WINDOW):
        logger.warning("Twitter rate limit window reached; skipping post.")
        return

    # Post to Twitter (X). Only record the post (rate limit + dedupe hash) when
    # it actually succeeded — otherwise a failed post silently "consumes" the
    # flight event and it's never posted or retried.
    if not post_to_twitter(message):
        logger.error(f"Failed to post update for flight {flight['icao24']}; not recording as posted.")
        return

    record_post('twitter')
    record_message_hash(msg_hash)

    # Add logic to post to other social networks here
    # For example:
    # post_to_facebook(message)
    # post_to_instagram(message)

    logger.info(f"Posted update for flight {flight['icao24']}")
