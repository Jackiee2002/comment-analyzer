# Comment Analyzer

Automated analysis of user feedback from YouTube and Steam, with a focus on negative sentiment detection.

## Features

- **Negative Sentiment Classifier**: Automatically identify and analyze negative comments
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
import pandas as pd

# Initialize classifier
classifier = NegativeSentimentClassifier()

# Load your comments
df = pd.read_csv('your_comments.csv')

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