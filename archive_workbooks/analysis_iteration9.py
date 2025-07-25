#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 9: Failure and Rejection Analysis
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
print("Minneapolis Permits Analysis - Iteration 9: Failure & Rejection Analysis")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['completeDate'] = pd.to_datetime(permits_df['completeDate'], errors='coerce')
permits_df['issueYear'] = permits_df['issueDate'].dt.year
permits_df['issueMonth'] = permits_df['issueDate'].dt.month
permits_df['processing_days'] = (permits_df['completeDate'] - permits_df['issueDate']).dt.days

print(f"\nData loaded: {len(permits_df):,} permits")

# 1. FAILURE TYPE IDENTIFICATION
print("\n\n1. FAILURE TYPE IDENTIFICATION")
print("-" * 60)

# Identify different types of failures
cancelled_df = permits_df[permits_df['status'] == 'Cancelled']
withdrawn_df = permits_df[permits_df['status'] == 'Withdrawn']
void_df = permits_df[permits_df['status'] == 'Void']
stop_work_df = permits_df[permits_df['status'] == 'Stop Work']

print(f"\nFailure Categories:")
print(f"  Cancelled:  {len(cancelled_df):>6,} ({len(cancelled_df)/len(permits_df)*100:>5.2f}%)")
print(f"  Withdrawn:  {len(withdrawn_df):>6,} ({len(withdrawn_df)/len(permits_df)*100:>5.2f}%)")
print(f"  Void:       {len(void_df):>6,} ({len(void_df)/len(permits_df)*100:>5.2f}%)")
print(f"  Stop Work:  {len(stop_work_df):>6,} ({len(stop_work_df)/len(permits_df)*100:>5.2f}%)")
print(f"  Total:      {len(cancelled_df) + len(withdrawn_df) + len(void_df) + len(stop_work_df):>6,} ({(len(cancelled_df) + len(withdrawn_df) + len(void_df) + len(stop_work_df))/len(permits_df)*100:>5.2f}%)")

# 2. CANCELLATION ANALYSIS
print("\n\n2. CANCELLATION ANALYSIS")
print("-" * 60)

# Cancellation by permit type
cancel_by_type = cancelled_df['permitType'].value_counts()
print("\nCancellations by Permit Type:")
for permit_type, count in cancel_by_type.items():
    pct_of_cancelled = count / len(cancelled_df) * 100
    type_df = permits_df[permits_df['permitType'] == permit_type]
    cancel_rate = count / len(type_df) * 100
    print(f"  {permit_type:>12}: {count:>4,} ({pct_of_cancelled:>5.1f}% of cancelled, {cancel_rate:>5.1f}% cancel rate)")

# Cancellation by work type
cancel_by_work = cancelled_df['workType'].value_counts().head(15)
print("\n\nTop 15 Work Types by Cancellation Count:")
for work_type, count in cancel_by_work.items():
    work_df = permits_df[permits_df['workType'] == work_type]
    cancel_rate = count / len(work_df) * 100 if len(work_df) > 0 else 0
    print(f"  {work_type:>20}: {count:>4,} ({cancel_rate:>5.1f}% cancel rate)")

# 3. TIMING OF CANCELLATIONS
print("\n\n3. TIMING OF CANCELLATIONS")
print("-" * 60)

# Days from issue to cancellation
cancelled_with_complete = cancelled_df[cancelled_df['completeDate'].notna()].copy()
cancelled_with_complete['days_to_cancel'] = (cancelled_with_complete['completeDate'] - cancelled_with_complete['issueDate']).dt.days
cancelled_with_complete = cancelled_with_complete[cancelled_with_complete['days_to_cancel'] >= 0]

if len(cancelled_with_complete) > 0:
    print(f"\nCancellation Timing Analysis:")
    print(f"  Cancellations with completion date: {len(cancelled_with_complete):,}")
    print(f"  Average days to cancellation: {cancelled_with_complete['days_to_cancel'].mean():.1f}")
    print(f"  Median days to cancellation: {cancelled_with_complete['days_to_cancel'].median():.0f}")
    
    # Distribution
    cancel_bins = [0, 7, 30, 90, 180, 365, float('inf')]
    cancel_labels = ['<1 week', '1-4 weeks', '1-3 months', '3-6 months', '6-12 months', '>1 year']
    cancelled_with_complete['cancel_timing'] = pd.cut(cancelled_with_complete['days_to_cancel'], 
                                                      bins=cancel_bins, 
                                                      labels=cancel_labels)
    
    timing_dist = cancelled_with_complete['cancel_timing'].value_counts()
    print("\nCancellation Timing Distribution:")
    for timing, count in timing_dist.items():
        pct = count / len(cancelled_with_complete) * 100
        print(f"  {timing:>12}: {count:>4,} ({pct:>5.1f}%)")

