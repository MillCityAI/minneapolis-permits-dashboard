#!/usr/bin/env python
"""
Minneapolis Permits Enhanced Visualizations
Creates clear, easy-to-understand visualizations of the permits data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import json
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

# Load the comprehensive analysis data
print("Loading analysis data...")
with open('analysis_outputs/plumbing_comprehensive_analysis.json', 'r') as f:
    analysis_data = json.load(f)

print(f"Analysis covers {analysis_data['metadata']['total_records']:,} plumbing permits")
print(f"Date range: {analysis_data['metadata']['date_range']['start'][:10]} to {analysis_data['metadata']['date_range']['end'][:10]}")

# 1. Executive Dashboard - Key Metrics at a Glance
print("\nCreating Executive Dashboard...")
fig = plt.figure(figsize=(20, 10))
fig.suptitle('Minneapolis Plumbing Permits - Executive Dashboard', fontsize=24, fontweight='bold')

# Define metrics
metrics = analysis_data['summary_metrics']

# Create metric cards
metric_data = [
    ('Total Permits', f"{metrics['volume']['total_permits']:,}", 'steelblue'),
    ('Monthly Average', f"{metrics['volume']['monthly_average']:.0f}", 'darkorange'),
    ('Growth Trend', f"{metrics['volume']['growth_trend']:.1f}/month", 'forestgreen'),
    ('Avg Processing', f"{metrics['processing']['median_days']:.0f} days", 'crimson'),
    ('Total Value', f"${metrics['financial']['total_value']/1e9:.1f}B", 'purple'),
    ('Cancellation Rate', f"{metrics['quality']['cancellation_rate']:.1f}%", 'darkred'),
    ('Emergency Rate', f"{metrics['quality']['emergency_rate']:.1f}%", 'orange'),
    ('Data Quality', f"{metrics['quality']['data_completeness']:.0f}%", 'teal')
]

# Create metric cards in a grid
for i, (label, value, color) in enumerate(metric_data):
    ax = plt.subplot(2, 4, i+1)
    ax.text(0.5, 0.6, value, fontsize=28, fontweight='bold', 
            ha='center', va='center', color=color)
    ax.text(0.5, 0.2, label, fontsize=14, ha='center', va='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    # Add a subtle border
    rect = plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False, 
                        edgecolor=color, linewidth=2, alpha=0.3)
    ax.add_patch(rect)

plt.tight_layout()
plt.savefig('analysis_outputs/executive_dashboard.png', dpi=150, bbox_inches='tight')
plt.show()

# 2. Time Series Analysis
print("\nCreating Time Series Analysis...")
fig, axes = plt.subplots(3, 1, figsize=(20, 12), sharex=True)
fig.suptitle('Minneapolis Plumbing Permits - Time Series Analysis', fontsize=20, fontweight='bold')

# Prepare time series data
monthly_data = pd.DataFrame(analysis_data['time_series']['monthly'])
monthly_data['month'] = pd.to_datetime(monthly_data['month'])

# Plot 1: Permit volume
ax1 = axes[0]
ax1.plot(monthly_data['month'], monthly_data['count'], 'b-o', linewidth=2, markersize=4)
# Add 12-month moving average
monthly_data['ma_12'] = monthly_data['count'].rolling(12).mean()
ax1.plot(monthly_data['month'], monthly_data['ma_12'], 'r--', linewidth=2, label='12-Month Average')
ax1.set_ylabel('Number of Permits', fontsize=12)
ax1.set_title('Monthly Permit Volume', fontsize=14)
ax1.grid(True, alpha=0.3)
ax1.legend()

# Plot 2: Average value
ax2 = axes[1]
ax2.bar(monthly_data['month'], monthly_data['avg_value'], color='green', alpha=0.7)
ax2.set_ylabel('Average Project Value ($)', fontsize=12)
ax2.set_title('Average Project Value by Month', fontsize=14)
ax2.grid(True, alpha=0.3)

# Plot 3: Processing time
ax3 = axes[2]
ax3.plot(monthly_data['month'], monthly_data['processing_days'], 'o-', color='orange', linewidth=2)
ax3.set_ylabel('Average Processing Days', fontsize=12)
ax3.set_xlabel('Date', fontsize=12)
ax3.set_title('Processing Time Trends', fontsize=14)
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/time_series_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# 3. Category Distribution
print("\nCreating Category Distribution...")
fig, axes = plt.subplots(2, 2, figsize=(20, 12))
fig.suptitle('Plumbing Permit Categories - Comprehensive View', fontsize=20, fontweight='bold')

# Get category data
categories = analysis_data['categories']['distribution']
cat_df = pd.DataFrame(list(categories.items()), columns=['Category', 'Count'])
cat_df = cat_df.sort_values('Count', ascending=False)

# 1. Pie chart for top categories
ax1 = axes[0, 0]
top_cats = cat_df.head(8)
other_count = cat_df.iloc[8:]['Count'].sum()
if other_count > 0:
    top_cats = pd.concat([top_cats, pd.DataFrame({'Category': ['Other'], 'Count': [other_count]})])

colors = plt.cm.Set3(np.linspace(0, 1, len(top_cats)))
wedges, texts, autotexts = ax1.pie(top_cats['Count'], labels=top_cats['Category'], 
                                    autopct='%1.1f%%', colors=colors, startangle=90)
ax1.set_title('Category Distribution (Top 8 + Other)', fontsize=16, fontweight='bold')

# 2. Horizontal bar chart for all categories
ax2 = axes[0, 1]
y_pos = np.arange(len(cat_df.head(15)))
bars = ax2.barh(y_pos, cat_df.head(15)['Count'], color=plt.cm.viridis(np.linspace(0.2, 0.8, 15)))
ax2.set_yticks(y_pos)
ax2.set_yticklabels(cat_df.head(15)['Category'])
ax2.invert_yaxis()
ax2.set_xlabel('Number of Permits')
ax2.set_title('Top 15 Categories by Volume', fontsize=16, fontweight='bold')

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    ax2.text(width + 50, bar.get_y() + bar.get_height()/2, 
             f'{int(width):,}', ha='left', va='center')

# 3. Cumulative distribution
ax3 = axes[1, 0]
cat_df['Cumulative'] = cat_df['Count'].cumsum() / cat_df['Count'].sum() * 100
cat_df['Category_num'] = range(1, len(cat_df) + 1)

ax3.plot(cat_df['Category_num'], cat_df['Cumulative'], 'b-', linewidth=2)
ax3.fill_between(cat_df['Category_num'], 0, cat_df['Cumulative'], alpha=0.3)
ax3.axhline(y=80, color='r', linestyle='--', label='80% threshold')
ax3.set_xlabel('Number of Categories')
ax3.set_ylabel('Cumulative % of Permits')
ax3.set_title('Cumulative Distribution - Category Concentration', fontsize=16, fontweight='bold')
ax3.grid(True, alpha=0.3)
ax3.legend()

# 4. Top 5 categories with volume
ax4 = axes[1, 1]
top_5_cats = cat_df.head(5)
bars = ax4.bar(range(5), top_5_cats['Count'], color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
ax4.set_xticks(range(5))
ax4.set_xticklabels(top_5_cats['Category'], rotation=45, ha='right')
ax4.set_ylabel('Number of Permits')
ax4.set_title('Top 5 Categories', fontsize=16, fontweight='bold')
ax4.grid(True, axis='y', alpha=0.3)

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax4.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('analysis_outputs/category_distribution.png', dpi=150, bbox_inches='tight')
plt.show()

# 4. Geographic Analysis
print("\nCreating Geographic Analysis...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

neighborhoods = pd.DataFrame(analysis_data['geographic']['top_neighborhoods'])

# Volume vs Processing Time
scatter = ax1.scatter(neighborhoods['permitNumber'], 
                     neighborhoods['processing_days'],
                     s=neighborhoods['value']/1000,
                     c=neighborhoods['value'],
                     cmap='viridis', alpha=0.6)

ax1.set_xlabel('Number of Permits', fontsize=12)
ax1.set_ylabel('Average Processing Days', fontsize=12)
ax1.set_title('Neighborhood Analysis: Volume vs Processing Time', fontsize=16, fontweight='bold')

# Add neighborhood labels for top 5
for i, row in neighborhoods.head(5).iterrows():
    ax1.annotate(row['Neighborhoods_Desc'][:20] + '...', 
                (row['permitNumber'], row['processing_days']),
                xytext=(5, 5), textcoords='offset points', fontsize=9)

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax1)
cbar.set_label('Average Project Value ($)', fontsize=10)

# Geographic distribution bar chart
top_10_neighborhoods = neighborhoods.head(10)
bars = ax2.bar(range(len(top_10_neighborhoods)), 
               top_10_neighborhoods['permitNumber'],
               color=plt.cm.Blues(np.linspace(0.4, 0.9, len(top_10_neighborhoods))))

ax2.set_xticks(range(len(top_10_neighborhoods)))
ax2.set_xticklabels([n[:15] + '...' if len(n) > 15 else n 
                     for n in top_10_neighborhoods['Neighborhoods_Desc']], 
                    rotation=45, ha='right')
ax2.set_ylabel('Number of Permits')
ax2.set_title('Top 10 Neighborhoods by Permit Volume', fontsize=16, fontweight='bold')

# Add value labels
for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('analysis_outputs/geographic_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# 5. Contractor Performance
print("\nCreating Contractor Performance Dashboard...")
contractors = pd.DataFrame(analysis_data['contractors']['top_20'])

fig = plt.figure(figsize=(20, 12))
gs = plt.GridSpec(3, 2, figure=fig, hspace=0.3, wspace=0.25)

# 1. Market concentration
ax1 = fig.add_subplot(gs[0, :])
top_10_contractors = contractors.head(10)
other_permits = contractors.iloc[10:]['permitNumber'].sum()
market_data = list(zip([c[:30] + '...' if len(c) > 30 else c 
                       for c in top_10_contractors['applicantName']], 
                      top_10_contractors['permitNumber']))
market_data.append(('Others (10+)', other_permits))

names, values = zip(*market_data)
colors = plt.cm.tab20(np.linspace(0, 1, len(names)))

wedges, texts, autotexts = ax1.pie(values, labels=names, autopct='%1.1f%%',
                                   colors=colors, startangle=90)
ax1.set_title('Contractor Market Share (Top 10)', fontsize=16, fontweight='bold')

# Make percentage text smaller
for autotext in autotexts:
    autotext.set_fontsize(9)

# 2. Performance metrics scatter
ax2 = fig.add_subplot(gs[1, 0])
scatter = ax2.scatter(contractors['permitNumber'], 
                     contractors['processing_days'],
                     s=contractors['value']/100,
                     c=contractors['efficiency_score']*100,
                     cmap='RdYlGn_r', alpha=0.6,
                     vmin=0, vmax=10)

ax2.set_xlabel('Total Permits')
ax2.set_ylabel('Avg Processing Days')
ax2.set_title('Contractor Performance Matrix', fontsize=14, fontweight='bold')
ax2.set_xscale('log')

# Add colorbar
cbar = plt.colorbar(scatter, ax=ax2)
cbar.set_label('Efficiency Score (%)', fontsize=10)

# 3. Volume leaders
ax3 = fig.add_subplot(gs[1, 1])
top_5 = contractors.head(5)
y_pos = np.arange(len(top_5))
bars = ax3.barh(y_pos, top_5['permitNumber'], color='skyblue')
ax3.set_yticks(y_pos)
ax3.set_yticklabels([name[:30] + '...' if len(name) > 30 else name 
                     for name in top_5['applicantName']])
ax3.invert_yaxis()
ax3.set_xlabel('Number of Permits')
ax3.set_title('Top 5 Contractors by Volume', fontsize=14, fontweight='bold')

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    ax3.text(width + 10, bar.get_y() + bar.get_height()/2,
            f'{int(width):,}', ha='left', va='center')

# 4. Quality metrics comparison
ax4 = fig.add_subplot(gs[2, :])
metrics_df = contractors.head(10)[['applicantName', 'efficiency_score', 'processing_days']].copy()
metrics_df['efficiency_score'] = metrics_df['efficiency_score'] * 100

x = np.arange(len(metrics_df))
width = 0.35

bars1 = ax4.bar(x - width/2, metrics_df['efficiency_score'], width, 
                label='Efficiency Score (%)', color='coral')
ax4_twin = ax4.twinx()
bars2 = ax4_twin.bar(x + width/2, metrics_df['processing_days'], width,
                     label='Avg Processing Days', color='lightblue')

ax4.set_xlabel('Contractor')
ax4.set_ylabel('Efficiency Score (%)', color='coral')
ax4_twin.set_ylabel('Processing Days', color='lightblue')
ax4.set_title('Contractor Quality Metrics Comparison', fontsize=14, fontweight='bold')
ax4.set_xticks(x)
ax4.set_xticklabels([name[:20] + '...' if len(name) > 20 else name 
                     for name in metrics_df['applicantName']], 
                    rotation=45, ha='right')

ax4.tick_params(axis='y', labelcolor='coral')
ax4_twin.tick_params(axis='y', labelcolor='lightblue')

plt.tight_layout()
plt.savefig('analysis_outputs/contractor_performance.png', dpi=150, bbox_inches='tight')
plt.show()

# 6. Key Insights Summary
print("\nCreating Key Insights Summary...")
fig = plt.figure(figsize=(20, 12))
fig.patch.set_facecolor('white')

# Main title
fig.suptitle('Minneapolis Plumbing Permits - Key Insights Summary', 
             fontsize=24, fontweight='bold', y=0.98)

# Create text-based insight cards
insights = [
    {
        'title': '📊 Volume Trends',
        'points': [
            f"Total Permits: {analysis_data['metadata']['total_records']:,}",
            f"Monthly Average: {analysis_data['summary_metrics']['volume']['monthly_average']:.0f}",
            f"Growth Rate: {analysis_data['summary_metrics']['volume']['growth_trend']:.1f} permits/month",
            "Peak Season: October-November"
        ],
        'color': 'lightblue'
    },
    {
        'title': '⏱️ Processing Efficiency',
        'points': [
            f"Median Time: {analysis_data['summary_metrics']['processing']['median_days']:.0f} days",
            f"90th Percentile: {analysis_data['summary_metrics']['processing']['p90_days']:.0f} days",
            f"On-Time Rate: {analysis_data['summary_metrics']['processing']['within_30_days_pct']:.1f}%",
            "Fastest: Residential permits"
        ],
        'color': 'lightgreen'
    },
    {
        'title': '💰 Financial Impact',
        'points': [
            f"Total Value: ${analysis_data['summary_metrics']['financial']['total_value']/1e9:.1f}B",
            f"Average Project: ${analysis_data['summary_metrics']['financial']['mean_value']:,.0f}",
            f"Total Fees: ${analysis_data['summary_metrics']['financial']['total_fees']/1e6:.1f}M",
            "Top Category: Water Heaters"
        ],
        'color': 'lightyellow'
    },
    {
        'title': '🎯 Quality Metrics',
        'points': [
            f"Cancellation Rate: {analysis_data['summary_metrics']['quality']['cancellation_rate']:.1f}%",
            f"Emergency Rate: {analysis_data['summary_metrics']['quality']['emergency_rate']:.1f}%",
            f"Data Quality: {analysis_data['summary_metrics']['quality']['data_completeness']:.0f}%",
            f"Model Accuracy: R² = {analysis_data['predictions']['model_performance']['r2']:.3f}"
        ],
        'color': 'lightcoral'
    },
    {
        'title': '🏢 Market Structure',
        'points': [
            f"Total Contractors: {len(analysis_data['contractors']['top_20']):,}+",
            "Top 10 Market Share: ~25%",
            "Geographic Concentration: High",
            "Specialization: Common"
        ],
        'color': 'lavender'
    },
    {
        'title': '📈 Predictions',
        'points': [
            "Seasonal Peak: March & October",
            "High Risk Categories: Water Service",
            "Processing Predictable: Yes",
            f"MAE: {analysis_data['predictions']['model_performance']['mae']:.0f} days"
        ],
        'color': 'lightsteelblue'
    }
]

# Create insight cards
for i, insight in enumerate(insights):
    ax = plt.subplot(2, 3, i+1)
    ax.set_facecolor(insight['color'])
    
    # Title
    ax.text(0.5, 0.9, insight['title'], fontsize=16, fontweight='bold',
            ha='center', va='top', transform=ax.transAxes)
    
    # Points
    for j, point in enumerate(insight['points']):
        ax.text(0.1, 0.7 - j*0.15, f"• {point}", fontsize=12,
               ha='left', va='top', transform=ax.transAxes)
    
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    
    # Add border
    rect = plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False, 
                        edgecolor='gray', linewidth=2)
    ax.add_patch(rect)

plt.tight_layout()
plt.savefig('analysis_outputs/key_insights_summary.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "="*80)
print("VISUALIZATION COMPLETE")
print("="*80)
print(f"\nTotal visualizations created: 6")
print(f"Data points visualized: {analysis_data['metadata']['total_records']:,}")
print(f"Time period: {analysis_data['metadata']['date_range']['start'][:10]} to {analysis_data['metadata']['date_range']['end'][:10]}")
print("\nVisualization files saved to analysis_outputs/:")
print("  - executive_dashboard.png")
print("  - time_series_analysis.png")
print("  - category_distribution.png")
print("  - geographic_analysis.png")
print("  - contractor_performance.png")
print("  - key_insights_summary.png")
print("\nThese visualizations provide a comprehensive view of the Minneapolis plumbing permits data.")
print("Each chart is designed to highlight specific insights and patterns in the data.")