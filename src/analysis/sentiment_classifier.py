"""
Sentiment Classifier focused on identifying negative comments.
"""
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
from tqdm import tqdm
import yaml
from pathlib import Path


class NegativeSentimentClassifier:
    """Classifier specifically designed to identify and analyze negative comments."""
    
    def __init__(self, config_path="config.yaml"):
        """Initialize the classifier with configuration."""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.classifier_config = config['classifier']
        self.model_name = self.classifier_config['model']
        self.batch_size = self.classifier_config['batch_size']
        self.negative_threshold = self.classifier_config['negative_threshold']
        
        print(f"Loading model: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name)
        
        # Use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"Using device: {self.device}")
    
    def classify_comment(self, text):
        """
        Classify a single comment and return sentiment score.
        
        Args:
            text: Comment text to classify
            
        Returns:
            dict: Contains label ('NEGATIVE' or 'POSITIVE'), score, and is_negative flag
        """
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
                               max_length=512, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        
        # Get negative sentiment score (index 0 is negative for SST-2 model)
        negative_score = predictions[0][0].item()
        positive_score = predictions[0][1].item()
        
        label = "NEGATIVE" if negative_score > positive_score else "POSITIVE"
        is_negative = negative_score >= self.negative_threshold
        
        return {
            'label': label,
            'negative_score': negative_score,
            'positive_score': positive_score,
            'is_negative': is_negative
        }
    
    def classify_batch(self, texts):
        """
        Classify multiple comments in batch for efficiency.
        
        Args:
            texts: List of comment texts
            
        Returns:
            list: List of classification results
        """
        results = []
        
        for i in tqdm(range(0, len(texts), self.batch_size), desc="Classifying comments"):
            batch = texts[i:i + self.batch_size]
            
            inputs = self.tokenizer(batch, return_tensors="pt", truncation=True,
                                   max_length=512, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            
            for pred in predictions:
                negative_score = pred[0].item()
                positive_score = pred[1].item()
                
                label = "NEGATIVE" if negative_score > positive_score else "POSITIVE"
                is_negative = negative_score >= self.negative_threshold
                
                results.append({
                    'label': label,
                    'negative_score': negative_score,
                    'positive_score': positive_score,
                    'is_negative': is_negative
                })
        
        return results
    
    def filter_negative_comments(self, comments_df):
        """
        Filter and classify comments, returning only negative ones.
        
        Args:
            comments_df: DataFrame with 'text' or 'comment' column
            
        Returns:
            DataFrame: Only negative comments with sentiment scores
        """
        # Identify the text column
        text_col = 'text' if 'text' in comments_df.columns else 'comment'
        
        if text_col not in comments_df.columns:
            raise ValueError("DataFrame must have 'text' or 'comment' column")
        
        # Get all texts
        texts = comments_df[text_col].fillna("").tolist()
        
        # Classify
        print(f"Classifying {len(texts)} comments...")
        results = self.classify_batch(texts)
        
        # Add results to dataframe
        comments_df['sentiment_label'] = [r['label'] for r in results]
        comments_df['negative_score'] = [r['negative_score'] for r in results]
        comments_df['positive_score'] = [r['positive_score'] for r in results]
        comments_df['is_negative'] = [r['is_negative'] for r in results]
        
        # Filter only negative comments
        negative_df = comments_df[comments_df['is_negative']].copy()
        
        # Sort by negative score (most negative first)
        negative_df = negative_df.sort_values('negative_score', ascending=False)
        
        print(f"\nFound {len(negative_df)} negative comments out of {len(comments_df)} total")
        print(f"Negative rate: {len(negative_df)/len(comments_df)*100:.1f}%")
        
        return negative_df
    
    def analyze_negative_comments(self, negative_df):
        """
        Provide statistics and insights about negative comments.
        
        Args:
            negative_df: DataFrame with negative comments
            
        Returns:
            dict: Statistics about negative comments
        """
        stats = {
            'total_negative': len(negative_df),
            'avg_negative_score': negative_df['negative_score'].mean(),
            'median_negative_score': negative_df['negative_score'].median(),
            'highly_negative_count': len(negative_df[negative_df['negative_score'] >= 0.8]),
            'moderately_negative_count': len(negative_df[
                (negative_df['negative_score'] >= 0.6) & 
                (negative_df['negative_score'] < 0.8)
            ]),
            'mildly_negative_count': len(negative_df[negative_df['negative_score'] < 0.6])
        }
        
        return stats


def main():
    """Example usage of the negative sentiment classifier."""
    import sys
    
    # Initialize classifier
    classifier = NegativeSentimentClassifier()
    
    # Example: Load comments from CSV file
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        print(f"\nLoading comments from: {input_file}")
        df = pd.read_csv(input_file)
    else:
        # Create example data if no file provided
        print("\nNo input file provided. Using example comments...")
        df = pd.DataFrame({
            'text': [
                "This is absolutely terrible and I hate it!",
                "Great product, love it!",
                "Worst experience ever, complete waste of money.",
                "Amazing quality and fast shipping!",
                "Disappointed with the quality, not worth the price.",
                "Best purchase I've made this year!",
                "Buggy and crashes constantly. Very frustrating.",
                "Works perfectly, exactly what I needed.",
            ]
        })
    
    # Filter and get negative comments
    negative_comments = classifier.filter_negative_comments(df)
    
    # Get statistics
    stats = classifier.analyze_negative_comments(negative_comments)
    
    print("\n" + "="*60)
    print("NEGATIVE COMMENT ANALYSIS")
    print("="*60)
    print(f"Total negative comments: {stats['total_negative']}")
    print(f"Average negative score: {stats['avg_negative_score']:.3f}")
    print(f"Median negative score: {stats['median_negative_score']:.3f}")
    print(f"\nBreakdown:")
    print(f"  Highly negative (≥0.8): {stats['highly_negative_count']}")
    print(f"  Moderately negative (0.6-0.8): {stats['moderately_negative_count']}")
    print(f"  Mildly negative (<0.6): {stats['mildly_negative_count']}")
    
    # Save negative comments
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "negative_comments.csv"
    negative_comments.to_csv(output_file, index=False)
    print(f"\nNegative comments saved to: {output_file}")
    
    # Show top 5 most negative comments
    print("\n" + "="*60)
    print("TOP 5 MOST NEGATIVE COMMENTS")
    print("="*60)
    text_col = 'text' if 'text' in negative_comments.columns else 'comment'
    for idx, row in negative_comments.head(5).iterrows():
        print(f"\nScore: {row['negative_score']:.3f}")
        print(f"Text: {row[text_col][:200]}...")


if __name__ == "__main__":
    main()