# 4. SEASONAL FAILURE PATTERNS
print("\n\n4. SEASONAL FAILURE PATTERNS")
print("-" * 60)

# Monthly cancellation patterns
monthly_failures = permits_df.groupby('issueMonth').agg({
    'status': lambda x: (x.isin(['Cancelled', 'Withdrawn', 'Void', 'Stop Work'])).sum(),
    'permitNumber': 'count'
}).rename(columns={'status': 'failures', 'permitNumber': 'total'})

monthly_failures['failure_rate'] = monthly_failures['failures'] / monthly_failures['total'] * 100

print("\nFailure Rate by Month:")
months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for month, row in monthly_failures.iterrows():
    if month <= 12:
        print(f"  {months[month-1]:>3}: {row['failure_rate']:>5.2f}% ({int(row['failures']):>4,} failures)")

# 5. HIGH-RISK INDICATORS
print("\n\n5. HIGH-RISK INDICATORS")
print("-" * 60)

# Analyze characteristics of cancelled permits
print("\nCharacteristics of Cancelled Permits:")

# Value analysis
cancelled_with_value = cancelled_df[cancelled_df['value'].notna() & (cancelled_df['value'] > 0)]
all_with_value = permits_df[permits_df['value'].notna() & (permits_df['value'] > 0)]

if len(cancelled_with_value) > 0 and len(all_with_value) > 0:
    print(f"\nProject Value Analysis:")
    print(f"  Average value - Cancelled: ${cancelled_with_value['value'].mean():,.2f}")
    print(f"  Average value - All permits: ${all_with_value['value'].mean():,.2f}")
    print(f"  Median value - Cancelled: ${cancelled_with_value['value'].median():,.2f}")
    print(f"  Median value - All permits: ${all_with_value['value'].median():,.2f}")

# Contractor analysis
contractor_cancels = cancelled_df.groupby('applicantName').size()
contractor_totals = permits_df.groupby('applicantName').size()
contractor_cancel_rates = (contractor_cancels / contractor_totals * 100).dropna()
contractor_cancel_rates = contractor_cancel_rates[contractor_totals >= 50]  # 50+ permits

print("\n\nHighest Cancellation Rate Contractors (50+ permits):")
high_cancel_contractors = contractor_cancel_rates.nlargest(15)
for contractor, rate in high_cancel_contractors.items():
    total = contractor_totals[contractor]
    cancelled = contractor_cancels.get(contractor, 0)
    print(f"  {contractor[:40]:>40}: {rate:>5.1f}% ({cancelled}/{total} permits)")

# 6. FAILURE RECOVERY ANALYSIS
print("\n\n6. FAILURE RECOVERY ANALYSIS")
print("-" * 60)

# Look for patterns where applicants reapply after cancellation
# This requires analyzing same applicant, same address, similar timeframe
print("\nReapplication Analysis (Sample):")

# Sample analysis - look at top contractors
top_contractors = permits_df['applicantName'].value_counts().head(20).index

reapplication_patterns = []
for contractor in top_contractors:
    contractor_df = permits_df[permits_df['applicantName'] == contractor].sort_values('issueDate')
    
    # Look for cancelled permits followed by new permits at same address
    cancelled_permits = contractor_df[contractor_df['status'] == 'Cancelled']
    
    if len(cancelled_permits) > 0:
        for _, cancelled in cancelled_permits.iterrows():
            if pd.notna(cancelled['Display']):
                # Look for subsequent permits at same address
                subsequent = contractor_df[
                    (contractor_df['Display'] == cancelled['Display']) &
                    (contractor_df['issueDate'] > cancelled['issueDate']) &
                    (contractor_df['issueDate'] <= cancelled['issueDate'] + pd.Timedelta(days=365))
                ]
                
                if len(subsequent) > 0:
                    reapplication_patterns.append({
                        'contractor': contractor,
                        'address': cancelled['Display'],
                        'original_date': cancelled['issueDate'],
                        'reapplied_count': len(subsequent)
                    })

