#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 2: Work Type and Occupancy Deep Dive
"""

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

print("=" * 80)
print("Minneapolis Permits Analysis - Iteration 2: Work Type & Occupancy Deep Dive")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)
use_cases_df = pd.read_csv('Mpls Use Cases - Minneapolis (1).csv')

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['completeDate'] = pd.to_datetime(permits_df['completeDate'], errors='coerce')

# Extract year for temporal analysis
permits_df['issueYear'] = permits_df['issueDate'].dt.year

# Calculate processing time
permits_df['processing_days'] = (permits_df['completeDate'] - permits_df['issueDate']).dt.days
permits_df.loc[permits_df['processing_days'] < 0, 'processing_days'] = np.nan

print(f"\nData loaded: {len(permits_df):,} permits")
print(f"Date range: {permits_df['issueDate'].min()} to {permits_df['issueDate'].max()}")

# 1. WORK TYPE ANALYSIS
print("\n\n1. WORK TYPE ANALYSIS")
print("-" * 60)

# Count unique work types
work_type_counts = permits_df['workType'].value_counts(dropna=False)
print(f"\nUnique work types: {len(work_type_counts) - (1 if pd.isna(work_type_counts.index).any() else 0)}")
print(f"Records with missing work type: {work_type_counts.get(np.nan, 0):,} ({work_type_counts.get(np.nan, 0)/len(permits_df)*100:.2f}%)")

print("\nTop 20 Work Types by Count:")
for i, (work_type, count) in enumerate(work_type_counts.head(20).items(), 1):
    pct = count / len(permits_df) * 100
    if pd.isna(work_type):
        print(f"{i:>3}. {'[Missing]':>20}: {count:>7,} ({pct:>5.1f}%)")
    else:
        print(f"{i:>3}. {work_type:>20}: {count:>7,} ({pct:>5.1f}%)")

# Work type trends over time
print("\n\nWork Type Trends (Top 10):")
top_work_types = work_type_counts.dropna().head(10).index
for work_type in top_work_types:
    wt_df = permits_df[permits_df['workType'] == work_type]
    annual_counts = wt_df['issueYear'].value_counts().sort_index()
    if len(annual_counts) > 1:
        start_count = annual_counts.iloc[0]
        end_count = annual_counts.iloc[-1]
        years = annual_counts.index.max() - annual_counts.index.min()
        if years > 0:
            cagr = (((end_count / start_count) ** (1/years)) - 1) * 100
            print(f"  {work_type:>20}: {cagr:>+6.1f}% CAGR ({annual_counts.index.min()}-{annual_counts.index.max()})")

# 2. OCCUPANCY TYPE ANALYSIS
print("\n\n2. OCCUPANCY TYPE ANALYSIS")
print("-" * 60)

# Count occupancy types
occupancy_counts = permits_df['occupancyType'].value_counts(dropna=False)
print(f"\nUnique occupancy types: {len(occupancy_counts) - (1 if pd.isna(occupancy_counts.index).any() else 0)}")
print(f"Records with missing occupancy type: {occupancy_counts.get(np.nan, 0):,} ({occupancy_counts.get(np.nan, 0)/len(permits_df)*100:.2f}%)")

print("\nOccupancy Type Distribution:")
for i, (occ_type, count) in enumerate(occupancy_counts.items(), 1):
    pct = count / len(permits_df) * 100
    if pd.isna(occ_type):
        print(f"  {'[Missing]':>10}: {count:>7,} ({pct:>5.1f}%)")
    else:
        print(f"  {occ_type:>10}: {count:>7,} ({pct:>5.1f}%)")

# Occupancy type trends
print("\n\nOccupancy Type Trends:")
for occ_type in occupancy_counts.dropna().index:
    ot_df = permits_df[permits_df['occupancyType'] == occ_type]
    annual_counts = ot_df['issueYear'].value_counts().sort_index()
    if len(annual_counts) > 1:
        start_count = annual_counts.iloc[0]
        end_count = annual_counts.iloc[-1]
        years = annual_counts.index.max() - annual_counts.index.min()
        if years > 0 and start_count > 0:
            cagr = (((end_count / start_count) ** (1/years)) - 1) * 100
            print(f"  {occ_type:>10}: {cagr:>+6.1f}% CAGR ({annual_counts.index.min()}-{annual_counts.index.max()})")

# 3. CROSS-TABULATION ANALYSIS
print("\n\n3. CROSS-TABULATION ANALYSIS")
print("-" * 60)

# Create cross-tab of permitType x workType (top combinations)
print("\nTop 20 Permit Type × Work Type Combinations:")
combo_counts = permits_df.groupby(['permitType', 'workType']).size().reset_index(name='count')
combo_counts = combo_counts.sort_values('count', ascending=False)

for i, row in combo_counts.head(20).iterrows():
    pct = row['count'] / len(permits_df) * 100
    permit_type = row['permitType'] if pd.notna(row['permitType']) else '[Missing]'
    work_type = row['workType'] if pd.notna(row['workType']) else '[Missing]'
    print(f"{i+1:>3}. {permit_type:>12} × {work_type:>20}: {row['count']:>7,} ({pct:>5.1f}%)")

# permitType x occupancyType
print("\n\nPermit Type × Occupancy Type Matrix:")
pt_ot_crosstab = pd.crosstab(permits_df['permitType'], permits_df['occupancyType'], margins=True)
print(pt_ot_crosstab.to_string())

# 4. PROCESSING TIME BY WORK TYPE
print("\n\n4. PROCESSING TIME BY WORK TYPE")
print("-" * 60)

# Calculate average processing time by work type
valid_processing = permits_df[permits_df['processing_days'].notna() & (permits_df['processing_days'] >= 0)]
print(f"\nRecords with valid processing time: {len(valid_processing):,} ({len(valid_processing)/len(permits_df)*100:.1f}%)")

print("\nAverage Processing Time by Work Type (Top 20):")
processing_by_wt = valid_processing.groupby('workType')['processing_days'].agg(['mean', 'median', 'count'])
processing_by_wt = processing_by_wt[processing_by_wt['count'] >= 100]  # Only work types with 100+ records
processing_by_wt = processing_by_wt.sort_values('mean', ascending=False)

for work_type, row in processing_by_wt.head(20).iterrows():
    wt_display = work_type if pd.notna(work_type) else '[Missing]'
    print(f"  {wt_display:>20}: {row['mean']:>6.1f} days (median: {row['median']:>5.0f}, n={row['count']:,})")

# 5. STATUS SUCCESS RATES BY WORK TYPE
print("\n\n5. STATUS SUCCESS RATES BY WORK TYPE")
print("-" * 60)

# Calculate success rates (Closed status) by work type
print("\nApproval Rates by Work Type (Top 20 by volume):")
for work_type in work_type_counts.head(20).index:
    wt_df = permits_df[permits_df['workType'] == work_type]
    closed_count = len(wt_df[wt_df['status'] == 'Closed'])
    cancelled_count = len(wt_df[wt_df['status'] == 'Cancelled'])
    total_count = len(wt_df)
    
    if total_count > 0:
        approval_rate = closed_count / total_count * 100
        rejection_rate = cancelled_count / total_count * 100
        wt_display = work_type if pd.notna(work_type) else '[Missing]'
        print(f"  {wt_display:>20}: {approval_rate:>5.1f}% approved, {rejection_rate:>5.1f}% cancelled (n={total_count:,})")

# 6. VALUE ANALYSIS BY WORK TYPE
print("\n\n6. VALUE ANALYSIS BY WORK TYPE")
print("-" * 60)

# Calculate average value by work type
value_df = permits_df[permits_df['value'].notna() & (permits_df['value'] > 0)]
print(f"\nRecords with valid value: {len(value_df):,} ({len(value_df)/len(permits_df)*100:.1f}%)")

print("\nAverage Project Value by Work Type (Top 20):")
value_by_wt = value_df.groupby('workType')['value'].agg(['mean', 'median', 'sum', 'count'])
value_by_wt = value_by_wt[value_by_wt['count'] >= 50]  # Only work types with 50+ records
value_by_wt = value_by_wt.sort_values('mean', ascending=False)

for work_type, row in value_by_wt.head(20).iterrows():
    wt_display = work_type if pd.notna(work_type) else '[Missing]'
    print(f"  {wt_display:>20}: ${row['mean']:>12,.0f} avg (median: ${row['median']:>10,.0f}, total: ${row['sum']:>15,.0f})")

# 7. OCCUPANCY × WORK TYPE PATTERNS
print("\n\n7. OCCUPANCY × WORK TYPE PATTERNS")
print("-" * 60)

# Analyze common patterns
print("\nMost Common Occupancy × Work Type Combinations:")
occ_wt_combo = permits_df.groupby(['occupancyType', 'workType']).size().reset_index(name='count')
occ_wt_combo = occ_wt_combo.sort_values('count', ascending=False)

for i, row in occ_wt_combo.head(15).iterrows():
    pct = row['count'] / len(permits_df) * 100
    occ_type = row['occupancyType'] if pd.notna(row['occupancyType']) else '[Missing]'
    work_type = row['workType'] if pd.notna(row['workType']) else '[Missing]'
    print(f"{i+1:>3}. {occ_type:>10} × {work_type:>20}: {row['count']:>7,} ({pct:>5.1f}%)")

# 8. TIME HORIZON ANALYSIS
print("\n\n8. WORK TYPE DISTRIBUTION BY TIME HORIZON")
print("-" * 60)

# Define horizons
current_date = permits_df['issueDate'].max()
horizons = {
    '3-year': current_date - pd.DateOffset(years=3),
    '5-year': current_date - pd.DateOffset(years=5),
    '10-year': current_date - pd.DateOffset(years=10)
}

for horizon_name, start_date in horizons.items():
    horizon_df = permits_df[permits_df['issueDate'] >= start_date]
    print(f"\n{horizon_name} Horizon - Top 10 Work Types:")
    horizon_wt = horizon_df['workType'].value_counts().head(10)
    for work_type, count in horizon_wt.items():
        pct = count / len(horizon_df) * 100
        print(f"  {work_type:>20}: {count:>7,} ({pct:>5.1f}%)")

# Export enhanced metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

work_occupancy_metrics = {
    'work_types': {
        'unique_count': int(len(work_type_counts.dropna())),
        'missing_count': int(work_type_counts.get(np.nan, 0)),
        'top_10': work_type_counts.head(10).to_dict()
    },
    'occupancy_types': {
        'unique_count': int(len(occupancy_counts.dropna())),
        'missing_count': int(occupancy_counts.get(np.nan, 0)),
        'distribution': occupancy_counts.to_dict()
    },
    'processing_times': processing_by_wt.head(20).to_dict('index'),
    'value_analysis': value_by_wt.head(20).to_dict('index'),
    'top_combinations': combo_counts.head(20).to_dict('records')
}

# Convert NaN to None for JSON serialization
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

work_occupancy_metrics = clean_for_json(work_occupancy_metrics)

with open(f'{output_dir}/work_occupancy_metrics.json', 'w') as f:
    json.dump(work_occupancy_metrics, f, indent=2)

print(f"\n✓ Iteration 2 complete. Work/Occupancy metrics saved to {output_dir}/work_occupancy_metrics.json")

# Key insights summary
print("\n\nKEY WORK TYPE & OCCUPANCY INSIGHTS:")
print("=" * 60)
print(f"1. Most common work types: {', '.join([str(wt) for wt in work_type_counts.head(3).index])}")
print(f"2. Dominant occupancy types: {', '.join([str(ot) for ot in occupancy_counts.dropna().head(3).index])}")
print(f"3. Longest processing: {processing_by_wt.head(1).index[0] if len(processing_by_wt) > 0 else 'N/A'}")
print(f"4. Highest value work: {value_by_wt.head(1).index[0] if len(value_by_wt) > 0 else 'N/A'}")
print("5. Work type patterns vary significantly by occupancy type")