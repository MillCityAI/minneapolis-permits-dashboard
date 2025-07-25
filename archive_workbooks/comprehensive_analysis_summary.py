#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Comprehensive Summary
Consolidates insights from all analysis iterations
"""

import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

print("=" * 80)
print("MINNEAPOLIS PERMITS COMPREHENSIVE ANALYSIS SUMMARY")
print("=" * 80)
print(f"\nAnalysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("Data Source: CCS_Permits.csv")
print("Time Period: 2016-2025")

# Load all metrics files
output_dir = 'analysis_outputs'
metrics_files = {
    'Initial': 'initial_summary.json',
    'Temporal': 'temporal_metrics.json', 
    'Work/Occupancy': 'work_occupancy_metrics.json',
    'Text Mining': 'text_mining_metrics.json'
}

loaded_metrics = {}
for name, filename in metrics_files.items():
    filepath = os.path.join(output_dir, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r') as f:
            loaded_metrics[name] = json.load(f)
        print(f"✓ Loaded {name} metrics")
    else:
        print(f"✗ Missing {name} metrics")

# EXECUTIVE SUMMARY
print("\n\n" + "=" * 80)
print("EXECUTIVE SUMMARY")
print("=" * 80)

if 'Initial' in loaded_metrics:
    initial = loaded_metrics['Initial']
    print(f"\nDataset Overview:")
    print(f"  • Total Permits: {initial['total_records']:,}")
    print(f"  • Date Range: {initial['date_range']['start'][:10]} to {initial['date_range']['end'][:10]}")
    print(f"  • Unique Applicants: {initial['unique_applicants']:,}")
    print(f"  • Neighborhoods: {initial['unique_neighborhoods']}")
    print(f"  • Total Project Value: ${initial['total_value']:,.2f}")
    print(f"  • Total Fees Collected: ${initial['total_fees']:,.2f}")

# KEY INSIGHTS BY CATEGORY
print("\n\n" + "=" * 80)
print("KEY INSIGHTS BY CATEGORY")
print("=" * 80)

# 1. TEMPORAL INSIGHTS
print("\n1. TEMPORAL PATTERNS")
print("-" * 60)
if 'Temporal' in loaded_metrics:
    temporal = loaded_metrics['Temporal']
    print(f"  • Overall Growth: {temporal['cagr']:.1f}% CAGR")
    print(f"  • Busiest Months: {', '.join(temporal['summary']['busiest_months'])}")
    print(f"  • Slowest Months: {', '.join(temporal['summary']['slowest_months'])}")
    print(f"  • Business Day Concentration: {temporal['summary']['business_day_pct']:.1f}%")
    print(f"  • Recent Trend: {temporal['recent_trend']['direction']} ({temporal['recent_trend']['slope']:.2f} permits/day)")
    
    # Day of week insights
    dow = temporal['day_of_week']
    busiest_day = max(dow, key=dow.get)
    print(f"  • Busiest Day: {busiest_day} ({dow[busiest_day]:,} permits)")

# 2. WORK TYPE & OCCUPANCY INSIGHTS
print("\n\n2. WORK TYPE & OCCUPANCY PATTERNS")
print("-" * 60)
if 'Work/Occupancy' in loaded_metrics:
    work_occ = loaded_metrics['Work/Occupancy']
    print(f"  • Unique Work Types: {work_occ['work_types']['unique_count']}")
    print(f"  • Top Work Types: {', '.join(list(work_occ['work_types']['top_10'].keys())[:3])}")
    print(f"  • Unique Occupancy Types: {work_occ['occupancy_types']['unique_count']}")
    
    # Processing time insights
    if work_occ.get('processing_times'):
        longest = max(work_occ['processing_times'].items(), key=lambda x: x[1]['mean'])
        print(f"  • Longest Processing: {longest[0]} ({longest[1]['mean']:.1f} days average)")
    
    # Value insights
    if work_occ.get('value_analysis'):
        highest = max(work_occ['value_analysis'].items(), key=lambda x: x[1]['mean'])
        print(f"  • Highest Value Work: {highest[0]} (${highest[1]['mean']:,.0f} average)")

# 3. TEXT MINING INSIGHTS
print("\n\n3. COMMENTS & PROJECT COMPLEXITY")
print("-" * 60)
if 'Text Mining' in loaded_metrics:
    text = loaded_metrics['Text Mining']
    print(f"  • Records with Comments: {text['overview']['total_with_comments']:,}")
    print(f"  • Top Keywords: {', '.join(list(text['top_keywords'].keys())[:5])}")
    
    # Scope distribution
    if text.get('scope_distribution'):
        major_pct = text['scope_distribution'].get('Major', 0) / text['overview']['total_with_comments'] * 100
        print(f"  • Major Scope Projects: {text['scope_distribution'].get('Major', 0):,} ({major_pct:.1f}%)")
    
    # Emergency work
    if text.get('urgency_distribution'):
        emergency_pct = text['urgency_distribution'].get('Emergency', 0) / text['overview']['total_with_comments'] * 100
        print(f"  • Emergency Work: {text['urgency_distribution'].get('Emergency', 0):,} ({emergency_pct:.1f}%)")
    
    # Multi-trade
    if text.get('trade_analysis'):
        multi_trade = sum(v for k, v in text['trade_analysis']['trade_count_distribution'].items() if int(k) > 1)
        multi_pct = multi_trade / text['overview']['total_with_comments'] * 100
        print(f"  • Multi-trade Projects: {multi_trade:,} ({multi_pct:.1f}%)")

# MARKET OPPORTUNITIES
print("\n\n" + "=" * 80)
print("MARKET OPPORTUNITIES & SEGMENTS")
print("=" * 80)

print("\n1. HIGH-VOLUME SEGMENTS")
print("-" * 60)
print("  • Plumbing (143,220 permits) - Dominated by 'Res' work type")
print("  • Residential (96,696 permits) - Strong growth at 26.4% CAGR")
print("  • Mechanical (76,115 permits) - Peak season in October")

print("\n2. HIGH-VALUE SEGMENTS")
print("-" * 60)
print("  • New Construction - $3.75M average project value")
print("  • Commercial Remodels - $292K average value")
print("  • Foundation Work - $2.2M average value")

print("\n3. FAST-GROWING SEGMENTS")
print("-" * 60)
print("  • ComMFDRR - 128.7% CAGR (HVAC replacement in multi-family)")
print("  • ComNoFdBv - 46.5% CAGR (Plumbing without food/beverage)")
print("  • ComMin - 43.8% CAGR (Minor commercial work)")

print("\n4. SEASONAL OPPORTUNITIES")
print("-" * 60)
print("  • October Peak - Plan for 14.2% above average volume")
print("  • January Plumbing - 43.1% above average (winter pipe issues)")
print("  • Summer Lull - August-December are slowest months")

# DATA QUALITY NOTES
print("\n\n" + "=" * 80)
print("DATA QUALITY & LIMITATIONS")
print("=" * 80)
print("\n  • Missing completion dates: 11.07% of records")
print("  • Blank occupancy type: 22.4% of records")
print("  • 2016 data appears partial (only 2,587 permits)")
print("  • 2025 data is incomplete (through June only)")
print("  • Holiday analysis needs refinement")

# RECOMMENDATIONS FOR FURTHER ANALYSIS
print("\n\n" + "=" * 80)
print("RECOMMENDATIONS FOR FURTHER ANALYSIS")
print("=" * 80)
print("\n1. Deep dive into top 20 contractors by segment")
print("2. Geographic heat maps by permit type and value")
print("3. Predictive modeling for processing times")
print("4. Customer journey analysis (multiple permits per address)")
print("5. Failure/cancellation root cause analysis")
print("6. Market share analysis by contractor")
print("7. Web research on top contractors for business intelligence")

# Export comprehensive summary
summary_data = {
    'analysis_date': datetime.now().isoformat(),
    'data_source': 'CCS_Permits.csv',
    'key_metrics': {
        'total_permits': initial['total_records'] if 'Initial' in loaded_metrics else None,
        'date_range': initial['date_range'] if 'Initial' in loaded_metrics else None,
        'growth_rate': temporal['cagr'] if 'Temporal' in loaded_metrics else None,
        'business_day_concentration': temporal['summary']['business_day_pct'] if 'Temporal' in loaded_metrics else None
    },
    'top_segments': {
        'by_volume': ['Plumbing', 'Residential', 'Mechanical'],
        'by_value': ['New Construction', 'Commercial Remodels', 'Foundation Work'],
        'by_growth': ['ComMFDRR', 'ComNoFdBv', 'ComMin']
    },
    'seasonal_patterns': {
        'peak_months': temporal['summary']['busiest_months'] if 'Temporal' in loaded_metrics else None,
        'slow_months': temporal['summary']['slowest_months'] if 'Temporal' in loaded_metrics else None
    }
}

with open(f'{output_dir}/comprehensive_summary.json', 'w') as f:
    json.dump(summary_data, f, indent=2)

print(f"\n\n✓ Comprehensive summary saved to {output_dir}/comprehensive_summary.json")
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)