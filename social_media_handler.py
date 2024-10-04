# social_media_handler.py

import tweepy
import logging
from twitter_config import (
    TWITTER_API_KEY,
    TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN,
    TWITTER_ACCESS_TOKEN_SECRET
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def post_to_twitter(message):
    try:
        # Authenticate to Twitter
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET
        )

        # Post a tweet
        response = client.create_tweet(text=message)
        
        # Check if the tweet was successfully posted
        if response.data:
            tweet_id = response.data['id']
            logging.info(f"Successfully posted to Twitter. Tweet ID: {tweet_id}")
        else:
            logging.warning("Tweet was created, but no data was returned.")
        
    except tweepy.TweepError as e:
        logging.error(f"Failed to post to Twitter: {e}")

def post_updates(flight, message):
    # Your existing code here
    
    # Add Twitter posting
    post_to_twitter(message)

    # Add logic to post to other social networks here