"""
Test script for Steam scraper - Gathers real data from Steam
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scrapers.steam_scraper import SteamScraperSimple
import pandas as pd


def test_steam_scraper():
    """Test Steam scraper with real data collection"""
    print("="*70)
    print("STEAM SCRAPER TEST - Data Collection")
    print("="*70)
    
    # Initialize scraper
    scraper = SteamScraperSimple()
    
    # Test with Counter-Strike 2 (App ID: 730)
    print("\n[Test 1] Scraping Counter-Strike 2 reviews...")
    print("-"*70)
    app_id = "730"
    max_reviews = 20
    
    reviews = scraper.scrape_reviews(app_id, max_reviews=max_reviews)
    
    if reviews:
        print(f"\n✅ SUCCESS: Collected {len(reviews)} reviews")
        
        # Display sample review
        print("\n" + "="*70)
        print("SAMPLE REVIEW:")
        print("="*70)
        sample = reviews[0]
        print(f"Review ID: {sample['review_id']}")
        print(f"Voted Up: {sample['voted_up']}")
        print(f"Playtime: {sample['author_playtime_hours']} hours")
        print(f"Votes Up: {sample['votes_up']}")
        print(f"Text: {sample['text'][:200]}...")
        
        # Save to CSV
        df = pd.DataFrame(reviews)
        output_path = scraper.save_to_csv(reviews, filename='steam_cs2_test.csv')
        
        # Show statistics
        print("\n" + "="*70)
        print("STATISTICS:")
        print("="*70)
        print(f"Total reviews collected: {len(df)}")
        print(f"Positive reviews: {df['voted_up'].sum()}")
        print(f"Negative reviews: {(~df['voted_up']).sum()}")
        print(f"Average playtime: {df['author_playtime_hours'].mean():.1f} hours")
        print(f"Total votes up: {df['votes_up'].sum()}")
        
        # Show positive/negative ratio
        positive_rate = (df['voted_up'].sum() / len(df)) * 100
        print(f"\nPositive rate: {positive_rate:.1f}%")
        print(f"Negative rate: {100-positive_rate:.1f}%")
        
        return True
    else:
        print("\n❌ FAILED: No reviews collected")
        return False


def test_multiple_games():
    """Test scraping multiple games"""
    print("\n\n" + "="*70)
    print("MULTI-GAME TEST")
    print("="*70)
    
    scraper = SteamScraperSimple()
    
    games = [
        ("730", "Counter-Strike 2", 10),
        ("570", "Dota 2", 10),
    ]
    
    all_reviews = []
    
    for app_id, game_name, max_reviews in games:
        print(f"\n[Scraping {game_name}]")
        print("-"*70)
        reviews = scraper.scrape_reviews(app_id, max_reviews=max_reviews)
        if reviews:
            all_reviews.extend(reviews)
            print(f"✅ Collected {len(reviews)} reviews from {game_name}")
        else:
            print(f"❌ Failed to collect reviews from {game_name}")
    
    if all_reviews:
        print(f"\n✅ TOTAL: Collected {len(all_reviews)} reviews from {len(games)} games")
        
        # Save combined results
        df = pd.DataFrame(all_reviews)
        scraper.save_to_csv(all_reviews, filename='steam_multi_game_test.csv')
        
        # Show breakdown by game
        print("\nBreakdown by game:")
        for app_id, game_name, _ in games:
            game_reviews = df[df['app_id'] == app_id]
            print(f"  {game_name}: {len(game_reviews)} reviews")
        
        return True
    else:
        print("\n❌ No reviews collected from any game")
        return False


if __name__ == "__main__":
    print("\n🚀 Starting Steam Scraper Tests...\n")
    
    # Run tests
    test1_passed = test_steam_scraper()
    test2_passed = test_multiple_games()
    
    # Summary
    print("\n\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Single game test: {'✅ PASSED' if test1_passed else '❌ FAILED'}")
    print(f"Multi-game test: {'✅ PASSED' if test2_passed else '❌ FAILED'}")
    
    if test1_passed and test2_passed:
        print("\n🎉 All tests passed! Steam scraper is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
