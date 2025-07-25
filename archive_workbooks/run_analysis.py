#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Initial Run
This script runs the analysis from the Jupyter notebook
"""

# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import warnings
import os
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)

# Configure plotting
plt.style.use('default')  # Using default style
plt.rcParams['figure.figsize'] = (12, 6)
plt.rcParams['font.size'] = 10

print("=" * 80)
print("Minneapolis Permits Data Analysis - Initial Run")
print("=" * 80)

# 1. Data Loading and Initial Validation
print("\n1. DATA LOADING AND INITIAL VALIDATION")
print("-" * 60)

# Load the permits data
permits_file = 'source/CCS_Permits.csv'
use_cases_file = 'Mpls Use Cases - Minneapolis (1).csv'

try:
    permits_df = pd.read_csv(permits_file, low_memory=False)
    print(f"✓ Successfully loaded permits data from {permits_file}")
    print(f"  Total records: {len(permits_df):,}")
    print(f"  Total columns: {len(permits_df.columns)}")
except Exception as e:
    print(f"✗ Error loading permits data: {e}")
    exit(1)

try:
    use_cases_df = pd.read_csv(use_cases_file)
    print(f"\n✓ Successfully loaded use cases from {use_cases_file}")
    print(f"  Total use cases: {len(use_cases_df):,}")
except Exception as e:
    print(f"✗ Error loading use cases: {e}")
    exit(1)

# Display column information
print("\nPermits Dataset Columns:")
print("=" * 60)
for i, col in enumerate(permits_df.columns, 1):
    print(f"{i:2d}. {col}")

# Data quality report
print("\n\nDATA QUALITY REPORT - CCS_Permits.csv")
print("=" * 60)

# Check for missing values
missing_summary = pd.DataFrame({
    'Column': permits_df.columns,
    'Missing_Count': permits_df.isnull().sum(),
    'Missing_Percentage': (permits_df.isnull().sum() / len(permits_df) * 100).round(2)
})

missing_summary = missing_summary[missing_summary['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
print("\nColumns with missing data:")
print(missing_summary.to_string())

# 2. Date Processing and Validation
print("\n\n2. DATE PROCESSING AND VALIDATION")
print("-" * 60)

# Convert date columns with validation
date_columns = ['issueDate', 'completeDate']

for col in date_columns:
    print(f"\nProcessing {col}:")
    
    # Count non-null values before conversion
    non_null_before = permits_df[col].notna().sum()
    print(f"  Non-null values: {non_null_before:,} of {len(permits_df):,} ({non_null_before/len(permits_df)*100:.2f}%)")
    
    # Convert to datetime
    permits_df[col] = pd.to_datetime(permits_df[col], errors='coerce')
    
    # Count successful conversions
    non_null_after = permits_df[col].notna().sum()
    print(f"  Successfully parsed: {non_null_after:,}")
    print(f"  Failed to parse: {non_null_before - non_null_after:,}")
    
    if non_null_after > 0:
        print(f"  Date range: {permits_df[col].min()} to {permits_df[col].max()}")

# Extract year and validate date ranges
permits_df['issueYear'] = permits_df['issueDate'].dt.year
permits_df['completeYear'] = permits_df['completeDate'].dt.year

# Check for future dates or invalid dates
today = pd.Timestamp.now(tz='UTC')
future_issue = permits_df[permits_df['issueDate'] > today]
future_complete = permits_df[permits_df['completeDate'] > today]

print(f"\nData validation results:")
print(f"  Permits with future issue dates: {len(future_issue):,}")
print(f"  Permits with future completion dates: {len(future_complete):,}")

# Check for completion before issue
invalid_timeline = permits_df[
    (permits_df['completeDate'].notna()) & 
    (permits_df['issueDate'].notna()) & 
    (permits_df['completeDate'] < permits_df['issueDate'])
]
print(f"  Permits completed before issued: {len(invalid_timeline):,}")

# 3. Use Cases Hierarchy Analysis
print("\n\n3. USE CASES HIERARCHY ANALYSIS")
print("-" * 60)

# Count unique categories and subcategories
categories = use_cases_df['Category'].dropna().unique()
print(f"\nTotal Categories: {len(categories)}")
print("Categories:", list(categories))

# Display hierarchy
for category in sorted(categories):
    cat_data = use_cases_df[use_cases_df['Category'] == category]
    subcats = cat_data['Sub-Category'].dropna().unique()
    
    print(f"\n{category}:")
    for subcat in sorted(subcats):
        subcat_data = cat_data[cat_data['Sub-Category'] == subcat]
        use_case_count = len(subcat_data)
        print(f"  ├── {subcat} ({use_case_count} use cases)")

# 4. Permit Type Mapping
print("\n\n4. PERMIT TYPE MAPPING")
print("-" * 60)

permit_type_counts = permits_df['permitType'].value_counts(dropna=False)
print(f"\nUnique permit types: {len(permit_type_counts)}")
print("\nTop 20 permit types by count:")
print(permit_type_counts.head(20).to_string())

# Check for null values
null_permit_types = permits_df['permitType'].isnull().sum()
print(f"\nRecords with null permitType: {null_permit_types:,} ({null_permit_types/len(permits_df)*100:.2f}%)")

# Summary statistics
print("\n\n5. SUMMARY STATISTICS")
print("-" * 60)
print(f"\nTotal permits analyzed: {len(permits_df):,}")
print(f"Date range: {permits_df['issueDate'].min()} to {permits_df['issueDate'].max()}")
print(f"Unique applicants: {permits_df['applicantName'].nunique():,}")
print(f"Unique neighborhoods: {permits_df['Neighborhoods_Desc'].nunique()}")
print(f"Total project value: ${permits_df['value'].sum():,.2f}")
print(f"Total fees collected: ${permits_df['totalFees'].sum():,.2f}")

# Save initial findings
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

# Export summary statistics
summary_stats = {
    'total_records': len(permits_df),
    'date_range': {
        'start': str(permits_df['issueDate'].min()),
        'end': str(permits_df['issueDate'].max())
    },
    'unique_applicants': int(permits_df['applicantName'].nunique()),
    'unique_neighborhoods': int(permits_df['Neighborhoods_Desc'].nunique()),
    'total_value': float(permits_df['value'].sum()),
    'total_fees': float(permits_df['totalFees'].sum()),
    'data_quality': {
        'missing_issue_date': int(permits_df['issueDate'].isna().sum()),
        'missing_complete_date': int(permits_df['completeDate'].isna().sum()),
        'future_dates': len(future_issue) + len(future_complete),
        'invalid_timelines': len(invalid_timeline)
    }
}

with open(f'{output_dir}/initial_summary.json', 'w') as f:
    json.dump(summary_stats, f, indent=2)

print(f"\n✓ Initial analysis complete. Summary saved to {output_dir}/initial_summary.json")
print("\nReady for enhancement iterations...")