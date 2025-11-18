#!/usr/bin/env python
"""
Main script to classify and extract negative comments from datasets.

Usage:
    python classify_negative.py [input_file.csv]
    
If no input file is provided, it will run with example data.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from analysis.sentiment_classifier import main

if __name__ == "__main__":
    main()
