#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 8: Status and Milestone Analytics
"""

import pandas as pd
import numpy as np
import json
import warnings
import os
from datetime import datetime
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)

print("=" * 80)
print("Minneapolis Permits Analysis - Iteration 8: Status & Milestone Analytics")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['completeDate'] = pd.to_datetime(permits_df['completeDate'], errors='coerce')
permits_df['issueYear'] = permits_df['issueDate'].dt.year
permits_df['processing_days'] = (permits_df['completeDate'] - permits_df['issueDate']).dt.days

print(f"\nData loaded: {len(permits_df):,} permits")

# 1. STATUS DISTRIBUTION ANALYSIS
print("\n\n1. STATUS DISTRIBUTION ANALYSIS")
print("-" * 60)

status_counts = permits_df['status'].value_counts(dropna=False)
print("\nOverall Status Distribution:")
for status, count in status_counts.items():
    pct = count / len(permits_df) * 100
    print(f"  {str(status):>12}: {count:>7,} ({pct:>5.1f}%)")

# Status by year
print("\n\nStatus Distribution by Year (2020-2024):")
recent_years = permits_df[permits_df['issueYear'].between(2020, 2024)]
status_year_crosstab = pd.crosstab(recent_years['issueYear'], recent_years['status'], normalize='index') * 100
print(status_year_crosstab.round(1).to_string())

# 2. MILESTONE ANALYSIS
print("\n\n2. MILESTONE ANALYSIS")
print("-" * 60)

milestone_counts = permits_df['milestone'].value_counts(dropna=False)
print("\nMilestone Distribution:")
for milestone, count in milestone_counts.items():
    pct = count / len(permits_df) * 100
    print(f"  {str(milestone):>15}: {count:>7,} ({pct:>5.1f}%)")

# Milestone vs Status relationship
print("\n\nMilestone-Status Relationship:")
milestone_status = pd.crosstab(permits_df['milestone'], permits_df['status'])
print(milestone_status.to_string())

# 3. PROCESSING TIME BY STATUS
print("\n\n3. PROCESSING TIME BY STATUS")
print("-" * 60)

# Calculate time in each status (for closed permits)
closed_permits = permits_df[permits_df['status'] == 'Closed'].copy()
closed_permits = closed_permits[closed_permits['processing_days'] >= 0]

print(f"\nClosed Permits Processing Time Analysis:")
print(f"  Total closed permits: {len(closed_permits):,}")
print(f"  Average processing time: {closed_permits['processing_days'].mean():.1f} days")
print(f"  Median processing time: {closed_permits['processing_days'].median():.0f} days")

# Processing time distribution
processing_bins = [0, 7, 30, 90, 180, 365, float('inf')]
processing_labels = ['<1 week', '1-4 weeks', '1-3 months', '3-6 months', '6-12 months', '>1 year']
closed_permits['processing_category'] = pd.cut(closed_permits['processing_days'], 
                                               bins=processing_bins, 
                                               labels=processing_labels)

processing_dist = closed_permits['processing_category'].value_counts()
print("\nProcessing Time Distribution (Closed Permits):")
for category, count in processing_dist.items():
    pct = count / len(closed_permits) * 100
    print(f"  {category:>12}: {count:>7,} ({pct:>5.1f}%)")

# 4. STATUS TRANSITIONS
print("\n\n4. STATUS TRANSITIONS")
print("-" * 60)

# Analyze typical status paths
print("\nStatus by Permit Type:")
status_type_crosstab = pd.crosstab(permits_df['permitType'], permits_df['status'], normalize='index') * 100
print(status_type_crosstab.round(1).to_string())

# Success rate by work type
print("\n\nClosure Rate by Work Type (Top 20):")
work_types = permits_df['workType'].value_counts().head(20).index
for work_type in work_types:
    wt_df = permits_df[permits_df['workType'] == work_type]
    closed_rate = (wt_df['status'] == 'Closed').sum() / len(wt_df) * 100
    cancelled_rate = (wt_df['status'] == 'Cancelled').sum() / len(wt_df) * 100
    open_rate = (wt_df['status'].isin(['Issued', 'Inspection'])).sum() / len(wt_df) * 100
    
    print(f"  {work_type:>20}: Closed: {closed_rate:>5.1f}%, Cancelled: {cancelled_rate:>5.1f}%, Open: {open_rate:>5.1f}%")

# 5. BOTTLENECK IDENTIFICATION
print("\n\n5. BOTTLENECK IDENTIFICATION")
print("-" * 60)

# Identify permits stuck in certain statuses
current_date = pd.Timestamp.now(tz='UTC')
open_permits = permits_df[permits_df['status'].isin(['Issued', 'Inspection'])].copy()
open_permits['days_open'] = (current_date - open_permits['issueDate']).dt.days

# Long-open permits
long_open = open_permits[open_permits['days_open'] > 365]
print(f"\nLong-Open Permits (>1 year):")
print(f"  Total: {len(long_open):,} permits")
print(f"  Average days open: {long_open['days_open'].mean():.0f}")
print(f"  Oldest permit: {long_open['days_open'].max():.0f} days")

# By permit type
print("\nLong-Open Permits by Type:")
long_open_types = long_open['permitType'].value_counts()
for permit_type, count in long_open_types.items():
    pct = count / len(long_open) * 100
    print(f"  {permit_type:>12}: {count:>5,} ({pct:>5.1f}%)")

# 6. MILESTONE ACHIEVEMENT RATES
print("\n\n6. MILESTONE ACHIEVEMENT RATES")
print("-" * 60)

# Calculate milestone completion rates
milestone_completion = pd.DataFrame()
for milestone in ['Plan Review', 'Permit Issue', 'Inspection', 'Closed']:
    if milestone in permits_df['milestone'].values:
        count = (permits_df['milestone'] == milestone).sum()
        milestone_completion = pd.concat([milestone_completion, pd.DataFrame({
            'milestone': [milestone],
            'count': [count],
            'percentage': [count / len(permits_df) * 100]
        })])

if not milestone_completion.empty:
    print("\nMilestone Achievement:")
    for _, row in milestone_completion.iterrows():
        print(f"  {row['milestone']:>15}: {int(row['count']):>7,} ({row['percentage']:>5.1f}%)")

# 7. SEASONAL STATUS PATTERNS
print("\n\n7. SEASONAL STATUS PATTERNS")
print("-" * 60)

# Status by month
permits_df['issueMonth'] = permits_df['issueDate'].dt.month
monthly_status = pd.crosstab(permits_df['issueMonth'], permits_df['status'])

print("\nCancellation Rate by Month:")
for month in range(1, 13):
    if month in monthly_status.index:
        total = monthly_status.loc[month].sum()
        cancelled = monthly_status.loc[month].get('Cancelled', 0)
        cancel_rate = cancelled / total * 100 if total > 0 else 0
        month_name = pd.Timestamp(2024, month, 1).strftime('%B')
        print(f"  {month_name:>10}: {cancel_rate:>5.1f}%")

# 8. CONTRACTOR STATUS PERFORMANCE
print("\n\n8. CONTRACTOR STATUS PERFORMANCE")
print("-" * 60)

# Top contractors by completion rate
contractor_permits = permits_df.groupby('applicantName').agg({
    'status': lambda x: (x == 'Closed').sum(),
    'permitNumber': 'count'
}).rename(columns={'status': 'closed_count', 'permitNumber': 'total_count'})

contractor_permits = contractor_permits[contractor_permits['total_count'] >= 100]
contractor_permits['completion_rate'] = contractor_permits['closed_count'] / contractor_permits['total_count'] * 100
contractor_permits = contractor_permits.sort_values('completion_rate', ascending=False)

print("\nTop 15 Contractors by Completion Rate (100+ permits):")
for contractor, row in contractor_permits.head(15).iterrows():
    print(f"  {contractor[:40]:>40}: {row['completion_rate']:>5.1f}% ({int(row['total_count']):,} permits)")

print("\n\nBottom 15 Contractors by Completion Rate (100+ permits):")
for contractor, row in contractor_permits.tail(15).iterrows():
    print(f"  {contractor[:40]:>40}: {row['completion_rate']:>5.1f}% ({int(row['total_count']):,} permits)")

# Export status and milestone metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

status_milestone_metrics = {
    'status_distribution': status_counts.to_dict(),
    'milestone_distribution': milestone_counts.to_dict(),
    'processing_time': {
        'closed_permits': int(len(closed_permits)),
        'avg_days': float(closed_permits['processing_days'].mean()),
        'median_days': float(closed_permits['processing_days'].median()),
        'distribution': processing_dist.to_dict()
    },
    'bottlenecks': {
        'long_open_permits': int(len(long_open)),
        'avg_days_open': float(long_open['days_open'].mean()),
        'by_type': long_open_types.to_dict()
    },
    'seasonal_patterns': {
        'monthly_cancellation_rates': {
            month: float((monthly_status.loc[month].get('Cancelled', 0) / monthly_status.loc[month].sum() * 100))
            for month in range(1, 13) if month in monthly_status.index
        }
    },
    'contractor_performance': {
        'top_completion': contractor_permits.head(20).to_dict('index'),
        'bottom_completion': contractor_permits.tail(20).to_dict('index')
    }
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

status_milestone_metrics = clean_for_json(status_milestone_metrics)

with open(f'{output_dir}/status_milestone_metrics.json', 'w') as f:
    json.dump(status_milestone_metrics, f, indent=2)

print(f"\n✓ Iteration 8 complete. Status/Milestone metrics saved to {output_dir}/status_milestone_metrics.json")

# Key insights summary
print("\n\nKEY STATUS & MILESTONE INSIGHTS:")
print("=" * 60)
print(f"1. {status_counts.iloc[0] / len(permits_df) * 100:.1f}% of permits are {status_counts.index[0]}")
print(f"2. Average processing time for closed permits: {closed_permits['processing_days'].mean():.0f} days")
print(f"3. {len(long_open):,} permits have been open >1 year")
print(f"4. Cancellation rates vary by month (peak: {max(monthly_status.loc[month].get('Cancelled', 0) / monthly_status.loc[month].sum() * 100 for month in range(1, 13) if month in monthly_status.index):.1f}%)")
print("5. Significant variation in contractor completion rates")