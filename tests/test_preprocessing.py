"""
Test script for preprocessing module
Tests text cleaning and preprocessing functionality
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from preprocessing import TextCleaner, TextPreprocessor
import pandas as pd


def test_text_cleaner():
    """Test TextCleaner functionality"""
    print("="*80)
    print("TEXT CLEANER TESTS")
    print("="*80)
    
    cleaner = TextCleaner(
        remove_urls=True,
        remove_html=True,
        remove_emails=True,
        remove_extra_whitespace=True,
        lowercase=False
    )
    
    test_cases = [
        {
            'name': 'URL Removal',
            'input': 'Check this out: https://example.com/page and http://test.com',
            'expected_contains': ['Check this out:', 'and'],
            'expected_not_contains': ['https://', 'http://']
        },
        {
            'name': 'HTML Removal',
            'input': 'This is <b>bold</b> &amp; <i>italic</i> text',
            'expected_contains': ['This is', 'bold', 'italic', 'text', '&'],
            'expected_not_contains': ['<b>', '</b>', '<i>', '&amp;']
        },
        {
            'name': 'Email Removal',
            'input': 'Contact us at support@example.com or sales@test.org',
            'expected_contains': ['Contact us at', 'or'],
            'expected_not_contains': ['support@example.com', 'sales@test.org']
        },
        {
            'name': 'Whitespace Normalization',
            'input': 'Too    many     spaces   here',
            'expected_contains': ['Too many spaces here'],
            'expected_not_contains': ['    ', '     ']
        }
    ]
    
    passed = 0
    failed = 0
    
    for test in test_cases:
        print(f"\n[Test: {test['name']}]")
        print(f"Input:  {test['input']}")
        
        result = cleaner.clean(test['input'])
        print(f"Output: {result}")
        
        # Check expected contains
        contains_check = all(item in result for item in test['expected_contains'])
        not_contains_check = all(item not in result for item in test['expected_not_contains'])
        
        if contains_check and not_contains_check:
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
            if not contains_check:
                print(f"   Missing expected: {[item for item in test['expected_contains'] if item not in result]}")
            if not not_contains_check:
                print(f"   Still contains: {[item for item in test['expected_not_contains'] if item in result]}")
            failed += 1
        print("-" * 80)
    
    # Test additional methods
    print("\n[Test: Emoji Removal]")
    emoji_text = "This is great! 😀😁😂🤣"
    emoji_removed = cleaner.remove_emojis(emoji_text)
    print(f"Input:  {emoji_text}")
    print(f"Output: {emoji_removed}")
    if '😀' not in emoji_removed and 'great' in emoji_removed:
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    print("\n[Test: Contraction Expansion]")
    contraction_text = "I'm can't won't shouldn't it's"
    expanded = cleaner.expand_contractions(contraction_text)
    print(f"Input:  {contraction_text}")
    print(f"Output: {expanded}")
    expected_expansions = ['i am', 'cannot', 'will not', 'should not', 'it is']
    if any(exp in expanded.lower() for exp in expected_expansions):
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    print("\n[Test: Number Removal]")
    number_text = "There are 123 items and 456 more"
    no_numbers = cleaner.remove_numbers(number_text)
    print(f"Input:  {number_text}")
    print(f"Output: {no_numbers}")
    if '123' not in no_numbers and '456' not in no_numbers and 'items' in no_numbers:
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    return passed, failed


def test_text_preprocessor():
    """Test TextPreprocessor functionality"""
    print("\n\n" + "="*80)
    print("TEXT PREPROCESSOR TESTS")
    print("="*80)
    
    preprocessor = TextPreprocessor(
        use_cleaner=True,
        cleaner_config={'lowercase': True, 'remove_urls': True}
    )
    
    passed = 0
    failed = 0
    
    # Test basic preprocessing
    print("\n[Test: Basic Preprocessing]")
    text = "This is a TEST with URLs https://example.com"
    result = preprocessor.preprocess(text)
    print(f"Input:  {text}")
    print(f"Output: {result}")
    if 'test' in result.lower() and 'https' not in result:
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    # Test stopword removal
    print("\n[Test: Stopword Removal]")
    text = "This is a test with the stopwords and more"
    result = preprocessor.preprocess(text, remove_stopwords=True)
    print(f"Input:  {text}")
    print(f"Output: {result}")
    removed_stopwords = ['is', 'a', 'the', 'and']
    if all(word not in result.lower().split() for word in removed_stopwords):
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    # Test tokenization
    print("\n[Test: Tokenization]")
    text = "Hello, world! This is a test."
    tokens = preprocessor.tokenize(text)
    print(f"Input:  {text}")
    print(f"Tokens: {tokens}")
    if len(tokens) == 5 and 'Hello' in tokens and 'test' in tokens:
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    # Test keyword extraction
    print("\n[Test: Keyword Extraction]")
    text = "This product is amazing. The quality is great and the price is good. Amazing value!"
    keywords = preprocessor.extract_keywords(text, top_n=3)
    print(f"Input:    {text}")
    print(f"Keywords: {keywords}")
    if len(keywords) <= 3 and keywords:
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    # Test word frequency
    print("\n[Test: Word Frequency]")
    texts = ["hello world", "hello there", "world peace"]
    freq = preprocessor.get_word_frequency(texts, top_n=3)
    print(f"Input:     {texts}")
    print(f"Frequency: {freq}")
    if 'hello' in freq and freq.get('hello', 0) == 2:
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    # Test DataFrame preprocessing
    print("\n[Test: DataFrame Preprocessing]")
    df = pd.DataFrame({
        'text': [
            'This is a test https://example.com',
            'Another TEST with CAPS',
            'Final test message here'
        ]
    })
    result_df = preprocessor.preprocess_dataframe(
        df, 
        text_column='text',
        remove_stopwords=False
    )
    print(f"Input rows: {len(df)}")
    print(f"Output has 'preprocessed_text' column: {'preprocessed_text' in result_df.columns}")
    print(f"Sample output: {result_df['preprocessed_text'].iloc[0]}")
    if 'preprocessed_text' in result_df.columns and len(result_df) == 3:
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    # Test custom stopwords
    print("\n[Test: Custom Stopwords]")
    preprocessor.add_stopwords(['product', 'item'])
    text = "This product is a great item"
    result = preprocessor.preprocess(text, remove_stopwords=True)
    print(f"Input:  {text}")
    print(f"Output: {result}")
    if 'product' not in result.lower() and 'item' not in result.lower():
        print("✅ PASSED")
        passed += 1
    else:
        print("❌ FAILED")
        failed += 1
    print("-" * 80)
    
    return passed, failed


def test_integration():
    """Test preprocessing with realistic comment data"""
    print("\n\n" + "="*80)
    print("INTEGRATION TEST - Realistic Comment Processing")
    print("="*80)
    
    # Simulate comment data
    comments = pd.DataFrame({
        'text': [
            "This game is TERRIBLE!!! Don't buy it! https://refund.com",
            "Amazing experience 😍😍 10/10 would recommend!!!",
            "I can't believe how bad this is... waste of money 💸",
            "BEST GAME EVER!!! <b>Highly recommended</b> @everyone",
            "Meh... it's okay I guess. Nothing special tbh",
        ]
    })
    
    # Initialize preprocessor
    preprocessor = TextPreprocessor(
        use_cleaner=True,
        cleaner_config={
            'remove_urls': True,
            'remove_html': True,
            'remove_mentions': True,
            'remove_extra_whitespace': True,
            'lowercase': True
        }
    )
    
    print(f"\nProcessing {len(comments)} comments...\n")
    
    # Process with different settings
    results = preprocessor.preprocess_dataframe(
        comments,
        text_column='text',
        output_column='preprocessed',
        remove_stopwords=False,
        min_word_length=2
    )
    
    # Show results
    print("\nResults:")
    print("-" * 80)
    for idx, row in results.iterrows():
        print(f"\nOriginal:     {row['text']}")
        print(f"Preprocessed: {row['preprocessed']}")
        
        # Extract keywords
        keywords = preprocessor.extract_keywords(row['preprocessed'], top_n=3)
        print(f"Keywords:     {keywords}")
    
    print("\n" + "="*80)
    print("✅ Integration test complete")
    
    return 1, 0


if __name__ == "__main__":
    print("\n🚀 Starting Preprocessing Module Tests...\n")
    
    # Run all tests
    cleaner_passed, cleaner_failed = test_text_cleaner()
    preprocessor_passed, preprocessor_failed = test_text_preprocessor()
    integration_passed, integration_failed = test_integration()
    
    # Summary
    total_passed = cleaner_passed + preprocessor_passed + integration_passed
    total_failed = cleaner_failed + preprocessor_failed + integration_failed
    total_tests = total_passed + total_failed
    
    print("\n\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"TextCleaner Tests:      {cleaner_passed} passed, {cleaner_failed} failed")
    print(f"TextPreprocessor Tests: {preprocessor_passed} passed, {preprocessor_failed} failed")
    print(f"Integration Tests:      {integration_passed} passed, {integration_failed} failed")
    print("-" * 80)
    print(f"TOTAL:                  {total_passed}/{total_tests} tests passed")
    print(f"Success Rate:           {(total_passed/total_tests)*100:.1f}%")
    
    if total_failed == 0:
        print("\n🎉 All tests passed! Preprocessing module is working correctly.")
    else:
        print(f"\n⚠️  {total_failed} test(s) failed. Check the output above for details.")
