#!/usr/bin/env python
"""Simple test to see what's failing."""
import sys
import traceback

print("Starting test...")
print(f"Python: {sys.executable}")
print(f"Version: {sys.version}")

try:
    print("\n1. Testing imports...")
    import yaml
    print("   ✅ yaml")
    import pandas as pd
    print("   ✅ pandas")
    from pathlib import Path
    print("   ✅ pathlib")
    
    print("\n2. Testing config load...")
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    print("   ✅ config.yaml loaded")
    
    print("\n3. Testing src imports...")
    sys.path.insert(0, str(Path(__file__).parent / "src"))
    from scrapers.youtube_scraper import YouTubeScraper
    print("   ✅ YouTubeScraper")
    from scrapers.steam_scraper import SteamScraperSimple
    print("   ✅ SteamScraperSimple")
    from preprocessing import TextCleaner, TextPreprocessor
    print("   ✅ TextCleaner, TextPreprocessor")
    from analysis.sentiment_classifier import NegativeSentimentClassifier
    print("   ✅ NegativeSentimentClassifier")
    
    print("\n✅ All tests passed! Your environment is ready.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)
