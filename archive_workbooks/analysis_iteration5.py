#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 5: Contractor Performance Analytics
"""

import pandas as pd
import numpy as np
from collections import Counter
import json
import warnings
import os
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)

print("=" * 80)
print("Minneapolis Permits Analysis - Iteration 5: Contractor Performance Analytics")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['completeDate'] = pd.to_datetime(permits_df['completeDate'], errors='coerce')
permits_df['issueYear'] = permits_df['issueDate'].dt.year
permits_df['processing_days'] = (permits_df['completeDate'] - permits_df['issueDate']).dt.days
permits_df.loc[permits_df['processing_days'] < 0, 'processing_days'] = np.nan

print(f"\nData loaded: {len(permits_df):,} permits")
print(f"Unique applicants: {permits_df['applicantName'].nunique():,}")

# 1. TOP CONTRACTORS ANALYSIS
print("\n\n1. TOP CONTRACTORS ANALYSIS")
print("-" * 60)

# Get top contractors overall
contractor_counts = permits_df['applicantName'].value_counts()
print(f"\nTop 25 Contractors by Total Permit Count:")
for i, (contractor, count) in enumerate(contractor_counts.head(25).items(), 1):
    pct = count / len(permits_df) * 100
    print(f"{i:>3}. {contractor[:40]:>40}: {count:>6,} ({pct:>5.2f}%)")

# 2. CONTRACTOR PERFORMANCE METRICS
print("\n\n2. CONTRACTOR PERFORMANCE METRICS")
print("-" * 60)

# Calculate performance metrics for contractors with 100+ permits
significant_contractors = contractor_counts[contractor_counts >= 100].index

contractor_metrics = []
for contractor in significant_contractors:
    contractor_df = permits_df[permits_df['applicantName'] == contractor]
    
    # Calculate metrics
    total_permits = len(contractor_df)
    closed_permits = len(contractor_df[contractor_df['status'] == 'Closed'])
    cancelled_permits = len(contractor_df[contractor_df['status'] == 'Cancelled'])
    
    # Processing time for completed permits
    completed_df = contractor_df[contractor_df['processing_days'].notna() & (contractor_df['processing_days'] >= 0)]
    avg_processing = completed_df['processing_days'].mean() if len(completed_df) > 0 else np.nan
    median_processing = completed_df['processing_days'].median() if len(completed_df) > 0 else np.nan
    
    # Value metrics
    value_df = contractor_df[contractor_df['value'].notna() & (contractor_df['value'] > 0)]
    avg_value = value_df['value'].mean() if len(value_df) > 0 else np.nan
    total_value = value_df['value'].sum() if len(value_df) > 0 else 0
    
    contractor_metrics.append({
        'contractor': contractor,
        'total_permits': total_permits,
        'approval_rate': closed_permits / total_permits * 100 if total_permits > 0 else 0,
        'cancellation_rate': cancelled_permits / total_permits * 100 if total_permits > 0 else 0,
        'avg_processing_days': avg_processing,
        'median_processing_days': median_processing,
        'avg_project_value': avg_value,
        'total_project_value': total_value
    })

contractor_metrics_df = pd.DataFrame(contractor_metrics)

# Display top performers by different metrics
print("\nTop 15 Contractors by Approval Rate (100+ permits):")
top_approval = contractor_metrics_df.nlargest(15, 'approval_rate')
for _, row in top_approval.iterrows():
    print(f"  {row['contractor'][:40]:>40}: {row['approval_rate']:>5.1f}% ({row['total_permits']:,} permits)")

print("\n\nFastest Processing Contractors (100+ permits, median days):")
fast_processing = contractor_metrics_df.dropna(subset=['median_processing_days']).nsmallest(15, 'median_processing_days')
for _, row in fast_processing.iterrows():
    print(f"  {row['contractor'][:40]:>40}: {row['median_processing_days']:>5.0f} days median ({row['total_permits']:,} permits)")

# 3. CONTRACTOR SPECIALIZATION
print("\n\n3. CONTRACTOR SPECIALIZATION")
print("-" * 60)

# Analyze permit type specialization for top contractors
top_50_contractors = contractor_counts.head(50).index

print("\nPermit Type Specialization (Top 50 Contractors):")
for contractor in top_50_contractors[:20]:  # Show first 20
    contractor_df = permits_df[permits_df['applicantName'] == contractor]
    permit_types = contractor_df['permitType'].value_counts()
    total = len(contractor_df)
    
    # Calculate specialization (how concentrated in top permit type)
    specialization = permit_types.iloc[0] / total * 100 if len(permit_types) > 0 else 0
    
    print(f"\n{contractor[:40]}:")
    for permit_type, count in permit_types.head(3).items():
        pct = count / total * 100
        print(f"  {permit_type:>12}: {count:>5,} ({pct:>5.1f}%)")
    print(f"  Specialization: {specialization:.1f}% in {permit_types.index[0]}")

# 4. GEOGRAPHIC COVERAGE
print("\n\n4. CONTRACTOR GEOGRAPHIC COVERAGE")
print("-" * 60)

# Analyze geographic spread for top contractors
print("\nGeographic Coverage (Top 20 Contractors):")
for contractor in contractor_counts.head(20).index:
    contractor_df = permits_df[permits_df['applicantName'] == contractor]
    neighborhoods = contractor_df['Neighborhoods_Desc'].dropna().nunique()
    wards = contractor_df['Wards'].dropna().nunique()
    
    # Top neighborhoods
    top_neighborhoods = contractor_df['Neighborhoods_Desc'].value_counts().head(3)
    
    print(f"\n{contractor[:40]}:")
    print(f"  Coverage: {neighborhoods} neighborhoods, {wards} wards")
    print(f"  Top areas: {', '.join(top_neighborhoods.index.tolist())}")

# 5. CONTRACTOR GROWTH ANALYSIS
print("\n\n5. CONTRACTOR GROWTH ANALYSIS")
print("-" * 60)

# Analyze growth trends for contractors with 3+ years of activity
print("\nContractor Growth Trends (Active 3+ years):")
growth_analysis = []

for contractor in contractor_counts.head(50).index:
    contractor_df = permits_df[permits_df['applicantName'] == contractor]
    years_active = contractor_df['issueYear'].nunique()
    
    if years_active >= 3:
        # Get first and last 2 years
        year_counts = contractor_df['issueYear'].value_counts().sort_index()
        early_years = year_counts.iloc[:2].mean()
        recent_years = year_counts.iloc[-2:].mean()
        
        if early_years > 0:
            growth_rate = ((recent_years - early_years) / early_years) * 100
            
            growth_analysis.append({
                'contractor': contractor,
                'years_active': years_active,
                'early_avg': early_years,
                'recent_avg': recent_years,
                'growth_rate': growth_rate
            })

growth_df = pd.DataFrame(growth_analysis)

# Show fastest growing
print("\nFastest Growing Contractors:")
fastest_growing = growth_df.nlargest(10, 'growth_rate')
for _, row in fastest_growing.iterrows():
    print(f"  {row['contractor'][:40]:>40}: {row['growth_rate']:>+6.1f}% ({row['early_avg']:.0f} → {row['recent_avg']:.0f} permits/year)")

# Show declining
print("\n\nDeclining Contractors:")
declining = growth_df.nsmallest(10, 'growth_rate')
declining = declining[declining['growth_rate'] < 0]
for _, row in declining.iterrows():
    print(f"  {row['contractor'][:40]:>40}: {row['growth_rate']:>+6.1f}% ({row['early_avg']:.0f} → {row['recent_avg']:.0f} permits/year)")

# 6. NEW VS ESTABLISHED CONTRACTORS
print("\n\n6. NEW VS ESTABLISHED CONTRACTORS")
print("-" * 60)

# Identify new contractors (first permit in 2022 or later)
contractor_first_year = permits_df.groupby('applicantName')['issueYear'].min()
new_contractors = contractor_first_year[contractor_first_year >= 2022].index

# Get metrics for new contractors
new_contractor_permits = permits_df[permits_df['applicantName'].isin(new_contractors)]
new_contractor_counts = new_contractor_permits['applicantName'].value_counts()

print(f"\nNew Contractors (Started 2022+): {len(new_contractors):,}")
print("\nTop 15 New Contractors by Volume:")
for contractor, count in new_contractor_counts.head(15).items():
    first_year = contractor_first_year[contractor]
    print(f"  {contractor[:40]:>40}: {count:>4,} permits (started {first_year})")

# 7. CONTRACTOR EFFICIENCY RANKING
print("\n\n7. CONTRACTOR EFFICIENCY RANKING")
print("-" * 60)

# Create efficiency score based on multiple factors
efficiency_scores = []

for _, row in contractor_metrics_df.iterrows():
    if row['total_permits'] >= 100:  # Only contractors with 100+ permits
        # Calculate efficiency score (0-100)
        score = 0
        
        # Approval rate (0-40 points)
        score += (row['approval_rate'] / 100) * 40
        
        # Processing speed (0-30 points, faster is better)
        if pd.notna(row['median_processing_days']):
            # Normalize to 0-1 scale (assume 500 days is worst, 0 is best)
            speed_score = max(0, 1 - (row['median_processing_days'] / 500))
            score += speed_score * 30
        
        # Volume (0-20 points, logarithmic scale)
        volume_score = min(1, np.log10(row['total_permits']) / 4)  # 10,000 permits = max score
        score += volume_score * 20
        
        # Low cancellation rate (0-10 points)
        score += (1 - row['cancellation_rate'] / 100) * 10
        
        efficiency_scores.append({
            'contractor': row['contractor'],
            'efficiency_score': score,
            'total_permits': row['total_permits'],
            'approval_rate': row['approval_rate'],
            'median_days': row['median_processing_days']
        })

efficiency_df = pd.DataFrame(efficiency_scores)
efficiency_df = efficiency_df.sort_values('efficiency_score', ascending=False)

print("\nTop 20 Contractors by Efficiency Score:")
for i, row in efficiency_df.head(20).iterrows():
    print(f"  {row['contractor'][:40]:>40}: {row['efficiency_score']:>5.1f} score ({row['total_permits']:,} permits)")

# Export contractor metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

contractor_analytics = {
    'overview': {
        'unique_contractors': int(permits_df['applicantName'].nunique()),
        'contractors_100plus': int(len(significant_contractors)),
        'new_contractors_2022plus': int(len(new_contractors))
    },
    'top_contractors': contractor_counts.head(50).to_dict(),
    'performance_metrics': contractor_metrics_df.head(50).to_dict('records'),
    'efficiency_rankings': efficiency_df.head(50).to_dict('records'),
    'growth_analysis': growth_df.to_dict('records'),
    'new_contractors': new_contractor_counts.head(30).to_dict()
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

contractor_analytics = clean_for_json(contractor_analytics)

with open(f'{output_dir}/contractor_metrics.json', 'w') as f:
    json.dump(contractor_analytics, f, indent=2)

print(f"\n✓ Iteration 5 complete. Contractor metrics saved to {output_dir}/contractor_metrics.json")

# Key insights summary
print("\n\nKEY CONTRACTOR INSIGHTS:")
print("=" * 60)
print(f"1. Top contractor: {contractor_counts.index[0]} with {contractor_counts.iloc[0]:,} permits")
print(f"2. Market concentration: Top 25 contractors = {contractor_counts.head(25).sum() / len(permits_df) * 100:.1f}% of permits")
print(f"3. New entrants: {len(new_contractors):,} contractors started since 2022")
print(f"4. Most efficient: {efficiency_df.iloc[0]['contractor'] if len(efficiency_df) > 0 else 'N/A'}")
print("5. Significant specialization patterns exist among top contractors")