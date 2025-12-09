#!/usr/bin/env python
"""
Automated Comment Analysis Pipeline
Scrapes comments from YouTube and Steam, then automatically categorizes negative comments.

Usage:
    python run_automated_analysis.py
"""

import sys
from pathlib import Path
from datetime import datetime
import os

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.youtube_scraper import YouTubeScraper
from scrapers.steam_scraper import SteamScraperSimple
from preprocessing import TextCleaner, TextPreprocessor
from analysis.sentiment_classifier import NegativeSentimentClassifier
import pandas as pd
import yaml
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)


def scrape_youtube_comments(config):
    """Scrape comments from YouTube videos"""
    print_banner("STEP 1: SCRAPING YOUTUBE COMMENTS")
    
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("⚠️  Warning: YOUTUBE_API_KEY not found in .env file")
        print("Skipping YouTube scraping...")
        return None
    
    youtube_config = config.get('youtube', {})
    video_ids = youtube_config.get('videos', [])
    
    if not video_ids:
        print("⚠️  No YouTube video IDs configured in config.yaml")
        print("Skipping YouTube scraping...")
        return None
    
    scraper = YouTubeScraper(api_key)
    max_comments = youtube_config.get('max_comments', 1000)
    include_replies = youtube_config.get('include_replies', True)
    
    print(f"📹 Scraping from {len(video_ids)} video(s)...")
    all_comments = scraper.scrape_multiple_videos(video_ids, max_comments)
    
    if all_comments:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'youtube_comments_{timestamp}.csv'
        output_path = scraper.save_to_csv(all_comments, filename)
        print(f"✅ YouTube scraping complete: {len(all_comments)} comments")
        return output_path
    
    return None


def scrape_steam_reviews(config):
    """Scrape reviews from Steam games"""
    print_banner("STEP 2: SCRAPING STEAM REVIEWS")
    
    steam_config = config.get('steam', {})
    game_ids = steam_config.get('games', [])
    
    if not game_ids:
        print("⚠️  No Steam game IDs configured in config.yaml")
        print("Skipping Steam scraping...")
        return None
    
    scraper = SteamScraperSimple()
    max_reviews = steam_config.get('max_reviews', 1000)
    
    all_reviews = []
    print(f"🎮 Scraping from {len(game_ids)} game(s)...")
    
    for game_id in game_ids:
        reviews = scraper.scrape_reviews(game_id, max_reviews)
        all_reviews.extend(reviews)
        print()
    
    if all_reviews:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f'steam_reviews_{timestamp}.csv'
        output_path = scraper.save_to_csv(all_reviews, filename)
        print(f"✅ Steam scraping complete: {len(all_reviews)} reviews")
        return output_path
    
    return None


def preprocess_data(input_files, config):
    """Preprocess all scraped data"""
    print_banner("STEP 3: PREPROCESSING DATA")
    
    if not input_files:
        print("❌ No data files to preprocess")
        return None
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor(
        use_cleaner=True,
        cleaner_config={
            'remove_urls': True,
            'remove_html': True,
            'remove_emails': True,
            'remove_extra_whitespace': True,
            'lowercase': False  # Keep original case for better sentiment analysis
        }
    )
    
    combined_data = []
    
    for file_path in input_files:
        if file_path and os.path.exists(file_path):
            print(f"📂 Loading: {file_path}")
            df = pd.read_csv(file_path)
            
            # Identify text column
            text_col = None
            if 'text' in df.columns:
                text_col = 'text'
            elif 'comment' in df.columns:
                text_col = 'comment'
            elif 'review' in df.columns:
                text_col = 'review'
            
            if text_col:
                print(f"   Preprocessing '{text_col}' column...")
                df = preprocessor.preprocess_dataframe(
                    df, 
                    text_column=text_col,
                    output_column='preprocessed_text'
                )
                # Keep both original and preprocessed
                combined_data.append(df)
            else:
                print(f"   ⚠️  Warning: No text column found, using raw data")
                combined_data.append(df)
    
    if combined_data:
        # Combine all data
        combined_df = pd.concat(combined_data, ignore_index=True)
        
        # Standardize column name to 'text'
        if 'text' not in combined_df.columns:
            if 'review' in combined_df.columns:
                combined_df['text'] = combined_df['review']
            elif 'comment' in combined_df.columns:
                combined_df['text'] = combined_df['comment']
        
        print(f"\n✅ Preprocessing complete: {len(combined_df)} total comments")
        return combined_df
    
    return None


