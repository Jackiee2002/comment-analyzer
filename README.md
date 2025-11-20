# Comment Analyzer

Automated analysis of user feedback from YouTube and Steam, with a focus on negative sentiment detection.

## Features

- **Negative Sentiment Classifier**: Automatically identify and analyze negative comments
- **Text Preprocessing**: Clean and normalize text with advanced preprocessing utilities
- Sentiment scoring with confidence levels
- Batch processing for large datasets
- Detailed statistics and visualizations
- Export filtered negative comments

## Setup

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Quick Start - Classify Negative Comments

Run the classifier with example data:

```bash
python classify_negative.py
```

Or with your own CSV file:

```bash
python classify_negative.py data/raw/your_comments.csv
```

The script will:
1. Load and classify all comments
2. Filter out only negative comments
3. Show statistics and top negative comments
4. Save results to `results/negative_comments.csv`

### Using in Code

```python
from src.analysis.sentiment_classifier import NegativeSentimentClassifier
from src.preprocessing import TextCleaner, TextPreprocessor
import pandas as pd

# Initialize classifier
classifier = NegativeSentimentClassifier()

# Initialize preprocessor (optional but recommended)
preprocessor = TextPreprocessor(
    use_cleaner=True,
    cleaner_config={
        'remove_urls': True,
        'remove_html': True,
        'lowercase': True
    }
)

# Load and preprocess your comments
df = pd.read_csv('your_comments.csv')
df = preprocessor.preprocess_dataframe(df, text_column='text')

# Get only negative comments
negative_comments = classifier.filter_negative_comments(df)

# Analyze statistics
stats = classifier.analyze_negative_comments(negative_comments)
print(f"Found {stats['total_negative']} negative comments")
```

### Interactive Analysis

Use the Jupyter notebook for detailed analysis and visualizations:

```bash
jupyter notebook notebooks/negative_sentiment_analysis.ipynb
```

## Configuration

Edit `config.yaml` to customize the classifier:

```yaml
classifier:
  model: "distilbert-base-uncased-finetuned-sst-2-english"
  batch_size: 16
  negative_threshold: 0.4  # Adjust sensitivity (lower = more sensitive)
```

## Output

The classifier produces CSV files with these columns:
- Original comment text
- `sentiment_label`: NEGATIVE or POSITIVE
- `negative_score`: Confidence score (0-1) for negative sentiment
- `positive_score`: Confidence score (0-1) for positive sentiment
- `is_negative`: Boolean flag if score exceeds threshold

Negative comments are categorized as:
- **Highly negative**: Score ≥ 0.8
- **Moderately negative**: Score 0.6-0.8
- **Mildly negative**: Score < 0.6

## Preprocessing

Clean and normalize text before analysis:

```python
from src.preprocessing import TextCleaner, TextPreprocessor

# Basic text cleaning
cleaner = TextCleaner(
    remove_urls=True,
    remove_html=True,
    remove_emails=True,
    lowercase=True
)
clean_text = cleaner.clean("Check out https://example.com!")

# Advanced preprocessing
preprocessor = TextPreprocessor()
processed = preprocessor.preprocess(
    "I'm loving this product!!!",
    remove_stopwords=True,
    expand_contractions=True
)

# Process entire DataFrame
df = preprocessor.preprocess_dataframe(
    df, 
    text_column='comment',
    remove_stopwords=True
)
```

### Preprocessing Features

- **Text Cleaning**: Remove URLs, HTML, emails, mentions, hashtags
- **Normalization**: Lowercase, whitespace, character repetitions
- **Tokenization**: Word-level tokenization
- **Stopword Removal**: Built-in English stopwords with custom options
- **Contraction Expansion**: "I'm" → "I am"
- **Emoji Removal**: Strip emoji characters
- **Keyword Extraction**: Extract most frequent meaningful words
- **Batch Processing**: Process DataFrames efficiently