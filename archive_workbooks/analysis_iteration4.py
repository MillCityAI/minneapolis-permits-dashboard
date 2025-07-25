#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 4: Geographic Intelligence
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
print("Minneapolis Permits Analysis - Iteration 4: Geographic Intelligence")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['issueYear'] = permits_df['issueDate'].dt.year

print(f"\nData loaded: {len(permits_df):,} permits")

# 1. NEIGHBORHOOD ANALYSIS
print("\n\n1. NEIGHBORHOOD ANALYSIS")
print("-" * 60)

# Neighborhood statistics
neighborhood_stats = permits_df['Neighborhoods_Desc'].value_counts(dropna=False)
print(f"\nUnique neighborhoods: {len(neighborhood_stats) - (1 if pd.isna(neighborhood_stats.index).any() else 0)}")
print(f"Records with missing neighborhood: {neighborhood_stats.get(np.nan, 0):,} ({neighborhood_stats.get(np.nan, 0)/len(permits_df)*100:.2f}%)")

print("\nTop 20 Neighborhoods by Permit Count:")
for i, (neighborhood, count) in enumerate(neighborhood_stats.head(20).items(), 1):
    if pd.notna(neighborhood):
        pct = count / len(permits_df) * 100
        print(f"{i:>3}. {neighborhood:>35}: {count:>7,} ({pct:>5.1f}%)")

# 2. WARD ANALYSIS
print("\n\n2. WARD ANALYSIS")
print("-" * 60)

ward_stats = permits_df['Wards'].value_counts(dropna=False).sort_index()
print("\nPermits by Ward:")
for ward, count in ward_stats.items():
    if pd.notna(ward):
        pct = count / len(permits_df) * 100
        print(f"  Ward {int(ward):>2}: {count:>7,} ({pct:>5.1f}%)")

# 3. GEOGRAPHIC GROWTH PATTERNS
print("\n\n3. GEOGRAPHIC GROWTH PATTERNS")
print("-" * 60)

# Calculate growth by neighborhood (2020-2024 vs 2017-2019)
recent_years = permits_df[permits_df['issueYear'].between(2020, 2024)]
baseline_years = permits_df[permits_df['issueYear'].between(2017, 2019)]

recent_neighborhood = recent_years['Neighborhoods_Desc'].value_counts()
baseline_neighborhood = baseline_years['Neighborhoods_Desc'].value_counts()

# Calculate growth rates
neighborhood_growth = pd.DataFrame({
    'recent': recent_neighborhood,
    'baseline': baseline_neighborhood
}).fillna(0)

neighborhood_growth['growth_rate'] = ((neighborhood_growth['recent'] - neighborhood_growth['baseline']) / 
                                     neighborhood_growth['baseline'] * 100).replace([np.inf, -np.inf], np.nan)

# Filter neighborhoods with sufficient baseline
significant_neighborhoods = neighborhood_growth[neighborhood_growth['baseline'] >= 100].copy()
significant_neighborhoods = significant_neighborhoods.sort_values('growth_rate', ascending=False)

print("\nFastest Growing Neighborhoods (100+ baseline permits):")
for neighborhood, row in significant_neighborhoods.head(10).iterrows():
    if pd.notna(row['growth_rate']):
        print(f"  {neighborhood:>35}: {row['growth_rate']:>+6.1f}% growth ({int(row['baseline'])} → {int(row['recent'])})")

print("\n\nDeclining Neighborhoods:")
for neighborhood, row in significant_neighborhoods.tail(10).iterrows():
    if pd.notna(row['growth_rate']) and row['growth_rate'] < 0:
        print(f"  {neighborhood:>35}: {row['growth_rate']:>+6.1f}% decline ({int(row['baseline'])} → {int(row['recent'])})")

# 4. PERMIT TYPE GEOGRAPHIC DISTRIBUTION
print("\n\n4. PERMIT TYPE GEOGRAPHIC DISTRIBUTION")
print("-" * 60)

# Top neighborhoods by permit type
for permit_type in ['Plumbing', 'Mechanical', 'Res', 'Commercial']:
    type_df = permits_df[permits_df['permitType'] == permit_type]
    type_neighborhoods = type_df['Neighborhoods_Desc'].value_counts().head(5)
    
    print(f"\n{permit_type} - Top 5 Neighborhoods:")
    for neighborhood, count in type_neighborhoods.items():
        pct = count / len(type_df) * 100
        print(f"  {neighborhood:>35}: {count:>6,} ({pct:>5.1f}% of {permit_type})")

# 5. GEOGRAPHIC CONCENTRATION ANALYSIS
print("\n\n5. GEOGRAPHIC CONCENTRATION ANALYSIS")
print("-" * 60)

# Calculate concentration metrics
total_neighborhoods = len(neighborhood_stats.dropna())
top_10_share = neighborhood_stats.head(10).sum() / len(permits_df) * 100
top_20_share = neighborhood_stats.head(20).sum() / len(permits_df) * 100

print(f"\nGeographic Concentration:")
print(f"  Top 10 neighborhoods: {top_10_share:.1f}% of all permits")
print(f"  Top 20 neighborhoods: {top_20_share:.1f}% of all permits")
print(f"  Bottom 50% neighborhoods: {100 - neighborhood_stats.head(int(total_neighborhoods/2)).sum() / len(permits_df) * 100:.1f}% of permits")