def classify_negative_comments(df, config):
    """Classify and filter negative comments"""
    print_banner("STEP 4: CLASSIFYING NEGATIVE COMMENTS")
    
    if df is None or df.empty:
        print("❌ No data to classify")
        return None, None
    
    # Initialize classifier
    classifier = NegativeSentimentClassifier(config_path='config.yaml')
    
    # Filter negative comments
    negative_comments = classifier.filter_negative_comments(df)
    
    if negative_comments.empty:
        print("ℹ️  No negative comments found")
        return df, None
    
    # Get statistics
    stats = classifier.analyze_negative_comments(negative_comments)
    
    print("\n" + "📊 NEGATIVE COMMENT STATISTICS")
    print("-" * 80)
    print(f"Total comments analyzed: {len(df)}")
    print(f"Negative comments found: {stats['total_negative']}")
    print(f"Negative rate: {stats['total_negative']/len(df)*100:.1f}%")
    print(f"\nAverage negative score: {stats['avg_negative_score']:.3f}")
    print(f"Median negative score: {stats['median_negative_score']:.3f}")
    print(f"\nBreakdown by severity:")
    print(f"  🔴 Highly negative (≥0.8):      {stats['highly_negative_count']}")
    print(f"  🟠 Moderately negative (0.6-0.8): {stats['moderately_negative_count']}")
    print(f"  🟡 Mildly negative (<0.6):       {stats['mildly_negative_count']}")
    
    return df, negative_comments


def display_top_negatives(negative_df, top_n=10):
    """Display the most negative comments"""
    print_banner(f"TOP {top_n} MOST NEGATIVE COMMENTS")
    
    if negative_df is None or negative_df.empty:
        print("No negative comments to display")
        return
    
    text_col = 'text' if 'text' in negative_df.columns else 'comment'
    
    for i, (idx, row) in enumerate(negative_df.head(top_n).iterrows(), 1):
        print(f"\n{i}. NEGATIVE SCORE: {row['negative_score']:.3f}")
        comment_text = str(row[text_col])[:200]
        print(f"   {comment_text}{'...' if len(str(row[text_col])) > 200 else ''}")
        
        # Show source if available
        if 'video_title' in row:
            print(f"   📹 Source: {row['video_title']}")
        elif 'app_id' in row:
            print(f"   🎮 Source: Steam App ID {row['app_id']}")
        
        print("-" * 80)


def save_results(all_comments_df, negative_df):
    """Save results to CSV files"""
    print_banner("STEP 5: SAVING RESULTS")
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_dir = Path('results')
    results_dir.mkdir(exist_ok=True)
    
    saved_files = []
    
    # Save all classified comments
    if all_comments_df is not None and not all_comments_df.empty:
        all_file = results_dir / f'all_comments_classified_{timestamp}.csv'
        all_comments_df.to_csv(all_file, index=False)
        print(f"💾 All comments saved: {all_file}")
        saved_files.append(str(all_file))
    
    # Save negative comments
    if negative_df is not None and not negative_df.empty:
        neg_file = results_dir / f'negative_comments_{timestamp}.csv'
        negative_df.to_csv(neg_file, index=False)
        print(f"💾 Negative comments saved: {neg_file}")
        saved_files.append(str(neg_file))
        
        # Save highly negative comments separately
        highly_negative = negative_df[negative_df['negative_score'] >= 0.8]
        if not highly_negative.empty:
            high_file = results_dir / f'highly_negative_comments_{timestamp}.csv'
            highly_negative.to_csv(high_file, index=False)
            print(f"💾 Highly negative comments saved: {high_file}")
            saved_files.append(str(high_file))
    
    return saved_files


def main():
    """Main automated pipeline"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "AUTOMATED COMMENT ANALYSIS PIPELINE" + " " * 23 + "║")
    print("╚" + "═" * 78 + "╝")
    
    start_time = datetime.now()
    
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Step 1 & 2: Scrape data
    scraped_files = []
    
    youtube_file = scrape_youtube_comments(config)
    if youtube_file:
        scraped_files.append(youtube_file)
    
    steam_file = scrape_steam_reviews(config)
    if steam_file:
        scraped_files.append(steam_file)
    
    if not scraped_files:
        print("\n❌ No data was scraped. Please check your configuration and API keys.")
        return
    
    # Step 3: Preprocess
    combined_df = preprocess_data(scraped_files, config)
    
    if combined_df is None:
        print("\n❌ Preprocessing failed.")
        return
    
    # Step 4: Classify
    all_comments_df, negative_df = classify_negative_comments(combined_df, config)
    
    # Display top negatives
    if negative_df is not None and not negative_df.empty:
        display_top_negatives(negative_df, top_n=10)
    
    # Step 5: Save results
    saved_files = save_results(all_comments_df, negative_df)
    
    # Summary
    print_banner("ANALYSIS COMPLETE!")
    
    elapsed_time = datetime.now() - start_time
    print(f"\n⏱️  Total execution time: {elapsed_time.total_seconds():.1f} seconds")
    print(f"\n📁 Results saved to:")
    for file in saved_files:
        print(f"   • {file}")
    
    print("\n✅ Pipeline completed successfully!\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
