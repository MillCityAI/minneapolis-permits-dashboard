#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 3: Comments Text Mining
"""

import pandas as pd
import numpy as np
import re
from collections import Counter
import json
import warnings
import os
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)
pd.set_option('display.max_colwidth', 100)

print("=" * 80)
print("Minneapolis Permits Analysis - Iteration 3: Comments Text Mining")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['completeDate'] = pd.to_datetime(permits_df['completeDate'], errors='coerce')
permits_df['processing_days'] = (permits_df['completeDate'] - permits_df['issueDate']).dt.days

print(f"\nData loaded: {len(permits_df):,} permits")
print(f"Records with comments: {permits_df['comments'].notna().sum():,} ({permits_df['comments'].notna().sum()/len(permits_df)*100:.1f}%)")

# 1. COMMENTS OVERVIEW
print("\n\n1. COMMENTS OVERVIEW")
print("-" * 60)

# Basic stats
comments_df = permits_df[permits_df['comments'].notna()].copy()
comments_df['comment_length'] = comments_df['comments'].astype(str).str.len()
comments_df['word_count'] = comments_df['comments'].astype(str).str.split().str.len()

print(f"\nComment Statistics:")
print(f"  Average length: {comments_df['comment_length'].mean():.1f} characters")
print(f"  Average words: {comments_df['word_count'].mean():.1f} words")
print(f"  Shortest comment: {comments_df['comment_length'].min()} chars")
print(f"  Longest comment: {comments_df['comment_length'].max()} chars")

# Sample comments
print("\n\nSample Comments:")
for i, comment in enumerate(comments_df['comments'].head(5), 1):
    print(f"{i}. {comment[:150]}{'...' if len(str(comment)) > 150 else ''}")

# 2. KEYWORD EXTRACTION
print("\n\n2. KEYWORD EXTRACTION")
print("-" * 60)

# Clean and tokenize comments
def clean_text(text):
    """Clean and normalize text for analysis"""
    if pd.isna(text):
        return ""
    text = str(text).lower()
    # Remove special characters but keep spaces and basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s\-/]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Extract all words
all_comments = ' '.join(comments_df['comments'].apply(clean_text).tolist())
words = all_comments.split()

# Filter out common stop words and short words
stop_words = {'the', 'and', 'to', 'of', 'a', 'in', 'for', 'on', 'with', 'as', 'at', 'by', 'an', 
              'be', 'is', 'it', 'or', 'no', 'per', 'all', 'new', 'from', 'will', 'are', 'not'}
meaningful_words = [w for w in words if len(w) > 2 and w not in stop_words]

# Count word frequencies
word_freq = Counter(meaningful_words)

print("\nTop 50 Most Common Keywords:")
for i, (word, count) in enumerate(word_freq.most_common(50), 1):
    pct = count / len(meaningful_words) * 100
    print(f"{i:>3}. {word:>20}: {count:>7,} ({pct:>4.2f}%)")

# 3. PROJECT SCOPE INDICATORS
print("\n\n3. PROJECT SCOPE INDICATORS")
print("-" * 60)

# Define scope indicators
major_indicators = [
    'complete', 'full', 'entire', 'whole', 'major', 'extensive', 'comprehensive',
    'structural', 'foundation', 'addition', 'new construction', 'demolition'
]

minor_indicators = [
    'repair', 'replace', 'fix', 'patch', 'minor', 'small', 'simple',
    'maintenance', 'service', 'adjust', 'clean'
]

# Check for indicators
def check_scope(comment):
    if pd.isna(comment):
        return 'Unknown'
    comment_lower = str(comment).lower()
    
    major_count = sum(1 for ind in major_indicators if ind in comment_lower)
    minor_count = sum(1 for ind in minor_indicators if ind in comment_lower)
    
    if major_count > minor_count:
        return 'Major'
    elif minor_count > major_count:
        return 'Minor'
    elif major_count > 0 and minor_count > 0:
        return 'Mixed'
    else:
        return 'Unspecified'

comments_df['scope'] = comments_df['comments'].apply(check_scope)

print("\nProject Scope Distribution:")
scope_counts = comments_df['scope'].value_counts()
for scope, count in scope_counts.items():
    pct = count / len(comments_df) * 100
    print(f"  {scope:>12}: {count:>7,} ({pct:>5.1f}%)")

# Average processing time by scope
print("\n\nAverage Processing Time by Scope:")
scope_processing = comments_df[comments_df['processing_days'] >= 0].groupby('scope')['processing_days'].agg(['mean', 'median', 'count'])
for scope, row in scope_processing.iterrows():
    if row['count'] > 10:
        print(f"  {scope:>12}: {row['mean']:>6.1f} days (median: {row['median']:>5.0f}, n={row['count']:,})")

# 4. EMERGENCY VS PLANNED WORK
print("\n\n4. EMERGENCY VS PLANNED WORK")
print("-" * 60)

# Emergency indicators
emergency_keywords = [
    'emergency', 'urgent', 'immediate', 'asap', 'leak', 'burst', 'flood',
    'damage', 'broken', 'failed', 'hazard', 'unsafe', 'danger'
]

def check_emergency(comment):
    if pd.isna(comment):
        return 'Unknown'
    comment_lower = str(comment).lower()
    return 'Emergency' if any(keyword in comment_lower for keyword in emergency_keywords) else 'Planned'

comments_df['urgency'] = comments_df['comments'].apply(check_emergency)

print("\nWork Urgency Distribution:")
urgency_counts = comments_df['urgency'].value_counts()
for urgency, count in urgency_counts.items():
    pct = count / len(comments_df) * 100
    print(f"  {urgency:>10}: {count:>7,} ({pct:>5.1f}%)")

# Processing time by urgency
print("\n\nProcessing Time by Urgency:")
urgency_processing = comments_df[comments_df['processing_days'] >= 0].groupby('urgency')['processing_days'].agg(['mean', 'median', 'count'])
for urgency, row in urgency_processing.iterrows():
    print(f"  {urgency:>10}: {row['mean']:>6.1f} days (median: {row['median']:>5.0f}, n={row['count']:,})")

# 5. MULTI-TRADE PROJECT IDENTIFICATION
print("\n\n5. MULTI-TRADE PROJECT IDENTIFICATION")
print("-" * 60)

# Trade indicators
trades = {
    'Plumbing': ['plumbing', 'pipe', 'water', 'drain', 'sewer', 'toilet', 'sink', 'shower', 'faucet'],
    'Electrical': ['electrical', 'electric', 'wire', 'circuit', 'panel', 'outlet', 'switch', 'lighting'],
    'HVAC': ['hvac', 'heating', 'cooling', 'furnace', 'air conditioning', 'ac', 'ductwork', 'ventilation'],
    'Structural': ['structural', 'foundation', 'beam', 'wall', 'framing', 'load bearing'],
    'Roofing': ['roof', 'shingle', 'gutter', 'flashing', 'soffit', 'fascia'],
    'Windows/Doors': ['window', 'door', 'glass', 'frame', 'entry'],
    'Insulation': ['insulation', 'insulate', 'vapor barrier', 'weatherization'],
    'Flooring': ['floor', 'carpet', 'tile', 'hardwood', 'laminate'],
    'Kitchen/Bath': ['kitchen', 'bathroom', 'bath', 'cabinet', 'countertop']
}

def identify_trades(comment):
    if pd.isna(comment):
        return []
    comment_lower = str(comment).lower()
    identified_trades = []
    
    for trade, keywords in trades.items():
        if any(keyword in comment_lower for keyword in keywords):
            identified_trades.append(trade)
    
    return identified_trades

comments_df['trades'] = comments_df['comments'].apply(identify_trades)
comments_df['trade_count'] = comments_df['trades'].str.len()

print("\nProjects by Number of Trades:")
trade_count_dist = comments_df['trade_count'].value_counts().sort_index()
for count, freq in trade_count_dist.items():
    pct = freq / len(comments_df) * 100
    print(f"  {count} trade(s): {freq:>7,} ({pct:>5.1f}%)")

# Most common trade combinations
print("\n\nMost Common Trade Combinations (Multi-trade only):")
multi_trade = comments_df[comments_df['trade_count'] > 1].copy()
trade_combos = Counter([tuple(sorted(trades)) for trades in multi_trade['trades']])

for combo, count in trade_combos.most_common(15):
    pct = count / len(multi_trade) * 100
    combo_str = ' + '.join(combo)
    print(f"  {combo_str:>50}: {count:>5,} ({pct:>5.1f}%)")

# 6. SPECIFIC WORK TYPE EXTRACTION
print("\n\n6. SPECIFIC WORK TYPE EXTRACTION")
print("-" * 60)

# Extract specific work patterns
work_patterns = {
    'Water Heater': r'water\s*heater|hwt|hot\s*water',
    'Furnace': r'furnace|boiler',
    'AC/Cooling': r'air\s*condition|a/c|ac\s|cooling',
    'Bathroom Remodel': r'bathroom\s*remodel|bath\s*remodel',
    'Kitchen Remodel': r'kitchen\s*remodel',
    'Roof Replacement': r'roof\s*replac|reroof|new\s*roof',
    'Window Replacement': r'window\s*replac|new\s*window',
    'Siding': r'siding|vinyl|hardie',
    'Deck/Patio': r'deck|patio',
    'Garage': r'garage|carport'
}

print("\nSpecific Work Types Found in Comments:")
for work_type, pattern in work_patterns.items():
    matches = comments_df['comments'].astype(str).str.contains(pattern, case=False, regex=True).sum()
    pct = matches / len(comments_df) * 100
    print(f"  {work_type:>20}: {matches:>6,} ({pct:>5.1f}%)")

# 7. PERMIT COMPLEXITY SCORING
print("\n\n7. PERMIT COMPLEXITY SCORING")
print("-" * 60)

# Create complexity score based on multiple factors
def calculate_complexity(row):
    score = 0
    
    # Length of comment
    if pd.notna(row['comments']):
        score += min(row['word_count'] / 20, 3)  # Up to 3 points for length
    
    # Scope
    if row.get('scope') == 'Major':
        score += 2
    elif row.get('scope') == 'Mixed':
        score += 1
    
    # Number of trades
    score += min(row.get('trade_count', 0), 3)  # Up to 3 points for multi-trade
    
    # Value (if available)
    if pd.notna(row.get('value')) and row['value'] > 0:
        if row['value'] > 100000:
            score += 2
        elif row['value'] > 50000:
            score += 1
    
    return score

comments_df['complexity_score'] = comments_df.apply(calculate_complexity, axis=1)

print("\nPermit Complexity Distribution:")
complexity_bins = [0, 2, 4, 6, 8, 10]
complexity_labels = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
comments_df['complexity_category'] = pd.cut(comments_df['complexity_score'], bins=complexity_bins, labels=complexity_labels, include_lowest=True)

complexity_dist = comments_df['complexity_category'].value_counts()
for category, count in complexity_dist.items():
    pct = count / len(comments_df) * 100
    print(f"  {category:>10}: {count:>7,} ({pct:>5.1f}%)")

# Export enhanced metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

# Prepare data for export
text_mining_metrics = {
    'overview': {
        'total_with_comments': int(len(comments_df)),
        'avg_comment_length': float(comments_df['comment_length'].mean()),
        'avg_word_count': float(comments_df['word_count'].mean())
    },
    'top_keywords': dict(word_freq.most_common(100)),
    'scope_distribution': scope_counts.to_dict(),
    'urgency_distribution': urgency_counts.to_dict(),
    'trade_analysis': {
        'trade_count_distribution': trade_count_dist.to_dict(),
        'top_trade_combinations': [{'trades': ' + '.join(combo), 'count': count} 
                                  for combo, count in trade_combos.most_common(20)]
    },
    'specific_work_types': {work_type: int(comments_df['comments'].astype(str).str.contains(pattern, case=False, regex=True).sum()) 
                           for work_type, pattern in work_patterns.items()},
    'complexity_distribution': complexity_dist.to_dict()
}

# Clean for JSON
def clean_for_json(obj):
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(v) for v in obj]
    elif pd.isna(obj):
        return None
    elif isinstance(obj, (np.integer, np.int64)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64)):
        return float(obj)
    else:
        return obj

text_mining_metrics = clean_for_json(text_mining_metrics)

with open(f'{output_dir}/text_mining_metrics.json', 'w') as f:
    json.dump(text_mining_metrics, f, indent=2)

print(f"\n✓ Iteration 3 complete. Text mining metrics saved to {output_dir}/text_mining_metrics.json")

# Key insights summary
print("\n\nKEY TEXT MINING INSIGHTS:")
print("=" * 60)
print(f"1. Most common keywords: {', '.join([w[0] for w in word_freq.most_common(5)])}")
print(f"2. Major scope projects: {scope_counts.get('Major', 0):,} ({scope_counts.get('Major', 0)/len(comments_df)*100:.1f}%)")
print(f"3. Emergency work: {urgency_counts.get('Emergency', 0):,} ({urgency_counts.get('Emergency', 0)/len(comments_df)*100:.1f}%)")
print(f"4. Multi-trade projects: {len(multi_trade):,} ({len(multi_trade)/len(comments_df)*100:.1f}%)")
print("5. Comments provide rich detail about project specifics and complexity")