# 6. VALUE BY GEOGRAPHY
print("\n\n6. VALUE BY GEOGRAPHY")
print("-" * 60)

# Calculate average value by neighborhood
value_df = permits_df[permits_df['value'].notna() & (permits_df['value'] > 0)].copy()

neighborhood_value = value_df.groupby('Neighborhoods_Desc').agg({
    'value': ['mean', 'median', 'sum', 'count']
}).round(0)

neighborhood_value.columns = ['avg_value', 'median_value', 'total_value', 'count']
neighborhood_value = neighborhood_value[neighborhood_value['count'] >= 50]  # Min 50 permits
neighborhood_value = neighborhood_value.sort_values('avg_value', ascending=False)

print("\nHighest Average Project Value by Neighborhood (50+ permits):")
for neighborhood, row in neighborhood_value.head(10).iterrows():
    print(f"  {neighborhood:>35}: ${row['avg_value']:>10,.0f} avg (n={int(row['count']):,})")

print("\n\nLowest Average Project Value by Neighborhood (50+ permits):")
for neighborhood, row in neighborhood_value.tail(10).iterrows():
    print(f"  {neighborhood:>35}: ${row['avg_value']:>10,.0f} avg (n={int(row['count']):,})")

# 7. COORDINATE ANALYSIS
print("\n\n7. COORDINATE ANALYSIS")
print("-" * 60)

# Check coordinate data quality
coords_valid = permits_df[(permits_df['Latitude'] != 0) & (permits_df['Longitude'] != 0)].copy()
print(f"\nRecords with valid coordinates: {len(coords_valid):,} ({len(coords_valid)/len(permits_df)*100:.1f}%)")

if len(coords_valid) > 0:
    # Calculate geographic bounds
    lat_min, lat_max = coords_valid['Latitude'].min(), coords_valid['Latitude'].max()
    lon_min, lon_max = coords_valid['Longitude'].min(), coords_valid['Longitude'].max()
    
    print(f"\nGeographic Bounds:")
    print(f"  Latitude:  {lat_min:.6f} to {lat_max:.6f}")
    print(f"  Longitude: {lon_min:.6f} to {lon_max:.6f}")
    
    # Calculate center point
    lat_center = coords_valid['Latitude'].mean()
    lon_center = coords_valid['Longitude'].mean()
    print(f"\nGeographic Center:")
    print(f"  Latitude:  {lat_center:.6f}")
    print(f"  Longitude: {lon_center:.6f}")

# 8. NEIGHBORHOOD PERMIT MIX
print("\n\n8. NEIGHBORHOOD PERMIT MIX")
print("-" * 60)

# Analyze permit type mix for top neighborhoods
top_neighborhoods = neighborhood_stats.head(5).index.dropna()

for neighborhood in top_neighborhoods:
    neigh_df = permits_df[permits_df['Neighborhoods_Desc'] == neighborhood]
    permit_mix = neigh_df['permitType'].value_counts()
    
    print(f"\n{neighborhood} - Permit Type Mix:")
    total = len(neigh_df)
    for permit_type, count in permit_mix.head(5).items():
        pct = count / total * 100
        print(f"  {permit_type:>12}: {count:>6,} ({pct:>5.1f}%)")

# Export geographic metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

geographic_metrics = {
    'neighborhood_stats': {
        'unique_count': int(len(neighborhood_stats.dropna())),
        'missing_count': int(neighborhood_stats.get(np.nan, 0)),
        'top_20': neighborhood_stats.head(20).to_dict()
    },
    'ward_distribution': ward_stats.to_dict(),
    'growth_patterns': {
        'fastest_growing': significant_neighborhoods.head(10)['growth_rate'].to_dict(),
        'declining': significant_neighborhoods[significant_neighborhoods['growth_rate'] < 0].tail(10)['growth_rate'].to_dict()
    },
    'concentration': {
        'top_10_share': float(top_10_share),
        'top_20_share': float(top_20_share)
    },
    'value_by_neighborhood': {
        'highest_value': neighborhood_value.head(10)['avg_value'].to_dict(),
        'lowest_value': neighborhood_value.tail(10)['avg_value'].to_dict()
    },
    'coordinate_coverage': {
        'valid_coords': int(len(coords_valid)),
        'coverage_pct': float(len(coords_valid)/len(permits_df)*100)
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

geographic_metrics = clean_for_json(geographic_metrics)

with open(f'{output_dir}/geographic_metrics.json', 'w') as f:
    json.dump(geographic_metrics, f, indent=2)

print(f"\n✓ Iteration 4 complete. Geographic metrics saved to {output_dir}/geographic_metrics.json")

# Key insights summary
print("\n\nKEY GEOGRAPHIC INSIGHTS:")
print("=" * 60)
print(f"1. Top neighborhoods: {', '.join([str(n) for n in neighborhood_stats.head(3).index if pd.notna(n)])}")
print(f"2. Geographic concentration: Top 10 neighborhoods = {top_10_share:.1f}% of permits")
print(f"3. Fastest growing: {significant_neighborhoods.index[0] if len(significant_neighborhoods) > 0 else 'N/A'}")
print(f"4. Coordinate coverage: {len(coords_valid)/len(permits_df)*100:.1f}% have valid lat/lon")
print("5. Significant geographic variation in project values and permit types")