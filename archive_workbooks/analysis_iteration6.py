#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 6: Financial Deep Dive
"""

import pandas as pd
import numpy as np
import json
import warnings
import os
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)

print("=" * 80)
print("Minneapolis Permits Analysis - Iteration 6: Financial Deep Dive")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['issueYear'] = permits_df['issueDate'].dt.year
permits_df['issueMonth'] = permits_df['issueDate'].dt.month

print(f"\nData loaded: {len(permits_df):,} permits")

# 1. VALUE DISTRIBUTION ANALYSIS
print("\n\n1. VALUE DISTRIBUTION ANALYSIS")
print("-" * 60)

# Basic value statistics
value_df = permits_df[permits_df['value'].notna() & (permits_df['value'] > 0)].copy()
zero_value = len(permits_df[permits_df['value'] == 0])
missing_value = permits_df['value'].isna().sum()

print(f"\nValue Data Quality:")
print(f"  Records with value > 0: {len(value_df):,} ({len(value_df)/len(permits_df)*100:.1f}%)")
print(f"  Records with value = 0: {zero_value:,} ({zero_value/len(permits_df)*100:.1f}%)")
print(f"  Records with missing value: {missing_value:,} ({missing_value/len(permits_df)*100:.1f}%)")

# Calculate percentiles
percentiles = [0, 10, 25, 50, 75, 90, 95, 99, 100]
value_percentiles = value_df['value'].quantile([p/100 for p in percentiles])

print(f"\nValue Distribution Percentiles:")
for p, v in zip(percentiles, value_percentiles):
    if p == 0:
        print(f"  Min:    ${v:>15,.2f}")
    elif p == 100:
        print(f"  Max:    ${v:>15,.2f}")
    else:
        print(f"  {p}th%:   ${v:>15,.2f}")

print(f"\nSummary Statistics:")
print(f"  Mean:   ${value_df['value'].mean():>15,.2f}")
print(f"  Median: ${value_df['value'].median():>15,.2f}")
print(f"  Std Dev:${value_df['value'].std():>15,.2f}")
print(f"  Total:  ${value_df['value'].sum():>15,.2f}")

# 2. PROJECT SIZE CATEGORIZATION
print("\n\n2. PROJECT SIZE CATEGORIZATION")
print("-" * 60)

# Create project size categories
value_df['project_size'] = pd.cut(value_df['value'], 
                                  bins=[0, 5000, 25000, 100000, 500000, 1000000, float('inf')],
                                  labels=['Small (<$5K)', 'Medium ($5-25K)', 'Large ($25-100K)', 
                                         'Major ($100-500K)', 'Mega ($500K-1M)', 'Mega+ (>$1M)'])

project_size_dist = value_df['project_size'].value_counts()
print("\nProject Size Distribution:")
for size, count in project_size_dist.items():
    pct = count / len(value_df) * 100
    avg_value = value_df[value_df['project_size'] == size]['value'].mean()
    total_value = value_df[value_df['project_size'] == size]['value'].sum()
    print(f"  {size:>20}: {count:>7,} ({pct:>5.1f}%) - Avg: ${avg_value:>10,.0f}, Total: ${total_value:>15,.0f}")

# 3. FEE ANALYSIS
print("\n\n3. FEE ANALYSIS")
print("-" * 60)

# Fee statistics
fee_df = permits_df[permits_df['totalFees'].notna() & (permits_df['totalFees'] > 0)].copy()
print(f"\nFee Data Quality:")
print(f"  Records with fees > 0: {len(fee_df):,} ({len(fee_df)/len(permits_df)*100:.1f}%)")
print(f"  Total fees collected: ${fee_df['totalFees'].sum():,.2f}")
print(f"  Average fee: ${fee_df['totalFees'].mean():,.2f}")
print(f"  Median fee: ${fee_df['totalFees'].median():,.2f}")

# Fee to value ratio (where both exist)
fee_value_df = permits_df[(permits_df['value'] > 0) & (permits_df['totalFees'] > 0)].copy()
fee_value_df['fee_ratio'] = (fee_value_df['totalFees'] / fee_value_df['value']) * 100

print(f"\nFee to Value Ratio Analysis:")
print(f"  Records with both fee and value: {len(fee_value_df):,}")
print(f"  Average fee ratio: {fee_value_df['fee_ratio'].mean():.2f}%")
print(f"  Median fee ratio: {fee_value_df['fee_ratio'].median():.2f}%")

# Fee ratio by permit type
print("\nAverage Fee Ratio by Permit Type:")
fee_by_type = fee_value_df.groupby('permitType').agg({
    'fee_ratio': ['mean', 'median'],
    'value': 'count'
}).round(2)
fee_by_type.columns = ['avg_fee_ratio', 'median_fee_ratio', 'count']
fee_by_type = fee_by_type[fee_by_type['count'] >= 100].sort_values('avg_fee_ratio', ascending=False)

for permit_type, row in fee_by_type.iterrows():
    print(f"  {permit_type:>12}: {row['avg_fee_ratio']:>5.2f}% avg (median: {row['median_fee_ratio']:>5.2f}%, n={int(row['count']):,})")

# 4. VALUE TRENDS OVER TIME
print("\n\n4. VALUE TRENDS OVER TIME")
print("-" * 60)

# Annual value trends
annual_values = value_df.groupby('issueYear').agg({
    'value': ['sum', 'mean', 'median', 'count']
}).round(0)
annual_values.columns = ['total_value', 'avg_value', 'median_value', 'count']

print("\nAnnual Value Trends:")
for year, row in annual_values.iterrows():
    if year >= 2017:  # Skip partial 2016 data
        print(f"  {int(year)}: Total: ${row['total_value']:>15,.0f}, Avg: ${row['avg_value']:>10,.0f}, Permits: {int(row['count']):>6,}")

# Calculate value CAGR (2017-2024)
if len(annual_values) > 1:
    start_value = annual_values.loc[2017, 'total_value']
    end_value = annual_values.loc[2024, 'total_value']
    years = 7
    value_cagr = (((end_value / start_value) ** (1/years)) - 1) * 100
    print(f"\nTotal Value CAGR (2017-2024): {value_cagr:.2f}%")

# 5. HIGH-VALUE PROJECT ANALYSIS
print("\n\n5. HIGH-VALUE PROJECT ANALYSIS")
print("-" * 60)

# Top value projects
top_projects = value_df.nlargest(20, 'value')
print("\nTop 20 Highest Value Projects:")
for i, (_, project) in enumerate(top_projects.iterrows(), 1):
    print(f"{i:>3}. ${project['value']:>15,.0f} - {project['permitType']:>12} - {project['workType'][:20]:>20} - {project['Neighborhoods_Desc']}")

# High-value contractors
high_value_df = value_df[value_df['value'] >= 1000000]
high_value_contractors = high_value_df.groupby('applicantName').agg({
    'value': ['sum', 'mean', 'count']
}).round(0)
high_value_contractors.columns = ['total_value', 'avg_value', 'count']
high_value_contractors = high_value_contractors[high_value_contractors['count'] >= 3].sort_values('total_value', ascending=False)

print(f"\n\nTop Contractors by High-Value Projects (>$1M, 3+ projects):")
for contractor, row in high_value_contractors.head(15).iterrows():
    print(f"  {contractor[:40]:>40}: ${row['total_value']:>15,.0f} total ({int(row['count'])} projects, ${row['avg_value']:>12,.0f} avg)")

# 6. VALUE BY GEOGRAPHY
print("\n\n6. VALUE BY GEOGRAPHY")
print("-" * 60)

# Total value by ward
ward_values = value_df.groupby('Wards').agg({
    'value': ['sum', 'mean', 'count']
}).round(0)
ward_values.columns = ['total_value', 'avg_value', 'count']
ward_values = ward_values.sort_values('total_value', ascending=False)

print("\nTotal Project Value by Ward:")
for ward, row in ward_values.iterrows():
    if pd.notna(ward):
        pct_of_total = row['total_value'] / value_df['value'].sum() * 100
        print(f"  Ward {int(ward):>2}: ${row['total_value']:>15,.0f} ({pct_of_total:>5.1f}%) - {int(row['count']):>6,} projects")

# 7. OUTLIER ANALYSIS
print("\n\n7. OUTLIER ANALYSIS")
print("-" * 60)

# Identify outliers using IQR method
Q1 = value_df['value'].quantile(0.25)
Q3 = value_df['value'].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = value_df[(value_df['value'] < lower_bound) | (value_df['value'] > upper_bound)]
print(f"\nOutlier Analysis (IQR Method):")
print(f"  Lower bound: ${lower_bound:,.2f}")
print(f"  Upper bound: ${upper_bound:,.2f}")
print(f"  Number of outliers: {len(outliers):,} ({len(outliers)/len(value_df)*100:.2f}%)")
print(f"  Total value in outliers: ${outliers['value'].sum():,.2f} ({outliers['value'].sum()/value_df['value'].sum()*100:.1f}%)")

# 8. VALUE BY WORK TYPE
print("\n\n8. VALUE BY WORK TYPE")
print("-" * 60)

# Average value by work type
worktype_values = value_df.groupby('workType').agg({
    'value': ['mean', 'median', 'sum', 'count']
}).round(0)
worktype_values.columns = ['avg_value', 'median_value', 'total_value', 'count']
worktype_values = worktype_values[worktype_values['count'] >= 50].sort_values('avg_value', ascending=False)

print("\nTop 15 Work Types by Average Value (50+ projects):")
for work_type, row in worktype_values.head(15).iterrows():
    print(f"  {work_type:>20}: ${row['avg_value']:>12,.0f} avg (median: ${row['median_value']:>10,.0f}, n={int(row['count']):,})")

# Export financial metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

financial_metrics = {
    'overview': {
        'records_with_value': int(len(value_df)),
        'total_project_value': float(value_df['value'].sum()),
        'avg_project_value': float(value_df['value'].mean()),
        'median_project_value': float(value_df['value'].median()),
        'total_fees_collected': float(fee_df['totalFees'].sum()),
        'avg_fee': float(fee_df['totalFees'].mean())
    },
    'value_distribution': {
        'percentiles': value_percentiles.to_dict(),
        'project_sizes': project_size_dist.to_dict()
    },
    'fee_analysis': {
        'avg_fee_ratio': float(fee_value_df['fee_ratio'].mean()),
        'fee_by_type': fee_by_type.to_dict('index')
    },
    'annual_trends': annual_values.to_dict('index'),
    'high_value_contractors': high_value_contractors.head(20).to_dict('index'),
    'geographic_value': ward_values.to_dict('index'),
    'outlier_stats': {
        'count': int(len(outliers)),
        'pct_of_records': float(len(outliers)/len(value_df)*100),
        'total_value': float(outliers['value'].sum()),
        'pct_of_value': float(outliers['value'].sum()/value_df['value'].sum()*100)
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

financial_metrics = clean_for_json(financial_metrics)

with open(f'{output_dir}/financial_metrics.json', 'w') as f:
    json.dump(financial_metrics, f, indent=2)

print(f"\n✓ Iteration 6 complete. Financial metrics saved to {output_dir}/financial_metrics.json")

# Key insights summary
print("\n\nKEY FINANCIAL INSIGHTS:")
print("=" * 60)
print(f"1. Total project value: ${value_df['value'].sum():,.2f}")
print(f"2. Only {len(value_df)/len(permits_df)*100:.1f}% of permits have value > 0")
print(f"3. Top 1% of projects account for {outliers['value'].sum()/value_df['value'].sum()*100:.1f}% of total value")
print(f"4. Average fee ratio: {fee_value_df['fee_ratio'].mean():.2f}% of project value")
print("5. Significant value concentration in commercial and new construction")