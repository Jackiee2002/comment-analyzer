"""
Example: Using preprocessing with sentiment classification
Demonstrates the complete pipeline: scrape → preprocess → classify
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from preprocessing import TextCleaner, TextPreprocessor
from analysis.sentiment_classifier import NegativeSentimentClassifier
import pandas as pd


def example_basic_preprocessing():
    """Example 1: Basic text cleaning"""
    print("="*70)
    print("EXAMPLE 1: Basic Text Cleaning")
    print("="*70)
    
    cleaner = TextCleaner(
        remove_urls=True,
        remove_html=True,
        remove_emails=True,
        lowercase=True
    )
    
    raw_comments = [
        "This is TERRIBLE!!! Check https://example.com for refund",
        "Great product <b>highly recommended</b> contact@example.com",
        "I'm disappointed... it's not worth it"
    ]
    
    print("\nCleaning comments:")
    for i, comment in enumerate(raw_comments, 1):
        cleaned = cleaner.clean(comment)
        print(f"\n{i}. Original: {comment}")
        print(f"   Cleaned:  {cleaned}")


def example_advanced_preprocessing():
    """Example 2: Advanced preprocessing with sentiment analysis"""
    print("\n\n" + "="*70)
    print("EXAMPLE 2: Preprocessing + Sentiment Classification")
    print("="*70)
    
    # Sample comments (simulating scraped data)
    comments_df = pd.DataFrame({
        'text': [
            "This game is absolutely TERRIBLE!!! Don't waste your money! https://refund.com",
            "Amazing experience! 10/10 would recommend to everyone!",
            "I can't believe how bad this is... complete waste of time and money",
            "BEST GAME EVER!!! Exceeded all expectations! <b>Must buy!</b>",
            "Meh... it's okay I guess. Nothing special, pretty average",
            "Horrible customer service. No response to emails. Very frustrated!",
            "Love it! Works perfectly and shipping was super fast!",
            "Buggy, crashes constantly, terrible performance. Disappointed."
        ]
    })
    
    print(f"\nOriginal comments: {len(comments_df)}")
    
    # Step 1: Preprocess
    print("\n[Step 1] Preprocessing text...")
    preprocessor = TextPreprocessor(
        use_cleaner=True,
        cleaner_config={
            'remove_urls': True,
            'remove_html': True,
            'remove_extra_whitespace': True,
            'lowercase': True
        }
    )
    
    comments_df = preprocessor.preprocess_dataframe(
        comments_df,
        text_column='text',
        output_column='preprocessed_text',
        remove_stopwords=False,
        min_word_length=2
    )
    
    # Step 2: Classify sentiment
    print("\n[Step 2] Classifying sentiment...")
    classifier = NegativeSentimentClassifier()
    
    # Use preprocessed text for classification
    # Create a copy with renamed column
    classified_df = comments_df.copy()
    classified_df['text'] = classified_df['preprocessed_text']
    negative_comments = classifier.filter_negative_comments(classified_df)
    
    # Step 3: Analyze results
    print("\n[Step 3] Analyzing results...")
    stats = classifier.analyze_negative_comments(negative_comments)
    
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Total comments analyzed: {len(comments_df)}")
    print(f"Negative comments found: {stats['total_negative']}")
    print(f"Negative rate: {(stats['total_negative']/len(comments_df))*100:.1f}%")
    print(f"\nBreakdown:")
    print(f"  Highly negative:     {stats['highly_negative_count']}")
    print(f"  Moderately negative: {stats['moderately_negative_count']}")
    print(f"  Mildly negative:     {stats['mildly_negative_count']}")
    
    # Show top negative comments
    print("\n" + "="*70)
    print("TOP 3 MOST NEGATIVE COMMENTS")
    print("="*70)
    for idx, row in negative_comments.head(3).iterrows():
        print(f"\nScore: {row['negative_score']:.3f}")
        print(f"Original: {comments_df.loc[idx, 'text'][:100]}...")
        print(f"Cleaned:  {row['text'][:100]}...")


def example_keyword_extraction():
    """Example 3: Extract keywords from negative comments"""
    print("\n\n" + "="*70)
    print("EXAMPLE 3: Keyword Extraction from Negative Feedback")
    print("="*70)
    
    negative_comments = [
        "Terrible customer service, no response to emails",
        "Product quality is awful, broke after one use",
        "Shipping was slow and item arrived damaged",
        "Not worth the price, very disappointed with quality",
        "Bad experience, customer support was unhelpful"
    ]
    
    preprocessor = TextPreprocessor(
        use_cleaner=True,
        cleaner_config={'lowercase': True}
    )
    
    print("\nExtracting keywords from negative comments:")
    
    all_text = ' '.join(negative_comments)
    keywords = preprocessor.extract_keywords(all_text, top_n=10)
    
    print(f"\nTop 10 keywords: {keywords}")
    
    # Word frequency
    freq = preprocessor.get_word_frequency(negative_comments, top_n=10)
    
    print("\nWord frequency:")
    for word, count in freq.items():
        print(f"  {word:15} {count}")


def example_custom_pipeline():
    """Example 4: Custom preprocessing pipeline"""
    print("\n\n" + "="*70)
    print("EXAMPLE 4: Custom Preprocessing Pipeline")
    print("="*70)
    
    # Custom cleaner for gaming reviews
    cleaner = TextCleaner(
        remove_urls=True,
        remove_html=True,
        remove_mentions=True,  # Remove @mentions
        remove_hashtags=True,  # Remove #hashtags
        remove_extra_whitespace=True,
        lowercase=True
    )
    
    gaming_comments = [
        "@dev This game is trash!!! #disappointed #refund https://steam.com/refund",
        "Amazing graphics but gameplay is boring... not worth $60",
        "10/10 GOTY!!! @everyone should play this!!! #gaming #masterpiece"
    ]
    
    print("\nCleaning gaming comments with custom settings:")
    for comment in gaming_comments:
        print(f"\nOriginal:  {comment}")
        
        # Clean
        cleaned = cleaner.clean(comment)
        print(f"Cleaned:   {cleaned}")
        
        # Remove emojis
        no_emoji = cleaner.remove_emojis(cleaned)
        print(f"No emoji:  {no_emoji}")
        
        # Remove numbers
        no_numbers = cleaner.remove_numbers(no_emoji)
        print(f"No numbers: {no_numbers}")
        
        # Normalize repetitions
        normalized = cleaner.normalize_repetitions(no_numbers)
        print(f"Normalized: {normalized}")


def example_dataframe_workflow():
    """Example 5: Complete DataFrame workflow"""
    print("\n\n" + "="*70)
    print("EXAMPLE 5: Complete DataFrame Preprocessing Workflow")
    print("="*70)
    
    # Simulate loaded data from Steam/YouTube
    df = pd.DataFrame({
        'comment': [
            "This is TERRIBLE!!! https://example.com",
            "Great product! Highly recommended!",
            "I'm very disappointed with the quality...",
            "BEST PURCHASE EVER!!!",
            "Not worth it. Waste of money. 0/10"
        ],
        'source': ['steam', 'youtube', 'steam', 'youtube', 'steam'],
        'likes': [45, 120, 30, 200, 15]
    })
    
    print(f"\nOriginal DataFrame: {len(df)} rows")
    print(df[['comment', 'source']].to_string(index=False))
    
    # Preprocess
    preprocessor = TextPreprocessor(
        use_cleaner=True,
        cleaner_config={
            'remove_urls': True,
            'remove_extra_whitespace': True,
            'lowercase': True
        }
    )
    
    df = preprocessor.preprocess_dataframe(
        df,
        text_column='comment',
        output_column='clean_comment',
        remove_stopwords=False
    )
    
    print("\n\nProcessed DataFrame:")
    print(df[['comment', 'clean_comment', 'source']].to_string(index=False))
    
    # Save to CSV
    output_path = Path("results") / "preprocessed_comments.csv"
    output_path.parent.mkdir(exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\n✓ Saved to: {output_path}")


if __name__ == "__main__":
    print("\nPreprocessing + Sentiment Analysis Examples\n")
    
    # Run all examples
    example_basic_preprocessing()
    example_advanced_preprocessing()
    example_keyword_extraction()
    example_custom_pipeline()
    example_dataframe_workflow()
    
    print("\n\n" + "="*70)
    print("All examples completed!")
    print("="*70)
    print("\nNext steps:")
    print("1. Try preprocessing your own comment data")
    print("2. Adjust cleaner settings for your use case")
    print("3. Combine with sentiment classification")
    print("4. Extract keywords and analyze patterns")
