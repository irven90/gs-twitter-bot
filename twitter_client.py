import os
from typing import Dict, Any, Tuple

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False

def publish_tweet(content: str, media_url: str = None) -> Tuple[bool, str]:
    """
    Publishes a tweet with optional image attachment to X (Twitter).
    Returns (success: bool, message_or_tweet_id: str).
    """
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    
    # Check credentials
    if not all([api_key, api_secret, access_token, access_token_secret]) or not TWEEPY_AVAILABLE:
        # Mock mode execution
        mock_id = f"mock_tweet_{os.urandom(4).hex()}"
        print(f"[MOCK PUBLISH] Content: {content} | Media: {media_url}")
        return True, f"SIMULATION_MODE_SUCCESS_{mock_id}"
        
    try:
        # Initialize Twitter API v1.1 for media upload
        auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
        api_v1 = tweepy.API(auth)
        
        # Initialize Twitter API v2 for posting tweet
        client_v2 = tweepy.Client(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        
        media_ids = []
        if media_url and os.path.exists(media_url):
            uploaded_media = api_v1.media_upload(filename=media_url)
            media_ids.append(uploaded_media.media_id)
            
        if media_ids:
            response = client_v2.create_tweet(text=content, media_ids=media_ids)
        else:
            response = client_v2.create_tweet(text=content)
            
        tweet_id = response.data['id']
        return True, str(tweet_id)
        
    except Exception as e:
        err_msg = str(e)
        print(f"X API Publish Error: {err_msg}")
        if "403" in err_msg or "permissions" in err_msg.lower():
            return False, (
                "⚠️ X API YAZMA İZNİ EKSİK (403 Forbidden):\n"
                "Twitter Developer Portal -> App Settings -> User Authentication Settings sekmesinden "
                "App Permissions yetkisini 'Read' yerine 'Read and Write' yapmanız ve YENİ Access Token üretmeniz gerekmektedir."
            )
        return False, f"Twitter API Hata: {err_msg}"
