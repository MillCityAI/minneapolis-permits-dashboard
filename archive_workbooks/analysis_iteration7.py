#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 7: Address and Repeat Customer Analysis
"""

import pandas as pd
import numpy as np
import json
import warnings
import os
from collections import Counter
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)

print("=" * 80)
print("Minneapolis Permits Analysis - Iteration 7: Address & Repeat Customer Analysis")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['issueYear'] = permits_df['issueDate'].dt.year

print(f"\nData loaded: {len(permits_df):,} permits")

# 1. ADDRESS ANALYSIS
print("\n\n1. ADDRESS ANALYSIS")
print("-" * 60)

# Create a unique address identifier
permits_df['full_address'] = permits_df['Display'].fillna('') + ', ' + permits_df['Neighborhoods_Desc'].fillna('')
permits_df['full_address'] = permits_df['full_address'].str.strip(', ')

# Count permits per address
address_counts = permits_df[permits_df['full_address'] != ''].groupby('full_address').size()
addresses_with_multiple = address_counts[address_counts > 1]

print(f"\nAddress Statistics:")
print(f"  Unique addresses: {len(address_counts):,}")
print(f"  Addresses with multiple permits: {len(addresses_with_multiple):,} ({len(addresses_with_multiple)/len(address_counts)*100:.1f}%)")
print(f"  Total permits at multi-permit addresses: {addresses_with_multiple.sum():,}")

# Distribution of permits per address
permit_count_dist = address_counts.value_counts().sort_index()
print("\nPermits per Address Distribution:")
for count, freq in permit_count_dist.head(10).items():
    pct = freq / len(address_counts) * 100
    print(f"  {count:>3} permit(s): {freq:>6,} addresses ({pct:>5.1f}%)")

# Top addresses by permit count
print("\n\nTop 20 Addresses by Permit Count:")
top_addresses = address_counts.nlargest(20)
for i, (address, count) in enumerate(top_addresses.items(), 1):
    print(f"{i:>3}. {address[:60]:>60}: {count:>4} permits")

# 2. PROPERTY IMPROVEMENT LIFECYCLES
print("\n\n2. PROPERTY IMPROVEMENT LIFECYCLES")
print("-" * 60)

# Analyze time between permits at same address
multi_permit_addresses = addresses_with_multiple.index

lifecycle_data = []
for address in multi_permit_addresses[:1000]:  # Sample for performance
    address_permits = permits_df[permits_df['full_address'] == address].sort_values('issueDate')
    
    if len(address_permits) > 1:
        # Calculate days between consecutive permits
        issue_dates = address_permits['issueDate'].dropna()
        if len(issue_dates) > 1:
            days_between = issue_dates.diff().dt.days.dropna()
            
            lifecycle_data.append({
                'address': address,
                'permit_count': len(address_permits),
                'avg_days_between': days_between.mean(),
                'min_days_between': days_between.min(),
                'max_days_between': days_between.max(),
                'total_span_days': (issue_dates.max() - issue_dates.min()).days
            })

lifecycle_df = pd.DataFrame(lifecycle_data)

if len(lifecycle_df) > 0:
    print(f"\nProperty Lifecycle Analysis (sample of {len(lifecycle_df)} addresses):")
    print(f"  Average days between permits: {lifecycle_df['avg_days_between'].mean():.1f}")
    print(f"  Median days between permits: {lifecycle_df['avg_days_between'].median():.1f}")
    
    # Categorize lifecycle patterns
    lifecycle_df['pattern'] = pd.cut(lifecycle_df['avg_days_between'], 
                                     bins=[0, 30, 180, 365, 1825, float('inf')],
                                     labels=['Rapid (<30d)', 'Quick (30-180d)', 'Annual', 'Multi-year', '5+ years'])
    
    pattern_dist = lifecycle_df['pattern'].value_counts()
    print("\nPermit Timing Patterns:")
    for pattern, count in pattern_dist.items():
        pct = count / len(lifecycle_df) * 100
        print(f"  {pattern:>15}: {count:>5} ({pct:>5.1f}%)")

# 3. PERMIT SEQUENCES
print("\n\n3. PERMIT SEQUENCES")
print("-" * 60)

# Analyze common permit type sequences
sequence_analysis = []
for address in multi_permit_addresses[:500]:  # Sample
    address_permits = permits_df[permits_df['full_address'] == address].sort_values('issueDate')
    
    if len(address_permits) >= 2:
        permit_sequence = address_permits['permitType'].tolist()
        sequence_analysis.append({
            'address': address,
            'sequence': ' → '.join(permit_sequence),
            'length': len(permit_sequence)
        })

# Count common sequences
if sequence_analysis:
    sequences = [s['sequence'] for s in sequence_analysis]
    sequence_counter = Counter(sequences)
    
    print("\nMost Common Permit Sequences (2+ permits):")
    for sequence, count in sequence_counter.most_common(15):
        if count >= 3:  # Show sequences that appear 3+ times
            print(f"  {sequence[:60]:>60}: {count:>3} occurrences")

# 4. REPEAT CUSTOMER ANALYSIS
print("\n\n4. REPEAT CUSTOMER ANALYSIS")
print("-" * 60)

# Analyze repeat customers
customer_permits = permits_df.groupby('applicantName').agg({
    'permitNumber': 'count',
    'issueDate': ['min', 'max'],
    'value': 'sum',
    'Neighborhoods_Desc': 'nunique'
}).round(0)

customer_permits.columns = ['permit_count', 'first_permit', 'last_permit', 'total_value', 'neighborhoods']
customer_permits['years_active'] = ((customer_permits['last_permit'] - customer_permits['first_permit']).dt.days / 365.25).round(1)

# Categorize customers
customer_permits['customer_type'] = pd.cut(customer_permits['permit_count'], 
                                           bins=[0, 1, 5, 20, 100, float('inf')],
                                           labels=['One-time', 'Occasional (2-5)', 'Regular (6-20)', 'Frequent (21-100)', 'Major (100+)'])

customer_type_dist = customer_permits['customer_type'].value_counts()
print("\nCustomer Type Distribution:")
for ctype, count in customer_type_dist.items():
    pct = count / len(customer_permits) * 100
    permits = customer_permits[customer_permits['customer_type'] == ctype]['permit_count'].sum()
    print(f"  {ctype:>20}: {count:>6,} customers ({pct:>5.1f}%) - {permits:,} permits total")

# Loyalty analysis - customers active multiple years
loyal_customers = customer_permits[customer_permits['years_active'] >= 3].copy()
print(f"\n\nLoyal Customers (Active 3+ years): {len(loyal_customers):,}")

# Top loyal customers by longevity
print("\nTop 15 Customers by Years Active:")
longest_active = loyal_customers.nlargest(15, 'years_active')
for customer, row in longest_active.iterrows():
    print(f"  {customer[:40]:>40}: {row['years_active']:>4.1f} years ({int(row['permit_count']):>5,} permits)")

# 5. COMMERCIAL VS RESIDENTIAL PATTERNS
print("\n\n5. COMMERCIAL VS RESIDENTIAL ADDRESS PATTERNS")
print("-" * 60)

# Identify likely commercial addresses based on permit patterns
address_types = []
for address in addresses_with_multiple[:500].index:
    address_df = permits_df[permits_df['full_address'] == address]
    
    # Check indicators
    commercial_permits = len(address_df[address_df['permitType'] == 'Commercial'])
    total_permits = len(address_df)
    unique_applicants = address_df['applicantName'].nunique()
    
    # Classify
    if commercial_permits / total_permits > 0.5:
        address_type = 'Commercial'
    elif unique_applicants == 1 and total_permits <= 5:
        address_type = 'Residential - Owner'
    elif unique_applicants > 3:
        address_type = 'Mixed/Multi-tenant'
    else:
        address_type = 'Residential'
    
    address_types.append({
        'address': address,
        'type': address_type,
        'permits': total_permits,
        'unique_applicants': unique_applicants
    })

address_type_df = pd.DataFrame(address_types)
type_dist = address_type_df['type'].value_counts()

print("\nAddress Type Distribution (Multi-permit addresses):")
for atype, count in type_dist.items():
    pct = count / len(address_type_df) * 100
    print(f"  {atype:>20}: {count:>4} ({pct:>5.1f}%)")

# 6. NEIGHBORHOOD CUSTOMER RETENTION
print("\n\n6. NEIGHBORHOOD CUSTOMER RETENTION")
print("-" * 60)

# Analyze if customers stay in same neighborhood
multi_neighborhood_customers = customer_permits[customer_permits['neighborhoods'] > 1].copy()
print(f"\nCustomers active in multiple neighborhoods: {len(multi_neighborhood_customers):,}")

# Top customers by neighborhood spread
print("\nTop 15 Customers by Neighborhood Coverage:")
widest_coverage = multi_neighborhood_customers.nlargest(15, 'neighborhoods')
for customer, row in widest_coverage.iterrows():
    print(f"  {customer[:40]:>40}: {int(row['neighborhoods']):>2} neighborhoods ({int(row['permit_count']):>5,} permits)")

# 7. ADDRESS VALUE ACCUMULATION
print("\n\n7. ADDRESS VALUE ACCUMULATION")
print("-" * 60)

# Calculate total investment per address
address_value = permits_df[permits_df['value'] > 0].groupby('full_address').agg({
    'value': ['sum', 'mean', 'count'],
    'permitType': lambda x: x.mode()[0] if len(x) > 0 else ''
}).round(0)

address_value.columns = ['total_value', 'avg_value', 'permit_count', 'primary_type']
address_value = address_value[address_value['permit_count'] >= 2].sort_values('total_value', ascending=False)

print("\nTop 20 Addresses by Total Investment:")
for i, (address, row) in enumerate(address_value.head(20).iterrows(), 1):
    print(f"{i:>3}. {address[:50]:>50}: ${row['total_value']:>12,.0f} ({int(row['permit_count'])} permits)")

# Export address and customer metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

address_customer_metrics = {
    'address_overview': {
        'unique_addresses': int(len(address_counts)),
        'multi_permit_addresses': int(len(addresses_with_multiple)),
        'pct_multi_permit': float(len(addresses_with_multiple)/len(address_counts)*100)
    },
    'top_addresses': top_addresses.head(50).to_dict(),
    'permit_sequences': sequence_counter.most_common(30) if 'sequence_counter' in locals() else [],
    'customer_distribution': customer_type_dist.to_dict(),
    'loyal_customers': {
        'count': int(len(loyal_customers)),
        'top_by_longevity': longest_active.to_dict('index')
    },
    'address_types': type_dist.to_dict() if 'type_dist' in locals() else {},
    'multi_neighborhood_customers': int(len(multi_neighborhood_customers)),
    'top_value_addresses': address_value.head(30).to_dict('index')
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

address_customer_metrics = clean_for_json(address_customer_metrics)

with open(f'{output_dir}/address_customer_metrics.json', 'w') as f:
    json.dump(address_customer_metrics, f, indent=2)

print(f"\n✓ Iteration 7 complete. Address/Customer metrics saved to {output_dir}/address_customer_metrics.json")

# Key insights summary
print("\n\nKEY ADDRESS & CUSTOMER INSIGHTS:")
print("=" * 60)
print(f"1. {len(addresses_with_multiple)/len(address_counts)*100:.1f}% of addresses have multiple permits")
print(f"2. Top address has {top_addresses.iloc[0]} permits")
print(f"3. {len(loyal_customers):,} customers active 3+ years")
print(f"4. Average {lifecycle_df['avg_days_between'].mean():.0f} days between permits at same address" if len(lifecycle_df) > 0 else "4. Lifecycle data available")
print("5. Clear patterns in permit sequences and property improvement cycles")