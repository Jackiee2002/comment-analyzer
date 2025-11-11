"""
Simple Steam Review Scraper
Direct API calls to Steam - faster and no rate limit issues for small batches
"""

import requests
import pandas as pd
from datetime import datetime
import time

class SteamScraperSimple:
    def __init__(self):
        """Initialize simple Steam scraper"""
        self.base_url = "https://store.steampowered.com/appreviews/"
    
    def scrape_reviews(self, app_id, max_reviews=20):
        """
        Scrape reviews from Steam using direct API
        
        Args:
            app_id (str): Steam App ID
            max_reviews (int): Maximum number of reviews to fetch
            
        Returns:
            list: List of review dictionaries
        """
        reviews = []
        
        print(f"Scraping reviews for Steam App ID: {app_id}")
        print(f"Fetching {max_reviews} reviews...\n")
        
        params = {
            'json': 1,
            'filter': 'recent',
            'language': 'english',
            'num_per_page': min(max_reviews, 100),  # Max 100 per request
            'purchase_type': 'all'
        }
        
        try:
            url = f"{self.base_url}{app_id}"
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"Error: HTTP {response.status_code}")
                return []
            
            data = response.json()
            
            if not data.get('success'):
                print("Failed to fetch reviews")
                return []
            
            review_list = data.get('reviews', [])
            
            if not review_list:
                print("No reviews found")
                return []
            
            print(f"Processing {len(review_list)} reviews...")
            
            for review_data in review_list[:max_reviews]:
                # Convert playtime
                playtime_hours = round(review_data.get('author', {}).get('playtime_forever', 0) / 60, 1)
                
                review = {
                    'review_id': review_data.get('recommendationid', ''),
                    'app_id': app_id,
                    'author_steamid': review_data.get('author', {}).get('steamid', ''),
                    'author_playtime_hours': playtime_hours,
                    'text': review_data.get('review', ''),
                    'timestamp_created': datetime.fromtimestamp(
                        review_data.get('timestamp_created', 0)
                    ).isoformat(),
                    'voted_up': review_data.get('voted_up', False),
                    'votes_up': review_data.get('votes_up', 0),
                    'votes_funny': review_data.get('votes_funny', 0),
                    'comment_count': review_data.get('comment_count', 0),
                    'steam_purchase': review_data.get('steam_purchase', False),
                    'language': review_data.get('language', ''),
                    'scraped_at': datetime.now().isoformat()
                }
                reviews.append(review)
            
            print(f"✅ Successfully scraped {len(reviews)} reviews")
            
        except requests.exceptions.Timeout:
            print("Request timed out")
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")
        
        return reviews
    
    def save_to_csv(self, reviews, filename='steam_reviews.csv'):
        """
        Save reviews to CSV file
        
        Args:
            reviews (list): List of review dictionaries
            filename (str): Output filename
        """
        if not reviews:
            print("No reviews to save")
            return None
        
        df = pd.DataFrame(reviews)
        output_path = f'data/raw/{filename}'
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"\n✓ Saved {len(reviews)} reviews to {output_path}")
        
        return output_path


# Test it directly
if __name__ == "__main__":
    scraper = SteamScraperSimple()
    
    app_id = "730"  # CS2
    reviews = scraper.scrape_reviews(app_id, max_reviews=20)
    
    if reviews:
        scraper.save_to_csv(reviews)
        print("\n✅ Test successful!")
    else:
        print("\n❌ Test failed")