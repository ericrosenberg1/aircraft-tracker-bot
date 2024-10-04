# test_twitter.py

from social_media_handler import post_to_twitter
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_twitter_posting():
    test_message = "This is a test post from 747tracker bot using Twitter API v2. If you see this, the Twitter integration is working!"
    post_to_twitter(test_message)

if __name__ == "__main__":
    logging.info("Starting Twitter test...")
    test_twitter_posting()
    logging.info("Twitter test completed.")