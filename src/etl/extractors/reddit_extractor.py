"""Reddit data extractor."""

from typing import List, Dict, Any
from datetime import datetime
import praw
from src.etl.extractors.base_extractor import BaseExtractor
from src.utils.config_loader import get_config
from src.utils.logger import log


class RedditExtractor(BaseExtractor):
    """Extract mental health related posts from Reddit."""
    
    def __init__(self):
        """Initialize Reddit extractor."""
        super().__init__('reddit')
        
        config = get_config()
        reddit_config = config.get('data_sources.reddit', {})
        
        if not reddit_config.get('enabled', False):
            raise ValueError("Reddit extractor is not enabled in config")
        
        # Initialize Reddit API client
        self.reddit = praw.Reddit(
            client_id=reddit_config.get('client_id'),
            client_secret=reddit_config.get('client_secret'),
            user_agent=reddit_config.get('user_agent', 'MentalHealthDashboard/1.0')
        )
        
        self.subreddits = reddit_config.get('subreddits', [])
    
    def extract(
        self,
        subreddits: List[str] = None,
        limit: int = 100,
        time_filter: str = 'day'
    ) -> List[Dict[str, Any]]:
        """Extract posts from specified subreddits.
        
        Args:
            subreddits: List of subreddit names (uses config if None)
            limit: Maximum posts per subreddit
            time_filter: Time filter (hour, day, week, month, year, all)
            
        Returns:
            List of extracted post records
        """
        subreddits = subreddits or self.subreddits
        records = []
        
        for subreddit_name in subreddits:
            try:
                log.info(f"Extracting from subreddit: r/{subreddit_name}")
                
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Get hot posts
                for submission in subreddit.hot(limit=limit):
                    # Extract post
                    if submission.selftext:  # Only text posts
                        record = self._create_post_record(submission, subreddit_name)
                        records.append(record)
                    
                    # Extract comments
                    submission.comments.replace_more(limit=0)  # Remove "load more" comments
                    for comment in submission.comments.list()[:10]:  # Top 10 comments
                        if hasattr(comment, 'body') and comment.body:
                            comment_record = self._create_comment_record(
                                comment,
                                submission.id,
                                subreddit_name
                            )
                            records.append(comment_record)
                
                log.info(f"Extracted posts and comments from r/{subreddit_name}")
            
            except Exception as e:
                log.error(f"Error extracting from r/{subreddit_name}: {str(e)}")
                continue
        
        return records
    
    def _create_post_record(self, submission, subreddit_name: str) -> Dict[str, Any]:
        """Create record from Reddit submission.
        
        Args:
            submission: PRAW submission object
            subreddit_name: Name of subreddit
            
        Returns:
            Standardized record
        """
        timestamp = datetime.fromtimestamp(submission.created_utc)
        
        text_content = f"{submission.title}\n\n{submission.selftext}"
        
        return self.create_record(
            user_id=submission.author.name if submission.author else 'deleted',
            text_content=text_content,
            timestamp=timestamp,
            metadata={
                'post_id': submission.id,
                'subreddit': subreddit_name,
                'title': submission.title,
                'score': submission.score,
                'num_comments': submission.num_comments,
                'upvote_ratio': submission.upvote_ratio,
                'content_type': 'post'
            }
        )
    
    def _create_comment_record(
        self,
        comment,
        submission_id: str,
        subreddit_name: str
    ) -> Dict[str, Any]:
        """Create record from Reddit comment.
        
        Args:
            comment: PRAW comment object
            submission_id: ID of parent submission
            subreddit_name: Name of subreddit
            
        Returns:
            Standardized record
        """
        timestamp = datetime.fromtimestamp(comment.created_utc)
        
        return self.create_record(
            user_id=comment.author.name if comment.author else 'deleted',
            text_content=comment.body,
            timestamp=timestamp,
            metadata={
                'comment_id': comment.id,
                'post_id': submission_id,
                'subreddit': subreddit_name,
                'score': comment.score,
                'content_type': 'comment'
            }
        )
    
    def extract_user_posts(
        self,
        username: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Extract posts and comments from a specific user.
        
        Args:
            username: Reddit username
            limit: Maximum items to extract
            
        Returns:
            List of extracted records
        """
        try:
            user = self.reddit.redditor(username)
            records = []
            
            # Get user's submissions
            for submission in user.submissions.new(limit=limit):
                if submission.selftext:
                    record = self._create_post_record(submission, submission.subreddit.display_name)
                    records.append(record)
            
            # Get user's comments
            for comment in user.comments.new(limit=limit):
                if comment.body:
                    record = self._create_comment_record(
                        comment,
                        comment.submission.id if hasattr(comment, 'submission') else 'unknown',
                        comment.subreddit.display_name
                    )
                    records.append(record)
            
            return records
        
        except Exception as e:
            log.error(f"Error extracting user posts for {username}: {str(e)}")
            return []
