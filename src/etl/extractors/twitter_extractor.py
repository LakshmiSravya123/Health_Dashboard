"""Twitter data extractor."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import tweepy
from src.etl.extractors.base_extractor import BaseExtractor
from src.utils.config_loader import get_config
from src.utils.logger import log


class TwitterExtractor(BaseExtractor):
    """Extract mental health related tweets from Twitter."""
    
    def __init__(self):
        """Initialize Twitter extractor."""
        super().__init__('twitter')
        
        config = get_config()
        twitter_config = config.get('data_sources.twitter', {})
        
        if not twitter_config.get('enabled', False):
            raise ValueError("Twitter extractor is not enabled in config")
        
        # Initialize Twitter API client
        bearer_token = twitter_config.get('bearer_token')
        if not bearer_token:
            raise ValueError("Twitter bearer token not configured")
        
        self.client = tweepy.Client(bearer_token=bearer_token)
        self.keywords = twitter_config.get('keywords', [])
        self.max_results = twitter_config.get('max_results', 100)
    
    def extract(
        self,
        keywords: List[str] = None,
        start_time: datetime = None,
        end_time: datetime = None,
        max_results: int = None
    ) -> List[Dict[str, Any]]:
        """Extract tweets based on keywords.
        
        Args:
            keywords: List of keywords to search (uses config if None)
            start_time: Start time for search (default: 24 hours ago)
            end_time: End time for search (default: now)
            max_results: Maximum results to return (uses config if None)
            
        Returns:
            List of extracted tweet records
        """
        keywords = keywords or self.keywords
        max_results = max_results or self.max_results
        
        if not start_time:
            start_time = datetime.utcnow() - timedelta(hours=24)
        if not end_time:
            end_time = datetime.utcnow()
        
        records = []
        
        for keyword in keywords:
            try:
                log.info(f"Searching Twitter for keyword: {keyword}")
                
                # Search recent tweets
                tweets = self.client.search_recent_tweets(
                    query=f"{keyword} -is:retweet lang:en",
                    start_time=start_time,
                    end_time=end_time,
                    max_results=min(max_results, 100),  # Twitter API limit
                    tweet_fields=['created_at', 'author_id', 'public_metrics', 'lang'],
                    expansions=['author_id']
                )
                
                if not tweets.data:
                    log.info(f"No tweets found for keyword: {keyword}")
                    continue
                
                # Process tweets
                for tweet in tweets.data:
                    record = self.create_record(
                        user_id=tweet.author_id,
                        text_content=tweet.text,
                        timestamp=tweet.created_at,
                        metadata={
                            'tweet_id': tweet.id,
                            'keyword': keyword,
                            'public_metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                            'language': tweet.lang if hasattr(tweet, 'lang') else 'en'
                        }
                    )
                    records.append(record)
                
                log.info(f"Extracted {len(tweets.data)} tweets for keyword: {keyword}")
            
            except tweepy.TweepyException as e:
                log.error(f"Error extracting tweets for keyword '{keyword}': {str(e)}")
                continue
            except Exception as e:
                log.error(f"Unexpected error for keyword '{keyword}': {str(e)}")
                continue
        
        return records
    
    def extract_user_timeline(
        self,
        user_id: str,
        max_results: int = 100
    ) -> List[Dict[str, Any]]:
        """Extract tweets from a specific user's timeline.
        
        Args:
            user_id: Twitter user ID
            max_results: Maximum number of tweets to extract
            
        Returns:
            List of extracted tweet records
        """
        try:
            tweets = self.client.get_users_tweets(
                id=user_id,
                max_results=min(max_results, 100),
                tweet_fields=['created_at', 'public_metrics', 'lang']
            )
            
            if not tweets.data:
                return []
            
            records = []
            for tweet in tweets.data:
                record = self.create_record(
                    user_id=user_id,
                    text_content=tweet.text,
                    timestamp=tweet.created_at,
                    metadata={
                        'tweet_id': tweet.id,
                        'public_metrics': tweet.public_metrics if hasattr(tweet, 'public_metrics') else {},
                        'language': tweet.lang if hasattr(tweet, 'lang') else 'en'
                    }
                )
                records.append(record)
            
            return records
        
        except tweepy.TweepyException as e:
            log.error(f"Error extracting user timeline for {user_id}: {str(e)}")
            return []
