# social_media_handler.py

from config import SOCIAL_MEDIA_KEYS
import tweepy
import logging

def post_updates(flight, message):
    try:
        # Post to Twitter
        auth = tweepy.OAuthHandler(
            SOCIAL_MEDIA_KEYS['twitter']['api_key'],
            SOCIAL_MEDIA_KEYS['twitter']['api_secret_key']
        )
        auth.set_access_token(
            SOCIAL_MEDIA_KEYS['twitter']['access_token'],
            SOCIAL_MEDIA_KEYS['twitter']['access_token_secret']
        )
        api = tweepy.API(auth)
        api.update_status(message)
        logging.info(f"Posted update for flight {flight['icao24']} to Twitter")

        # Add logic to post to other social networks here

    except Exception as e:
        logging.error(f"An error occurred while posting updates: {e}")