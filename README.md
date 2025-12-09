# Comment Analyzer

Automated analysis of user feedback from YouTube and Steam, with a focus on negative sentiment detection.

## Features

- 🤖 **Fully Automated Pipeline**: Scrape → Preprocess → Classify in one command
- **Negative Sentiment Classifier**: Automatically identify and analyze negative comments
- **Multi-Platform Scraping**: YouTube comments and Steam reviews
- **Text Preprocessing**: Clean and normalize text with advanced preprocessing utilities
- Sentiment scoring with confidence levels
- Batch processing for large datasets
- Detailed statistics and visualizations
- Export filtered negative comments

## Quick Start (3 Steps)

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Setup

```bash
python setup.py
```

This will check your configuration and create necessary directories.

### 3. Configure (if needed)

**Get YouTube API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new project (or select existing)
3. Enable YouTube Data API v3
4. Create credentials (API Key)
5. Add to `.env` file:
   ```
   YOUTUBE_API_KEY=your_actual_api_key_here
   ```

**Configure Sources** in `config.yaml`:

```yaml
youtube:
  videos:
    - "dQw4w9WgXcQ"  # Add your YouTube video IDs here
  max_comments: 1000

steam:
  games:
    - "730"  # Add Steam App IDs (e.g., 730 = CS2)
  max_reviews: 1000
```

**Find YouTube Video ID:** From URL `https://youtube.com/watch?v=VIDEO_ID`  
**Find Steam App ID:** From URL `https://store.steampowered.com/app/APP_ID/`

### 4. Test the Pipeline (Optional)

Test with sample data before using real API keys:

```bash
python test_automation.py
```

This runs the full pipeline with mock data to verify everything works.

## Usage

### 🚀 Fully Automated Analysis (Recommended)

**Option 1: Using convenience launcher (easiest)**

Windows:
```bash
run_analysis.bat
```

Linux/Mac:
```bash
chmod +x run_analysis.sh
./run_analysis.sh
```

**Option 2: Direct Python command**

```bash
python run_automated_analysis.py
```

**What it does:**
1. ✅ Scrapes comments from configured YouTube videos
2. ✅ Scrapes reviews from configured Steam games
3. ✅ Preprocesses all text data (removes URLs, HTML, etc.)
4. ✅ Classifies sentiment using AI
5. ✅ Filters negative comments
6. ✅ Shows top negative comments with scores
7. ✅ Saves all results with timestamps

**Output files** (in `results/` folder):
- `all_comments_classified_YYYYMMDD_HHMMSS.csv` - All comments with sentiment scores
- `negative_comments_YYYYMMDD_HHMMSS.csv` - Only negative comments
- `highly_negative_comments_YYYYMMDD_HHMMSS.csv` - Highly negative (score ≥ 0.8)

### Manual Classification (Existing Data)

If you already have comments in a CSV file:

```bash
python classify_negative.py data/raw/your_comments.csv
```

The script will:
1. Load and classify all comments
2. Filter out only negative comments
3. Show statistics and top negative comments
4. Save results to `results/negative_comments.csv`

## 📚 Documentation

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Quick command reference card
- **[AUTOMATION_GUIDE.md](AUTOMATION_GUIDE.md)** - Detailed workflow and troubleshooting
- **[notebooks/](notebooks/)** - Interactive Jupyter notebooks for analysis

## Advanced Usage

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