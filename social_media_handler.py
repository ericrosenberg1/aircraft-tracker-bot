import tweepy
import time
import logging
from twitter_config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the Twitter API client
client = tweepy.Client(
    consumer_key=TWITTER_API_KEY,
    consumer_secret=TWITTER_API_SECRET,
    access_token=TWITTER_ACCESS_TOKEN,
    access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
)

def post_to_twitter(message):
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
            return
        except tweepy.TooManyRequests:
            if attempt < max_retries - 1:
                logger.warning(f"Rate limit exceeded. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error("Failed to post to Twitter after multiple attempts due to rate limiting.")
        except tweepy.TwitterServerError as e:
            logger.error(f"Twitter server error: {e}")
        except tweepy.Forbidden as e:
            logger.error(f"Twitter authentication error: {e}")
        except tweepy.BadRequest as e:
            logger.error(f"Bad request error: {e}")
        except tweepy.NotFound as e:
            logger.error(f"Not found error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error posting to Twitter: {e}")

def post_updates(flight, message):
    # Post to Twitter
    post_to_twitter(message)

    # Add logic to post to other social networks here
    # For example:
    # post_to_facebook(message)
    # post_to_instagram(message)

    logger.info(f"Posted update for flight {flight['icao24']}")