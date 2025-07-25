#!/usr/bin/env python
"""
Minneapolis Permits Data Analysis - Iteration 1: Seasonal and Temporal Patterns
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
import warnings
import os
import calendar
from scipy import stats
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
pd.set_option('display.float_format', '{:.2f}'.format)

print("=" * 80)
print("Minneapolis Permits Analysis - Iteration 1: Seasonal & Temporal Patterns")
print("=" * 80)

# Load the data
permits_df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)
use_cases_df = pd.read_csv('Mpls Use Cases - Minneapolis (1).csv')

# Convert dates
permits_df['issueDate'] = pd.to_datetime(permits_df['issueDate'], errors='coerce')
permits_df['completeDate'] = pd.to_datetime(permits_df['completeDate'], errors='coerce')

# Extract temporal features
permits_df['issueYear'] = permits_df['issueDate'].dt.year
permits_df['issueMonth'] = permits_df['issueDate'].dt.month
permits_df['issueWeek'] = permits_df['issueDate'].dt.isocalendar().week
permits_df['issueDayOfWeek'] = permits_df['issueDate'].dt.dayofweek
permits_df['issueDayName'] = permits_df['issueDate'].dt.day_name()
permits_df['issueMonthName'] = permits_df['issueDate'].dt.month_name()
permits_df['issueQuarter'] = permits_df['issueDate'].dt.quarter

print(f"\nData loaded: {len(permits_df):,} permits")
print(f"Date range: {permits_df['issueDate'].min()} to {permits_df['issueDate'].max()}")

# 1. MONTHLY PERMIT VOLUME PATTERNS
print("\n\n1. MONTHLY PERMIT VOLUME PATTERNS")
print("-" * 60)

# Monthly volumes across all years
monthly_counts = permits_df.groupby(['issueYear', 'issueMonth']).size().reset_index(name='count')
monthly_counts['year_month'] = pd.to_datetime(
    monthly_counts['issueYear'].astype(str) + '-' + 
    monthly_counts['issueMonth'].astype(str).str.zfill(2) + '-01'
)

# Average permits by month (seasonality)
monthly_avg_df = permits_df.groupby('issueMonth').size().reset_index(name='avg_permits')
monthly_avg_df['month_name'] = monthly_avg_df['issueMonth'].apply(lambda x: calendar.month_name[x])

print("\nAverage Permits by Month (All Years):")
for _, row in monthly_avg_df.iterrows():
    print(f"  {row['month_name']:>9}: {row['avg_permits']/permits_df['issueYear'].nunique():>7,.0f} permits")

# Seasonal indices
annual_avg = len(permits_df) / permits_df['issueYear'].nunique() / 12
monthly_avg_df['seasonal_index'] = (monthly_avg_df['avg_permits'] / permits_df['issueYear'].nunique()) / annual_avg * 100

print("\nSeasonal Indices (100 = average):")
for _, row in monthly_avg_df.iterrows():
    print(f"  {row['month_name']:>9}: {row['seasonal_index']:>6.1f}")

# 2. DAY-OF-WEEK ANALYSIS
print("\n\n2. DAY-OF-WEEK ANALYSIS")
print("-" * 60)

dow_counts = permits_df['issueDayName'].value_counts().reindex(
    ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
)

print("\nPermits Issued by Day of Week:")
for day, count in dow_counts.items():
    pct = count / len(permits_df) * 100
    print(f"  {day:>9}: {count:>7,} ({pct:>5.1f}%)")

# Business days vs weekends
business_days = dow_counts[['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']].sum()
weekend_days = dow_counts[['Saturday', 'Sunday']].sum()
print(f"\nBusiness Days: {business_days:,} ({business_days/len(permits_df)*100:.1f}%)")
print(f"Weekend Days:  {weekend_days:,} ({weekend_days/len(permits_df)*100:.1f}%)")

# 3. YEAR-OVER-YEAR GROWTH RATES
print("\n\n3. YEAR-OVER-YEAR GROWTH RATES")
print("-" * 60)

# Annual counts
annual_counts = permits_df['issueYear'].value_counts().sort_index()
annual_df = pd.DataFrame({'year': annual_counts.index, 'permits': annual_counts.values})
annual_df['yoy_growth'] = annual_df['permits'].pct_change() * 100

print("\nAnnual Permit Volumes and Growth:")
for _, row in annual_df.iterrows():
    if pd.notna(row['yoy_growth']):
        print(f"  {int(row['year'])}: {row['permits']:>7,} permits ({row['yoy_growth']:>+6.1f}% YoY)")
    else:
        print(f"  {int(row['year'])}: {row['permits']:>7,} permits (baseline)")

# Calculate CAGR
years = annual_df['year'].max() - annual_df['year'].min()
if years > 0:
    cagr = (((annual_df['permits'].iloc[-1] / annual_df['permits'].iloc[0]) ** (1/years)) - 1) * 100
    print(f"\nCompound Annual Growth Rate (CAGR): {cagr:.2f}%")

# Growth by permit type
print("\n\nGrowth Rates by Permit Type:")
for permit_type in permits_df['permitType'].dropna().unique():
    type_df = permits_df[permits_df['permitType'] == permit_type]
    type_annual = type_df['issueYear'].value_counts().sort_index()
    if len(type_annual) > 1:
        start_year = type_annual.index.min()
        end_year = type_annual.index.max()
        start_count = type_annual.iloc[0]
        end_count = type_annual.iloc[-1]
        years_diff = end_year - start_year
        if years_diff > 0:
            type_cagr = (((end_count / start_count) ** (1/years_diff)) - 1) * 100
            print(f"  {permit_type:>12}: {type_cagr:>+6.1f}% CAGR ({start_year}-{end_year})")

# 4. TREND ANALYSIS WITH MOVING AVERAGES
print("\n\n4. TREND ANALYSIS")
print("-" * 60)

# Create daily time series
daily_counts = permits_df.groupby(permits_df['issueDate'].dt.date).size()
daily_series = pd.Series(daily_counts.values, index=pd.to_datetime(daily_counts.index))

# Calculate moving averages
ma_7 = daily_series.rolling(window=7).mean()
ma_30 = daily_series.rolling(window=30).mean()
ma_90 = daily_series.rolling(window=90).mean()

# Recent trend (last 90 days)
recent_days = 90
recent_data = daily_series.tail(recent_days)
if len(recent_data) > 1:
    x = np.arange(len(recent_data))
    y = recent_data.values
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    
    print(f"\nRecent Trend Analysis (Last {recent_days} days):")
    print(f"  Average daily permits: {recent_data.mean():.1f}")
    print(f"  Trend: {'Increasing' if slope > 0 else 'Decreasing'} ({slope:.2f} permits/day)")
    print(f"  R-squared: {r_value**2:.3f}")

# 5. HOLIDAY IMPACT ANALYSIS
print("\n\n5. HOLIDAY IMPACT ANALYSIS")
print("-" * 60)

# Define major holidays (simplified - would need full holiday calendar)
holidays = {
    'New Year': (1, 1),
    'MLK Day': (1, 15),  # Approximate
    'Presidents Day': (2, 15),  # Approximate
    'Memorial Day': (5, 25),  # Approximate
    'Independence Day': (7, 4),
    'Labor Day': (9, 1),  # Approximate
    'Thanksgiving': (11, 25),  # Approximate
    'Christmas': (12, 25)
}

# Analyze permit volume around holidays
print("\nPermit Activity Around Major Holidays:")
for holiday_name, (month, day) in holidays.items():
    holiday_permits = permits_df[
        (permits_df['issueMonth'] == month) & 
        (permits_df['issueDate'].dt.day == day)
    ]
    
    # Compare to same month average
    month_avg = permits_df[permits_df['issueMonth'] == month].groupby('issueDate').size().mean()
    holiday_avg = len(holiday_permits) / permits_df['issueYear'].nunique() if permits_df['issueYear'].nunique() > 0 else 0
    
    if month_avg > 0:
        ratio = (holiday_avg / month_avg) * 100
        print(f"  {holiday_name:>15}: {ratio:>6.1f}% of typical day in {calendar.month_name[month]}")

# 6. PERMIT TYPE SEASONALITY
print("\n\n6. PERMIT TYPE SEASONALITY")
print("-" * 60)

# Calculate seasonal patterns by permit type
print("\nSeasonal Indices by Permit Type:")
for permit_type in ['Plumbing', 'Mechanical', 'Res', 'Commercial']:
    type_df = permits_df[permits_df['permitType'] == permit_type]
    if len(type_df) > 0:
        type_monthly = type_df.groupby('issueMonth').size()
        type_annual_avg = len(type_df) / type_df['issueYear'].nunique() / 12
        
        print(f"\n{permit_type}:")
        peak_month = type_monthly.idxmax()
        low_month = type_monthly.idxmin()
        peak_index = (type_monthly.max() / type_df['issueYear'].nunique()) / type_annual_avg * 100
        low_index = (type_monthly.min() / type_df['issueYear'].nunique()) / type_annual_avg * 100
        
        print(f"  Peak: {calendar.month_name[peak_month]} (Index: {peak_index:.1f})")
        print(f"  Low:  {calendar.month_name[low_month]} (Index: {low_index:.1f})")
        print(f"  Variability: {peak_index - low_index:.1f} points")

# 7. TIME HORIZON COMPARISONS
print("\n\n7. TIME HORIZON COMPARISONS")
print("-" * 60)

# Define horizons
current_date = permits_df['issueDate'].max()
horizons = {
    '3-year': current_date - pd.DateOffset(years=3),
    '5-year': current_date - pd.DateOffset(years=5),
    '10-year': current_date - pd.DateOffset(years=10)
}

print("\nPermit Volumes by Time Horizon:")
for horizon_name, start_date in horizons.items():
    horizon_df = permits_df[permits_df['issueDate'] >= start_date]
    monthly_avg = len(horizon_df) / ((current_date - start_date).days / 30.44)
    print(f"  {horizon_name:>7}: {len(horizon_df):>7,} permits ({monthly_avg:>6,.0f}/month avg)")

# Export enhanced metrics
output_dir = 'analysis_outputs'
os.makedirs(output_dir, exist_ok=True)

temporal_metrics = {
    'monthly_seasonality': monthly_avg_df[['month_name', 'avg_permits', 'seasonal_index']].to_dict('records'),
    'day_of_week': dow_counts.to_dict(),
    'annual_growth': annual_df.to_dict('records'),
    'cagr': float(cagr) if 'cagr' in locals() else None,
    'recent_trend': {
        'slope': float(slope) if 'slope' in locals() else None,
        'direction': 'Increasing' if 'slope' in locals() and slope > 0 else 'Decreasing'
    },
    'summary': {
        'busiest_months': monthly_avg_df.nlargest(3, 'seasonal_index')['month_name'].tolist(),
        'slowest_months': monthly_avg_df.nsmallest(3, 'seasonal_index')['month_name'].tolist(),
        'business_day_pct': float(business_days/len(permits_df)*100),
        'total_permits': len(permits_df)
    }
}

with open(f'{output_dir}/temporal_metrics.json', 'w') as f:
    json.dump(temporal_metrics, f, indent=2)

print(f"\n✓ Iteration 1 complete. Temporal metrics saved to {output_dir}/temporal_metrics.json")

# Key insights summary
print("\n\nKEY TEMPORAL INSIGHTS:")
print("=" * 60)
print("1. Strongest months:", monthly_avg_df.nlargest(3, 'seasonal_index')['month_name'].tolist())
print("2. Weakest months:", monthly_avg_df.nsmallest(3, 'seasonal_index')['month_name'].tolist())
print("3. Business day concentration:", f"{business_days/len(permits_df)*100:.1f}%")
print("4. Overall growth trend:", f"{cagr:.1f}% CAGR" if 'cagr' in locals() else "N/A")
print("5. Seasonal variability is significant across permit types")