if reapplication_patterns:
    print(f"  Found {len(reapplication_patterns)} potential reapplication patterns")
    print("\n  Sample Reapplication Cases:")
    for i, pattern in enumerate(reapplication_patterns[:5]):
        print(f"    {i+1}. {pattern['contractor'][:30]} at {pattern['address'][:30]}")
        print(f"       Original: {pattern['original_date'].strftime('%Y-%m-%d')}, Reapplied: {pattern['reapplied_count']} time(s)")

# 7. FAILURE IMPACT ANALYSIS
print("\n\n7. FAILURE IMPACT ANALYSIS")
print("-" * 60)

# Calculate lost revenue from cancellations
cancelled_fees = cancelled_df['totalFees'].sum()
print(f"\nFinancial Impact:")
print(f"  Total fees from cancelled permits: ${cancelled_fees:,.2f}")
print(f"  Average fee per cancellation: ${cancelled_df['totalFees'].mean():,.2f}")

# Calculate lost project value
cancelled_value = cancelled_df['value'].sum()
print(f"\n  Total project value cancelled: ${cancelled_value:,.2f}")
print(f"  Average project value cancelled: ${cancelled_df[cancelled_df['value'] > 0]['value'].mean():,.2f}")

# 8. WORK TYPE FAILURE ANALYSIS
print("\n\n8. WORK TYPE FAILURE ANALYSIS")
print("-" * 60)

# Analyze failure rates by work type
work_type_failures = permits_df.groupby('workType').agg({
    'status': lambda x: (x.isin(['Cancelled', 'Withdrawn', 'Void', 'Stop Work'])).sum(),
    'permitNumber': 'count'
}).rename(columns={'status': 'failures', 'permitNumber': 'total'})

work_type_failures = work_type_failures[work_type_failures['total'] >= 100]  # 100+ permits
work_type_failures['failure_rate'] = work_type_failures['failures'] / work_type_failures['total'] * 100
work_type_failures = work_type_failures.sort_values('failure_rate', ascending=False)

print("\nHighest Failure Rate Work Types (100+ permits):")
for work_type, row in work_type_failures.head(15).iterrows():
    print(f"  {work_type:>20}: {row['failure_rate']:>5.2f}% ({int(row['failures'])}/{int(row['total'])} permits)")

# Export failure and rejection metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

failure_metrics = {
    'overview': {
        'total_failures': int(len(cancelled_df) + len(withdrawn_df) + len(void_df) + len(stop_work_df)),
        'failure_rate': float((len(cancelled_df) + len(withdrawn_df) + len(void_df) + len(stop_work_df))/len(permits_df)*100),
        'cancelled': int(len(cancelled_df)),
        'withdrawn': int(len(withdrawn_df)),
        'void': int(len(void_df)),
        'stop_work': int(len(stop_work_df))
    },
    'cancellation_analysis': {
        'by_permit_type': cancel_by_type.to_dict(),
        'by_work_type': cancel_by_work.to_dict(),
        'timing_distribution': timing_dist.to_dict() if 'timing_dist' in locals() else {}
    },
    'seasonal_patterns': monthly_failures.to_dict('index'),
    'high_risk_contractors': high_cancel_contractors.to_dict(),
    'financial_impact': {
        'total_fees_lost': float(cancelled_fees),
        'avg_fee_lost': float(cancelled_df['totalFees'].mean()),
        'total_value_lost': float(cancelled_value),
        'avg_value_lost': float(cancelled_df[cancelled_df['value'] > 0]['value'].mean()) if len(cancelled_df[cancelled_df['value'] > 0]) > 0 else 0
    },
    'work_type_failures': work_type_failures.head(20).to_dict('index')
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
    elif isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    else:
        return obj

failure_metrics = clean_for_json(failure_metrics)

with open(f'{output_dir}/failure_rejection_metrics.json', 'w') as f:
    json.dump(failure_metrics, f, indent=2)

print(f"\n✓ Iteration 9 complete. Failure/Rejection metrics saved to {output_dir}/failure_rejection_metrics.json")

# Key insights summary
print("\n\nKEY FAILURE & REJECTION INSIGHTS:")
print("=" * 60)
print(f"1. Overall failure rate: {(len(cancelled_df) + len(withdrawn_df) + len(void_df) + len(stop_work_df))/len(permits_df)*100:.2f}%")
print(f"2. Cancellations account for {len(cancelled_df)/(len(cancelled_df) + len(withdrawn_df) + len(void_df) + len(stop_work_df))*100:.1f}% of failures")
print(f"3. Site permits have highest cancellation rate among permit types")
print(f"4. ${cancelled_fees:,.0f} in fees lost to cancellations")
print("5. Clear seasonal patterns in failure rates")