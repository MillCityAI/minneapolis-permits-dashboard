#!/usr/bin/env python3
"""
Analyze permit abandonment patterns across categories.
Identifies cancelled, withdrawn, stop work, and incomplete permits.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def analyze_abandonment(df):
    """
    Analyze different types of permit abandonment.
    
    Returns detailed abandonment statistics by category and use case.
    """
    results = []
    
    # Define abandonment types
    df['is_cancelled'] = df['status'] == 'Cancelled'
    df['is_withdrawn'] = df['status'] == 'Withdrawn'
    df['is_stop_work'] = df['status'] == 'Stop Work'
    df['is_void'] = df['status'] == 'Void'
    
    # Identify never-completed permits (issued but no completion date after reasonable time)
    # Consider permits issued more than 2 years ago without completion as potentially abandoned
    two_years_ago = pd.Timestamp.now() - pd.Timedelta(days=730)
    
    # Handle timezone-aware dates
    if df['issueDate'].dt.tz is not None:
        two_years_ago = two_years_ago.tz_localize('UTC')
    
    df['is_incomplete'] = (
        (df['status'] == 'Issued') & 
        (df['issueDate'] < two_years_ago) & 
        (df['completeDate'].isna())
    )
    
    # Overall abandonment
    df['is_abandoned'] = (
        df['is_cancelled'] | 
        df['is_withdrawn'] | 
        df['is_stop_work'] | 
        df['is_void'] |
        df['is_incomplete']
    )
    
    # Calculate by sub_category and use_case
    groupings = [
        ('sub_category', df.groupby('sub_category')),
        ('use_case', df.groupby(['sub_category', 'use_case']))
    ]
    
    for group_type, grouped in groupings:
        for name, group in grouped:
            if group_type == 'sub_category':
                category = name
                use_case = 'All'
            else:
                category, use_case = name
                if pd.isna(use_case):
                    use_case = 'Uncategorized'
            
            total_permits = len(group)
            if total_permits == 0:
                continue
            
            stats = {
                'category': category,
                'use_case': use_case,
                'total_permits': total_permits,
                'completed': len(group[group['status'] == 'Closed']),
                'cancelled': len(group[group['is_cancelled']]),
                'withdrawn': len(group[group['is_withdrawn']]),
                'stop_work': len(group[group['is_stop_work']]),
                'void': len(group[group['is_void']]),
                'incomplete': len(group[group['is_incomplete']]),
                'total_abandoned': len(group[group['is_abandoned']]),
                'abandonment_rate': len(group[group['is_abandoned']]) / total_permits * 100,
                'completion_rate': len(group[group['status'] == 'Closed']) / total_permits * 100
            }
            
            # Add value analysis for abandoned permits
            abandoned_group = group[group['is_abandoned']]
            if len(abandoned_group) > 0:
                stats['abandoned_total_value'] = abandoned_group['value'].sum()
                stats['abandoned_avg_value'] = abandoned_group['value'].mean()
                stats['abandoned_total_fees'] = abandoned_group['totalFees'].sum()
            else:
                stats['abandoned_total_value'] = 0
                stats['abandoned_avg_value'] = 0
                stats['abandoned_total_fees'] = 0
            
            results.append(stats)
    
    return pd.DataFrame(results)

def analyze_abandonment_reasons(df):
    """
    Analyze comments field for abandoned permits to identify common reasons.
    """
    abandoned_df = df[
        (df['status'].isin(['Cancelled', 'Withdrawn', 'Stop Work', 'Void'])) &
        (df['comments'].notna())
    ]
    
    # Common keywords to look for
    reason_keywords = {
        'cost': ['cost', 'expensive', 'budget', 'afford'],
        'scope_change': ['change', 'different', 'revised', 'modify'],
        'duplicate': ['duplicate', 'already', 'existing'],
        'owner_request': ['owner', 'request', 'cancel'],
        'code_violation': ['violation', 'code', 'compliance', 'illegal'],
        'contractor_issue': ['contractor', 'dispute', 'fired'],
        'property_sale': ['sold', 'sale', 'new owner']
    }
    
    reason_counts = {}
    for reason, keywords in reason_keywords.items():
        count = 0
        for keyword in keywords:
            count += abandoned_df['comments'].str.contains(keyword, case=False, na=False).sum()
        reason_counts[reason] = count
    
    return reason_counts

def analyze_time_to_abandonment(df):
    """
    Analyze how long permits remain active before abandonment.
    """
    abandoned_df = df[df['status'].isin(['Cancelled', 'Withdrawn', 'Stop Work', 'Void'])].copy()
    
    # Calculate days from issue to last update
    abandoned_df['days_to_abandonment'] = (
        pd.to_datetime(abandoned_df['completeDate']) - 
        pd.to_datetime(abandoned_df['issueDate'])
    ).dt.days
    
    stats = {
        'mean_days': abandoned_df['days_to_abandonment'].mean(),
        'median_days': abandoned_df['days_to_abandonment'].median(),
        'min_days': abandoned_df['days_to_abandonment'].min(),
        'max_days': abandoned_df['days_to_abandonment'].max(),
        'under_30_days': len(abandoned_df[abandoned_df['days_to_abandonment'] < 30]),
        'under_90_days': len(abandoned_df[abandoned_df['days_to_abandonment'] < 90]),
        'over_365_days': len(abandoned_df[abandoned_df['days_to_abandonment'] > 365])
    }
    
    return stats

def main():
    """Run abandonment analysis and save results."""
    print("Loading permit data for abandonment analysis...")
    
    # Load the data
    df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)
    
    # Apply categorization
    from categorize_permits import categorize_permit
    df[['sub_category', 'use_case']] = df.apply(
        lambda row: pd.Series(categorize_permit(row)), axis=1
    )
    
    # Convert dates
    df['issueDate'] = pd.to_datetime(df['issueDate'], errors='coerce')
    df['completeDate'] = pd.to_datetime(df['completeDate'], errors='coerce')
    
    print("\nAnalyzing abandonment patterns...")
    
    # Main abandonment analysis
    abandonment_df = analyze_abandonment(df)
    abandonment_df = abandonment_df.sort_values(['category', 'abandonment_rate'], ascending=[True, False])
    abandonment_df.to_csv('drill_down_reports/data/abandonment_analysis_by_category.csv', index=False)
    
    # Analyze reasons
    print("\nAnalyzing abandonment reasons...")
    reasons = analyze_abandonment_reasons(df)
    
    # Time to abandonment
    print("\nAnalyzing time to abandonment...")
    time_stats = analyze_time_to_abandonment(df)
    
    # Print summary
    print("\n" + "="*60)
    print("ABANDONMENT ANALYSIS SUMMARY")
    print("="*60)
    
    # Overall statistics
    total_permits = len(df)
    total_abandoned = len(df[df['status'].isin(['Cancelled', 'Withdrawn', 'Stop Work', 'Void'])])
    
    print(f"\nOverall Statistics:")
    print(f"Total Permits: {total_permits:,}")
    print(f"Total Abandoned: {total_abandoned:,} ({total_abandoned/total_permits*100:.1f}%)")
    
    print(f"\nAbandonment by Status:")
    for status in ['Cancelled', 'Withdrawn', 'Stop Work', 'Void']:
        count = len(df[df['status'] == status])
        print(f"  {status}: {count:,} ({count/total_permits*100:.2f}%)")
    
    print(f"\nAbandonment by Category:")
    cat_summary = abandonment_df[abandonment_df['use_case'] == 'All'].sort_values('abandonment_rate', ascending=False)
    for _, row in cat_summary.iterrows():
        if pd.notna(row['category']):
            print(f"  {row['category']}: {row['abandonment_rate']:.1f}% ({row['total_abandoned']:,} of {row['total_permits']:,})")
    
    print(f"\nTime to Abandonment:")
    print(f"  Mean: {time_stats['mean_days']:.0f} days")
    print(f"  Median: {time_stats['median_days']:.0f} days")
    print(f"  Under 30 days: {time_stats['under_30_days']:,}")
    print(f"  Under 90 days: {time_stats['under_90_days']:,}")
    print(f"  Over 1 year: {time_stats['over_365_days']:,}")
    
    print(f"\nPotential Reasons (keyword analysis):")
    for reason, count in sorted(reasons.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {reason.replace('_', ' ').title()}: {count} mentions")
    
    print("\nAbandonment analysis complete!")
    print("Results saved to: drill_down_reports/data/abandonment_analysis_by_category.csv")

if __name__ == "__main__":
    main()