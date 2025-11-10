"""
YouTube Comment Scraper
Fetches comments from YouTube videos using the YouTube Data API
"""

import os
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from datetime import datetime
from tqdm import tqdm
import time

class YouTubeScraper:
    def __init__(self, api_key):
        """
        Initialize YouTube scraper with API key
        
        Args:
            api_key (str): YouTube Data API key
        """
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
    def get_video_info(self, video_id):
        """
        Get basic information about a video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video information
        """
        try:
            request = self.youtube.videos().list(
                part='snippet,statistics',
                id=video_id
            )
            response = request.execute()
            
            if response['items']:
                video = response['items'][0]
                return {
                    'video_id': video_id,
                    'title': video['snippet']['title'],
                    'channel': video['snippet']['channelTitle'],
                    'published_at': video['snippet']['publishedAt'],
                    'view_count': video['statistics'].get('viewCount', 0),
                    'like_count': video['statistics'].get('likeCount', 0),
                    'comment_count': video['statistics'].get('commentCount', 0)
                }
        except HttpError as e:
            print(f"Error fetching video info: {e}")
            return None
    
    def scrape_comments(self, video_id, max_comments=1000, include_replies=False):
        """
        Scrape comments from a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            max_comments (int): Maximum number of comments to fetch
            include_replies (bool): Whether to include replies to comments
            
        Returns:
            list: List of comment dictionaries
        """
        comments = []
        next_page_token = None
        
        print(f"Scraping comments from video: {video_id}")
        video_info = self.get_video_info(video_id)
        
        if not video_info:
            print("Could not fetch video info")
            return []
        
        print(f"Video: {video_info['title']}")
        print(f"Total comments available: {video_info['comment_count']}")
        
        with tqdm(total=min(max_comments, int(video_info['comment_count']))) as pbar:
            while len(comments) < max_comments:
                try:
                    request = self.youtube.commentThreads().list(
                        part='snippet,replies',
                        videoId=video_id,
                        maxResults=100,  # Max allowed by API
                        pageToken=next_page_token,
                        textFormat='plainText',
                        order='relevance'  # or 'time'
                    )
                    response = request.execute()
                    
                    for item in response['items']:
                        # Top-level comment
                        top_comment = item['snippet']['topLevelComment']['snippet']
                        comment_data = {
                            'comment_id': item['snippet']['topLevelComment']['id'],
                            'video_id': video_id,
                            'video_title': video_info['title'],
                            'author': top_comment['authorDisplayName'],
                            'text': top_comment['textDisplay'],
                            'like_count': top_comment['likeCount'],
                            'published_at': top_comment['publishedAt'],
                            'updated_at': top_comment['updatedAt'],
                            'is_reply': False,
                            'parent_id': None,
                            'scraped_at': datetime.now().isoformat()
                        }
                        comments.append(comment_data)
                        pbar.update(1)
                        
                        # Get replies if requested
                        if include_replies and 'replies' in item:
                            for reply in item['replies']['comments']:
                                reply_snippet = reply['snippet']
                                reply_data = {
                                    'comment_id': reply['id'],
                                    'video_id': video_id,
                                    'video_title': video_info['title'],
                                    'author': reply_snippet['authorDisplayName'],
                                    'text': reply_snippet['textDisplay'],
                                    'like_count': reply_snippet['likeCount'],
                                    'published_at': reply_snippet['publishedAt'],
                                    'updated_at': reply_snippet['updatedAt'],
                                    'is_reply': True,
                                    'parent_id': item['snippet']['topLevelComment']['id'],
                                    'scraped_at': datetime.now().isoformat()
                                }
                                comments.append(reply_data)
                                pbar.update(1)
                        
                        if len(comments) >= max_comments:
                            break
                    
                    # Check if there are more pages
                    next_page_token = response.get('nextPageToken')
                    if not next_page_token:
                        break
                    
                    # Small delay to respect rate limits
                    time.sleep(0.1)
                    
                except HttpError as e:
                    print(f"\nError fetching comments: {e}")
                    break
        
        print(f"\nScraped {len(comments)} comments")
        return comments
    
    def scrape_multiple_videos(self, video_ids, max_comments_per_video=1000):
        """
        Scrape comments from multiple videos
        
        Args:
            video_ids (list): List of YouTube video IDs
            max_comments_per_video (int): Max comments per video
            
        Returns:
            list: Combined list of all comments
        """
        all_comments = []
        
        for video_id in video_ids:
            comments = self.scrape_comments(video_id, max_comments_per_video)
            all_comments.extend(comments)
            print(f"Total comments collected so far: {len(all_comments)}\n")
        
        return all_comments
    
    def save_to_csv(self, comments, filename='youtube_comments.csv'):
        """
        Save comments to CSV file
        
        Args:
            comments (list): List of comment dictionaries
            filename (str): Output filename
        """
        if not comments:
            print("No comments to save")
            return
        
        df = pd.DataFrame(comments)
        output_path = os.path.join('data', 'raw', filename)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Saved {len(comments)} comments to {output_path}")
        
        return output_path


# Example usage
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    # Initialize scraper
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("Error: YOUTUBE_API_KEY not found in .env file")
        exit(1)
    
    scraper = YouTubeScraper(api_key)
    
    # Example: Scrape comments from a video
    video_id = "dQw4w9WgXcQ"  # Replace with actual video ID
    comments = scraper.scrape_comments(video_id, max_comments=100, include_replies=True)
    
    # Save to CSV
    scraper.save_to_csv(comments)