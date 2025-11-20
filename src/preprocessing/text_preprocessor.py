"""
Text preprocessor for advanced NLP operations.
Includes tokenization, stopword removal, lemmatization, and more.
"""
import re
import pandas as pd
from typing import List, Optional, Union
from .text_cleaner import TextCleaner


class TextPreprocessor:
    """
    Advanced text preprocessing for NLP tasks.
    Combines cleaning, tokenization, and normalization.
    """
    
    def __init__(self, 
                 use_cleaner: bool = True,
                 cleaner_config: Optional[dict] = None):
        """
        Initialize preprocessor.
        
        Args:
            use_cleaner: Whether to use text cleaner
            cleaner_config: Configuration for TextCleaner
        """
        self.use_cleaner = use_cleaner
        
        if use_cleaner:
            cleaner_config = cleaner_config or {}
            self.cleaner = TextCleaner(**cleaner_config)
        
        # Common English stopwords (basic set)
        self.stopwords = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
            'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
            'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
            'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once'
        }
    
    def preprocess(self, text: str, 
                   remove_stopwords: bool = False,
                   min_word_length: int = 1,
                   expand_contractions: bool = False) -> str:
        """
        Preprocess a single text.
        
        Args:
            text: Raw text to preprocess
            remove_stopwords: Remove common stopwords
            min_word_length: Minimum word length to keep
            expand_contractions: Expand contractions (I'm -> I am)
            
        Returns:
            str: Preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Clean text first
        if self.use_cleaner:
            text = self.cleaner.clean(text)
        
        # Expand contractions
        if expand_contractions and self.use_cleaner:
            text = self.cleaner.expand_contractions(text)
        
        # Tokenize
        words = self.tokenize(text)
        
        # Remove stopwords
        if remove_stopwords:
            words = [w for w in words if w.lower() not in self.stopwords]
        
        # Filter by word length
        if min_word_length > 1:
            words = [w for w in words if len(w) >= min_word_length]
        
        return ' '.join(words)
    
    def tokenize(self, text: str) -> List[str]:
        """
        Simple word tokenization.
        
        Args:
            text: Text to tokenize
            
        Returns:
            List[str]: List of tokens
        """
        # Split on whitespace and punctuation, keep words
        tokens = re.findall(r'\b\w+\b', text)
        return [t for t in tokens if t]
    
    def remove_stopwords(self, text: str, custom_stopwords: Optional[set] = None) -> str:
        """
        Remove stopwords from text.
        
        Args:
            text: Text to process
            custom_stopwords: Optional custom stopword set to use instead
            
        Returns:
            str: Text without stopwords
        """
        stopwords = custom_stopwords if custom_stopwords else self.stopwords
        words = self.tokenize(text)
        filtered_words = [w for w in words if w.lower() not in stopwords]
        return ' '.join(filtered_words)
    
    def add_stopwords(self, words: Union[str, List[str]]):
        """
        Add custom stopwords.
        
        Args:
            words: Single word or list of words to add
        """
        if isinstance(words, str):
            words = [words]
        self.stopwords.update(w.lower() for w in words)
    
    def remove_stopword_entries(self, words: Union[str, List[str]]):
        """
        Remove words from stopword list.
        
        Args:
            words: Single word or list of words to remove
        """
        if isinstance(words, str):
            words = [words]
        self.stopwords.difference_update(w.lower() for w in words)
    
    def preprocess_dataframe(self, df: pd.DataFrame, 
                            text_column: str,
                            output_column: str = 'preprocessed_text',
                            **preprocess_kwargs) -> pd.DataFrame:
        """
        Preprocess text in a pandas DataFrame.
        
        Args:
            df: DataFrame containing text data
            text_column: Name of column with text to preprocess
            output_column: Name for output column
            **preprocess_kwargs: Arguments to pass to preprocess()
            
        Returns:
            pd.DataFrame: DataFrame with preprocessed text column
        """
        if text_column not in df.columns:
            raise ValueError(f"Column '{text_column}' not found in DataFrame")
        
        print(f"Preprocessing {len(df)} texts...")
        df[output_column] = df[text_column].fillna('').apply(
            lambda x: self.preprocess(x, **preprocess_kwargs)
        )
        
        print(f"✓ Preprocessing complete. Results in '{output_column}' column")
        return df
    
    def get_word_frequency(self, texts: Union[str, List[str]], 
                          top_n: Optional[int] = None) -> dict:
        """
        Get word frequency from text(s).
        
        Args:
            texts: Single text or list of texts
            top_n: Return only top N most frequent words
            
        Returns:
            dict: Word frequency dictionary
        """
        if isinstance(texts, str):
            texts = [texts]
        
        word_freq = {}
        for text in texts:
            words = self.tokenize(text.lower())
            for word in words:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        word_freq = dict(sorted(word_freq.items(), key=lambda x: x[1], reverse=True))
        
        if top_n:
            word_freq = dict(list(word_freq.items())[:top_n])
        
        return word_freq
    
    def filter_by_length(self, text: str, min_length: int = 0, max_length: Optional[int] = None) -> str:
        """
        Filter text by total character length.
        
        Args:
            text: Text to filter
            min_length: Minimum character length
            max_length: Maximum character length (None for no limit)
            
        Returns:
            str: Filtered text or empty string if doesn't meet criteria
        """
        if len(text) < min_length:
            return ""
        if max_length and len(text) > max_length:
            return text[:max_length]
        return text
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """
        Extract keywords from text based on frequency.
        
        Args:
            text: Text to extract keywords from
            top_n: Number of keywords to extract
            
        Returns:
            List[str]: List of keywords
        """
        # Preprocess and remove stopwords
        processed_text = self.preprocess(text, remove_stopwords=True, min_word_length=3)
        
        # Get word frequency
        word_freq = self.get_word_frequency(processed_text, top_n=top_n)
        
        return list(word_freq.keys())
    
    def batch_preprocess(self, texts: List[str], **preprocess_kwargs) -> List[str]:
        """
        Preprocess multiple texts.
        
        Args:
            texts: List of texts to preprocess
            **preprocess_kwargs: Arguments to pass to preprocess()
            
        Returns:
            List[str]: List of preprocessed texts
        """
        return [self.preprocess(text, **preprocess_kwargs) for text in texts]


# Example usage
if __name__ == "__main__":
    # Initialize preprocessor with custom cleaner config
    preprocessor = TextPreprocessor(
        use_cleaner=True,
        cleaner_config={
            'remove_urls': True,
            'remove_html': True,
            'remove_extra_whitespace': True,
            'lowercase': True
        }
    )
    
    # Test texts
    test_texts = [
        "This is ABSOLUTELY terrible!!! I can't believe it doesn't work.",
        "Great product! Check it out at https://example.com",
        "I'm very disappointed with the quality. It's not worth the price.",
        "Amazing service! Will definitely buy again. Highly recommended!!!",
    ]
    
    print("Text Preprocessor Test Results:")
    print("=" * 80)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nTest {i}:")
        print(f"Original:    {text}")
        
        # Basic preprocessing
        basic = preprocessor.preprocess(text)
        print(f"Basic:       {basic}")
        
        # With stopword removal
        no_stop = preprocessor.preprocess(text, remove_stopwords=True)
        print(f"No stopwords: {no_stop}")
        
        # Extract keywords
        keywords = preprocessor.extract_keywords(text, top_n=3)
        print(f"Keywords:    {keywords}")
        print("-" * 80)
    
    # Test word frequency
    print("\n\nWord Frequency Analysis:")
    print("=" * 80)
    all_text = ' '.join(test_texts)
    freq = preprocessor.get_word_frequency(all_text, top_n=10)
    for word, count in freq.items():
        print(f"{word:15} {count}")
