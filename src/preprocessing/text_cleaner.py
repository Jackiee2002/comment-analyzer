"""
Text cleaning utilities for comment preprocessing.
Handles HTML, URLs, emojis, special characters, and more.
"""
import re
import html
from typing import Optional


class TextCleaner:
    """Clean and normalize text data from comments."""
    
    def __init__(self, 
                 remove_urls: bool = True,
                 remove_emails: bool = True,
                 remove_html: bool = True,
                 remove_mentions: bool = False,
                 remove_hashtags: bool = False,
                 remove_extra_whitespace: bool = True,
                 lowercase: bool = False):
        """
        Initialize text cleaner with configuration.
        
        Args:
            remove_urls: Remove URLs from text
            remove_emails: Remove email addresses
            remove_html: Remove HTML tags and entities
            remove_mentions: Remove @mentions (useful for social media)
            remove_hashtags: Remove #hashtags
            remove_extra_whitespace: Normalize whitespace
            lowercase: Convert text to lowercase
        """
        self.remove_urls = remove_urls
        self.remove_emails = remove_emails
        self.remove_html = remove_html
        self.remove_mentions = remove_mentions
        self.remove_hashtags = remove_hashtags
        self.remove_extra_whitespace = remove_extra_whitespace
        self.lowercase = lowercase
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for text cleaning."""
        # URL pattern - matches http(s) URLs
        self.url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        
        # Email pattern
        self.email_pattern = re.compile(
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        )
        
        # HTML tags
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        
        # Mentions (@username)
        self.mention_pattern = re.compile(r'@\w+')
        
        # Hashtags (#hashtag)
        self.hashtag_pattern = re.compile(r'#\w+')
        
        # Multiple whitespace
        self.whitespace_pattern = re.compile(r'\s+')
        
        # Special characters (for optional removal)
        self.special_chars_pattern = re.compile(r'[^\w\s.,!?;:\'\"-]')
    
    def clean(self, text: str) -> str:
        """
        Clean text according to configuration.
        
        Args:
            text: Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Decode HTML entities first
        if self.remove_html:
            text = html.unescape(text)
            text = self.html_tag_pattern.sub(' ', text)
        
        # Remove URLs
        if self.remove_urls:
            text = self.url_pattern.sub(' ', text)
        
        # Remove emails
        if self.remove_emails:
            text = self.email_pattern.sub(' ', text)
        
        # Remove mentions
        if self.remove_mentions:
            text = self.mention_pattern.sub(' ', text)
        
        # Remove hashtags
        if self.remove_hashtags:
            text = self.hashtag_pattern.sub(' ', text)
        
        # Normalize whitespace
        if self.remove_extra_whitespace:
            text = self.whitespace_pattern.sub(' ', text)
        
        # Convert to lowercase
        if self.lowercase:
            text = text.lower()
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def remove_special_characters(self, text: str, keep_punctuation: bool = True) -> str:
        """
        Remove special characters from text.
        
        Args:
            text: Text to process
            keep_punctuation: If True, keeps common punctuation (.,!?;:'\"-)
            
        Returns:
            str: Text with special characters removed
        """
        if not keep_punctuation:
            text = re.sub(r'[^\w\s]', ' ', text)
        else:
            text = self.special_chars_pattern.sub(' ', text)
        
        return self.whitespace_pattern.sub(' ', text).strip()
    
    def remove_emojis(self, text: str) -> str:
        """
        Remove emojis from text.
        
        Args:
            text: Text containing emojis
            
        Returns:
            str: Text without emojis
        """
        # Emoji pattern - covers most emoji ranges
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642"
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            "]+",
            flags=re.UNICODE
        )
        return emoji_pattern.sub(r' ', text)
    
    def remove_numbers(self, text: str, replace_with: str = ' ') -> str:
        """
        Remove numbers from text.
        
        Args:
            text: Text containing numbers
            replace_with: String to replace numbers with
            
        Returns:
            str: Text without numbers
        """
        return re.sub(r'\d+', replace_with, text)
    
    def expand_contractions(self, text: str) -> str:
        """
        Expand common English contractions.
        
        Args:
            text: Text with contractions
            
        Returns:
            str: Text with expanded contractions
        """
        contractions_dict = {
            "ain't": "am not",
            "aren't": "are not",
            "can't": "cannot",
            "can't've": "cannot have",
            "could've": "could have",
            "couldn't": "could not",
            "didn't": "did not",
            "doesn't": "does not",
            "don't": "do not",
            "hadn't": "had not",
            "hasn't": "has not",
            "haven't": "have not",
            "he'd": "he would",
            "he'll": "he will",
            "he's": "he is",
            "i'd": "i would",
            "i'll": "i will",
            "i'm": "i am",
            "i've": "i have",
            "isn't": "is not",
            "it'd": "it would",
            "it'll": "it will",
            "it's": "it is",
            "let's": "let us",
            "might've": "might have",
            "must've": "must have",
            "shan't": "shall not",
            "she'd": "she would",
            "she'll": "she will",
            "she's": "she is",
            "should've": "should have",
            "shouldn't": "should not",
            "that'd": "that would",
            "that's": "that is",
            "there'd": "there would",
            "there's": "there is",
            "they'd": "they would",
            "they'll": "they will",
            "they're": "they are",
            "they've": "they have",
            "wasn't": "was not",
            "we'd": "we would",
            "we'll": "we will",
            "we're": "we are",
            "we've": "we have",
            "weren't": "were not",
            "what'll": "what will",
            "what're": "what are",
            "what's": "what is",
            "what've": "what have",
            "where'd": "where did",
            "where's": "where is",
            "who'll": "who will",
            "who's": "who is",
            "won't": "will not",
            "wouldn't": "would not",
            "you'd": "you would",
            "you'll": "you will",
            "you're": "you are",
            "you've": "you have"
        }
        
        # Create pattern from contractions
        pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in contractions_dict.keys()) + r')\b', re.IGNORECASE)
        
        def replace_match(match):
            return contractions_dict[match.group(0).lower()]
        
        return pattern.sub(replace_match, text)
    
    def normalize_repetitions(self, text: str, max_repetitions: int = 2) -> str:
        """
        Normalize character repetitions (e.g., 'soooo' -> 'soo').
        
        Args:
            text: Text with character repetitions
            max_repetitions: Maximum allowed repetitions
            
        Returns:
            str: Text with normalized repetitions
        """
        pattern = re.compile(r'(.)\1{' + str(max_repetitions) + ',}')
        return pattern.sub(r'\1' * max_repetitions, text)


# Example usage and testing
if __name__ == "__main__":
    # Test the cleaner
    cleaner = TextCleaner(
        remove_urls=True,
        remove_html=True,
        remove_extra_whitespace=True,
        lowercase=False
    )
    
    test_texts = [
        "Check out this link: https://example.com/page",
        "This is <b>HTML</b> &amp; entities",
        "Email me at test@example.com for more info",
        "Sooooo goooood!!! Love it!!!",
        "@user #trending this is amazing",
        "I'm can't believe it's not working 😂😂😂"
    ]
    
    print("Text Cleaner Test Results:")
    print("=" * 70)
    for text in test_texts:
        cleaned = cleaner.clean(text)
        print(f"Original: {text}")
        print(f"Cleaned:  {cleaned}")
        print("-" * 70)
