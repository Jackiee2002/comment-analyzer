"""
Test script for YouTube scraper - Gathers real data from YouTube
Note: Requires YOUTUBE_API_KEY in .env file
"""
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scrapers.youtube_scraper import YouTubeScraper
import pandas as pd
from dotenv import load_dotenv


def test_youtube_scraper():
    """Test YouTube scraper with real data collection"""
    print("="*70)
    print("YOUTUBE SCRAPER TEST - Data Collection")
    print("="*70)
    
    # Load environment variables
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: YOUTUBE_API_KEY not found in .env file")
        print("\nTo fix this:")
        print("1. Create a .env file in the project root")
        print("2. Add: YOUTUBE_API_KEY=your_api_key_here")
        print("3. Get API key from: https://console.cloud.google.com/")
        return False
    
    # Initialize scraper
    scraper = YouTubeScraper(api_key)
    
    # Test with a popular video (Using a generic popular video ID)
    # Replace with actual video IDs you want to test
    print("\n[Test 1] Scraping YouTube comments...")
    print("-"*70)
    
    # Example: Use a well-known video ID (you should replace this)
    video_id = "dQw4w9WgXcQ"  # Replace with actual video ID
    max_comments = 20
    
    print(f"Video ID: {video_id}")
    print(f"Max comments: {max_comments}")
    
    try:
        comments = scraper.scrape_comments(video_id, max_comments=max_comments, include_replies=False)
        
        if comments:
            print(f"\n✅ SUCCESS: Collected {len(comments)} comments")
            
            # Display sample comment
            print("\n" + "="*70)
            print("SAMPLE COMMENT:")
            print("="*70)
            sample = comments[0]
            print(f"Comment ID: {sample['comment_id']}")
            print(f"Author: {sample['author']}")
            print(f"Likes: {sample['like_count']}")
            print(f"Published: {sample['published_at']}")
            print(f"Text: {sample['text'][:200]}...")
            
            # Save to CSV
            df = pd.DataFrame(comments)
            output_path = scraper.save_to_csv(comments, filename='youtube_test.csv')
            
            # Show statistics
            print("\n" + "="*70)
            print("STATISTICS:")
            print("="*70)
            print(f"Total comments collected: {len(df)}")
            print(f"Unique authors: {df['author'].nunique()}")
            print(f"Total likes: {df['like_count'].sum()}")
            print(f"Average likes per comment: {df['like_count'].mean():.1f}")
            print(f"Comments with replies: {df[df['is_reply']].shape[0]}")
            
            # Show top liked comments
            top_liked = df.nlargest(3, 'like_count')
            print("\nTop 3 most liked comments:")
            for idx, row in top_liked.iterrows():
                print(f"  • {row['like_count']} likes: {row['text'][:80]}...")
            
            return True
        else:
            print("\n❌ FAILED: No comments collected")
            print("This might be due to:")
            print("  - Comments disabled on the video")
            print("  - Invalid video ID")
            print("  - API quota exceeded")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_multiple_videos():
    """Test scraping multiple videos"""
    print("\n\n" + "="*70)
    print("MULTI-VIDEO TEST")
    print("="*70)
    
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: YOUTUBE_API_KEY not found")
        return False
    
    scraper = YouTubeScraper(api_key)
    
    # Replace with actual video IDs you want to test
    videos = [
        ("dQw4w9WgXcQ", 10),  # Replace with real video ID
        ("dQw4w9WgXcQ", 10),  # Replace with real video ID
    ]
    
    print("\nNote: Replace video IDs in the test file with real YouTube video IDs")
    print("Current IDs are placeholders only\n")
    
    all_comments = []
    
    for video_id, max_comments in videos:
        print(f"\n[Scraping video {video_id}]")
        print("-"*70)
        try:
            comments = scraper.scrape_comments(video_id, max_comments=max_comments)
            if comments:
                all_comments.extend(comments)
                print(f"✅ Collected {len(comments)} comments")
            else:
                print(f"❌ No comments collected")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    if all_comments:
        print(f"\n✅ TOTAL: Collected {len(all_comments)} comments from {len(videos)} videos")
        
        # Save combined results
        df = pd.DataFrame(all_comments)
        scraper.save_to_csv(all_comments, filename='youtube_multi_video_test.csv')
        
        # Show breakdown by video
        print("\nBreakdown by video:")
        video_counts = df['video_id'].value_counts()
        for video_id, count in video_counts.items():
            print(f"  {video_id}: {count} comments")
        
        return True
    else:
        print("\n❌ No comments collected from any video")
        return False


def test_with_replies():
    """Test scraping comments with replies"""
    print("\n\n" + "="*70)
    print("COMMENTS WITH REPLIES TEST")
    print("="*70)
    
    load_dotenv()
    api_key = os.getenv('YOUTUBE_API_KEY')
    
    if not api_key:
        print("\n❌ ERROR: YOUTUBE_API_KEY not found")
        return False
    
    scraper = YouTubeScraper(api_key)
    
    video_id = "dQw4w9WgXcQ"  # Replace with actual video ID
    max_comments = 15
    
    print(f"\nScraping {max_comments} comments with replies...")
    print("-"*70)
    
    try:
        comments = scraper.scrape_comments(video_id, max_comments=max_comments, include_replies=True)
        
        if comments:
            df = pd.DataFrame(comments)
            top_level = df[~df['is_reply']]
            replies = df[df['is_reply']]
            
            print(f"\n✅ SUCCESS:")
            print(f"  Top-level comments: {len(top_level)}")
            print(f"  Replies: {len(replies)}")
            print(f"  Total: {len(df)}")
            
            scraper.save_to_csv(comments, filename='youtube_with_replies_test.csv')
            
            return True
        else:
            print("\n❌ FAILED: No comments collected")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting YouTube Scraper Tests...\n")
    
    # Check for API key first
    load_dotenv()
    if not os.getenv('YOUTUBE_API_KEY'):
        print("⚠️  SETUP REQUIRED:")
        print("="*70)
        print("Before running YouTube tests, you need to:")
        print("1. Create a .env file in the project root directory")
        print("2. Add your YouTube API key: YOUTUBE_API_KEY=your_key_here")
        print("3. Get your API key from: https://console.cloud.google.com/")
        print("\nAlso update the video IDs in this test file with real YouTube video IDs")
        print("="*70)
        sys.exit(1)
    
    # Run tests
    test1_passed = test_youtube_scraper()
    test2_passed = test_multiple_videos()
    test3_passed = test_with_replies()
    
    # Summary
    print("\n\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Single video test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Multi-video test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    print(f"With replies test: {'✅ PASSED' if test3_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed and test3_passed:
        print("\n🎉 All tests passed! YouTube scraper is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
