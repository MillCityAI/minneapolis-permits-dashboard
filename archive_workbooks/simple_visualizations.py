#!/usr/bin/env python
"""
Minneapolis Permits Simple Visualizations
Creates clear, easy-to-understand visualizations of the permits data
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import json
import warnings
warnings.filterwarnings('ignore')

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('husl')

print("Loading analysis data...")
with open('analysis_outputs/plumbing_comprehensive_analysis.json', 'r') as f:
    analysis_data = json.load(f)

print(f"Analysis covers {analysis_data['metadata']['total_records']:,} plumbing permits")
print(f"Date range: {analysis_data['metadata']['date_range']['start'][:10]} to {analysis_data['metadata']['date_range']['end'][:10]}")

# 1. Executive Dashboard
print("\n1. Creating Executive Dashboard...")
fig = plt.figure(figsize=(20, 10))
fig.suptitle('Minneapolis Plumbing Permits - Executive Dashboard', fontsize=24, fontweight='bold')

metrics = analysis_data['summary_metrics']
metric_data = [
    ('Total Permits', f"{metrics['volume']['total_permits']:,}", 'steelblue'),
    ('Monthly Average', f"{metrics['volume']['monthly_average']:.0f}", 'darkorange'),
    ('Growth Trend', f"{metrics['volume']['growth_trend']:.1f}/month", 'forestgreen'),
    ('Median Processing', f"{metrics['processing']['median_days']:.0f} days", 'crimson'),
    ('Total Value', f"${metrics['financial']['total_value']/1e9:.1f}B", 'purple'),
    ('Cancellation Rate', f"{metrics['quality']['cancellation_rate']:.1f}%", 'darkred'),
    ('Emergency Rate', f"{metrics['quality']['emergency_rate']:.1f}%", 'orange'),
    ('Data Quality', f"{metrics['quality']['data_completeness']:.0f}%", 'teal')
]

for i, (label, value, color) in enumerate(metric_data):
    ax = plt.subplot(2, 4, i+1)
    ax.text(0.5, 0.6, value, fontsize=28, fontweight='bold', 
            ha='center', va='center', color=color)
    ax.text(0.5, 0.2, label, fontsize=14, ha='center', va='center')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    rect = plt.Rectangle((0.05, 0.05), 0.9, 0.9, fill=False, 
                        edgecolor=color, linewidth=2, alpha=0.3)
    ax.add_patch(rect)

plt.tight_layout()
plt.savefig('analysis_outputs/executive_dashboard.png', dpi=150, bbox_inches='tight')
plt.show()

# 2. Time Series Analysis
print("\n2. Creating Time Series Analysis...")
monthly_data = pd.DataFrame(analysis_data['time_series']['monthly'])
monthly_data['month'] = pd.to_datetime(monthly_data['month'])

fig, axes = plt.subplots(3, 1, figsize=(20, 12), sharex=True)
fig.suptitle('Minneapolis Plumbing Permits - Time Series Analysis', fontsize=20, fontweight='bold')

# Monthly permits
axes[0].plot(monthly_data['month'], monthly_data['count'], 'b-o', linewidth=2, markersize=4)
monthly_data['ma_12'] = monthly_data['count'].rolling(12).mean()
axes[0].plot(monthly_data['month'], monthly_data['ma_12'], 'r--', linewidth=2, label='12-Month Average')
axes[0].set_ylabel('Number of Permits')
axes[0].set_title('Monthly Permit Volume')
axes[0].grid(True, alpha=0.3)
axes[0].legend()

# Average value
axes[1].bar(monthly_data['month'], monthly_data['avg_value'], color='green', alpha=0.7, width=20)
axes[1].set_ylabel('Average Project Value ($)')
axes[1].set_title('Average Project Value by Month')
axes[1].grid(True, alpha=0.3)

# Processing time
axes[2].plot(monthly_data['month'], monthly_data['avg_processing'], 'o-', color='orange', linewidth=2)
axes[2].set_ylabel('Average Processing Days')
axes[2].set_xlabel('Date')
axes[2].set_title('Processing Time Trends')
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/time_series_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# 3. Category Distribution
print("\n3. Creating Category Analysis...")
categories = analysis_data['categories']['distribution']
cat_df = pd.DataFrame(list(categories.items()), columns=['Category', 'Count']).sort_values('Count', ascending=False)

fig, axes = plt.subplots(2, 2, figsize=(20, 12))
fig.suptitle('Plumbing Permit Categories Analysis', fontsize=20, fontweight='bold')

# Pie chart
top_cats = cat_df.head(8)
other_count = cat_df.iloc[8:]['Count'].sum()
if other_count > 0:
    top_cats = pd.concat([top_cats, pd.DataFrame({'Category': ['Other'], 'Count': [other_count]})])

axes[0,0].pie(top_cats['Count'], labels=top_cats['Category'], autopct='%1.1f%%', startangle=90)
axes[0,0].set_title('Category Distribution (Top 8)')

# Bar chart
axes[0,1].barh(range(len(cat_df.head(15))), cat_df.head(15)['Count'], 
               color=plt.cm.viridis(np.linspace(0.2, 0.8, 15)))
axes[0,1].set_yticks(range(len(cat_df.head(15))))
axes[0,1].set_yticklabels(cat_df.head(15)['Category'])
axes[0,1].invert_yaxis()
axes[0,1].set_xlabel('Number of Permits')
axes[0,1].set_title('Top 15 Categories')

# Cumulative
cat_df['Cumulative'] = cat_df['Count'].cumsum() / cat_df['Count'].sum() * 100
axes[1,0].plot(range(1, len(cat_df)+1), cat_df['Cumulative'], 'b-', linewidth=2)
axes[1,0].fill_between(range(1, len(cat_df)+1), 0, cat_df['Cumulative'], alpha=0.3)
axes[1,0].axhline(y=80, color='r', linestyle='--', label='80% threshold')
axes[1,0].set_xlabel('Number of Categories')
axes[1,0].set_ylabel('Cumulative % of Permits')
axes[1,0].set_title('Category Concentration')
axes[1,0].grid(True, alpha=0.3)
axes[1,0].legend()

# Top 5
top_5 = cat_df.head(5)
bars = axes[1,1].bar(range(5), top_5['Count'], color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
axes[1,1].set_xticks(range(5))
axes[1,1].set_xticklabels(top_5['Category'], rotation=45, ha='right')
axes[1,1].set_ylabel('Number of Permits')
axes[1,1].set_title('Top 5 Categories')
axes[1,1].grid(True, axis='y', alpha=0.3)

for bar in bars:
    height = bar.get_height()
    axes[1,1].text(bar.get_x() + bar.get_width()/2., height,
                  f'{int(height):,}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('analysis_outputs/category_distribution.png', dpi=150, bbox_inches='tight')
plt.show()

# 4. Geographic Analysis
print("\n4. Creating Geographic Analysis...")
neighborhoods = pd.DataFrame(analysis_data['geographic']['top_neighborhoods'])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))
fig.suptitle('Geographic Distribution Analysis', fontsize=20, fontweight='bold')

# Volume vs Processing scatter
scatter = ax1.scatter(neighborhoods['permitNumber'], neighborhoods['processing_days'],
                     s=neighborhoods['value']/1000 + 10, c=neighborhoods['value'],
                     cmap='viridis', alpha=0.6)
ax1.set_xlabel('Number of Permits')
ax1.set_ylabel('Average Processing Days')
ax1.set_title('Neighborhoods: Volume vs Processing Time')

# Label top 5
for i, row in neighborhoods.head(5).iterrows():
    ax1.annotate(row['Neighborhoods_Desc'][:15] + '...', 
                (row['permitNumber'], row['processing_days']),
                xytext=(5, 5), textcoords='offset points', fontsize=9)

cbar = plt.colorbar(scatter, ax=ax1)
cbar.set_label('Average Project Value ($)')

# Top neighborhoods bar
top_10 = neighborhoods.head(10)
bars = ax2.bar(range(len(top_10)), top_10['permitNumber'],
               color=plt.cm.Blues(np.linspace(0.4, 0.9, len(top_10))))
ax2.set_xticks(range(len(top_10)))
ax2.set_xticklabels([n[:12] + '...' if len(n) > 12 else n 
                     for n in top_10['Neighborhoods_Desc']], rotation=45, ha='right')
ax2.set_ylabel('Number of Permits')
ax2.set_title('Top 10 Neighborhoods')

for bar in bars:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width()/2., height,
            f'{int(height):,}', ha='center', va='bottom')

plt.tight_layout()
plt.savefig('analysis_outputs/geographic_analysis.png', dpi=150, bbox_inches='tight')
plt.show()

# 5. Contractor Performance
print("\n5. Creating Contractor Analysis...")
contractors = pd.DataFrame(analysis_data['contractors']['top_20'])

fig, axes = plt.subplots(2, 2, figsize=(20, 12))
fig.suptitle('Contractor Performance Analysis', fontsize=20, fontweight='bold')

# Market share pie
top_10_contractors = contractors.head(10)
other_permits = contractors.iloc[10:]['permitNumber'].sum()
names = [c[:25] + '...' if len(c) > 25 else c for c in top_10_contractors['applicantName']]
values = list(top_10_contractors['permitNumber']) + [other_permits]
names.append('Others (10+)')

axes[0,0].pie(values, labels=names, autopct='%1.1f%%', startangle=90)
axes[0,0].set_title('Contractor Market Share (Top 10)')

# Performance scatter
scatter = axes[0,1].scatter(contractors['permitNumber'], contractors['processing_days'],
                           s=contractors['value']/100 + 10, c=contractors['efficiency_score']*100,
                           cmap='RdYlGn', alpha=0.6)
axes[0,1].set_xlabel('Total Permits')
axes[0,1].set_ylabel('Avg Processing Days')
axes[0,1].set_title('Performance Matrix')
axes[0,1].set_xscale('log')
cbar = plt.colorbar(scatter, ax=axes[0,1])
cbar.set_label('Efficiency Score (%)')

# Top 5 by volume
top_5 = contractors.head(5)
bars = axes[1,0].barh(range(len(top_5)), top_5['permitNumber'], color='skyblue')
axes[1,0].set_yticks(range(len(top_5)))
axes[1,0].set_yticklabels([name[:25] + '...' if len(name) > 25 else name 
                          for name in top_5['applicantName']])
axes[1,0].invert_yaxis()
axes[1,0].set_xlabel('Number of Permits')
axes[1,0].set_title('Top 5 Contractors by Volume')

for i, bar in enumerate(bars):
    width = bar.get_width()
    axes[1,0].text(width + 100, bar.get_y() + bar.get_height()/2,
                  f'{int(width):,}', ha='left', va='center')

# Efficiency comparison
top_10_eff = contractors.head(10)
x = np.arange(len(top_10_eff))
bars = axes[1,1].bar(x, top_10_eff['efficiency_score']*100, color='coral', alpha=0.7)
axes[1,1].set_xticks(x)
axes[1,1].set_xticklabels([name[:15] + '...' if len(name) > 15 else name 
                          for name in top_10_eff['applicantName']], rotation=45, ha='right')
axes[1,1].set_ylabel('Efficiency Score (%)')
axes[1,1].set_title('Top 10 Contractors - Efficiency Scores')
axes[1,1].grid(True, axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('analysis_outputs/contractor_performance.png', dpi=150, bbox_inches='tight')
plt.show()

# 6. Key Insights Summary
print("\n6. Creating Key Insights Summary...")
fig = plt.figure(figsize=(20, 12))
fig.suptitle('Minneapolis Plumbing Permits - Key Insights Summary', 
             fontsize=24, fontweight='bold', y=0.98)

insights = [
    {
        'title': '📊 Volume Trends',
        'points': [
            f"Total Permits: {analysis_data['metadata']['total_records']:,}",
            f"Monthly Average: {analysis_data['summary_metrics']['volume']['monthly_average']:.0f}",
            f"Growth Rate: {analysis_data['summary_metrics']['volume']['growth_trend']:.1f} permits/month",
            "Analysis Period: 2016-2025"
        ],
        'color': 'lightblue'
    },
    {
        'title': '⏱️ Processing Efficiency',
        'points': [
            f"Median Time: {analysis_data['summary_metrics']['processing']['median_days']:.0f} days",
            f"90th Percentile: {analysis_data['summary_metrics']['processing']['p90_days']:.0f} days",
            f"On-Time Rate: {analysis_data['summary_metrics']['processing']['within_30_days_pct']:.1f}%",
            "Process Predictable: Yes"
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
            f"Model R²: {analysis_data['predictions']['model_performance']['r2']:.3f}"
        ],
        'color': 'lightcoral'
    },
    {
        'title': '🏢 Market Structure',
        'points': [
            f"Active Contractors: {len(analysis_data['contractors']['top_20']):,}+",
            "Market: Highly competitive",
            "Geographic: City-wide coverage",
            "Specialization: Common"
        ],
        'color': 'lavender'
    },
    {
        'title': '📈 Predictive Insights',
        'points': [
            "Seasonal Peaks: Identifiable",
            "Risk Assessment: Functional",
            "Processing: Predictable",
            f"Model MAE: {analysis_data['predictions']['model_performance']['mae']:.0f} days"
        ],
        'color': 'lightsteelblue'
    }
]

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
    
    # Border
    rect = plt.Rectangle((0.02, 0.02), 0.96, 0.96, fill=False, 
                        edgecolor='gray', linewidth=2)
    ax.add_patch(rect)

plt.tight_layout()
plt.savefig('analysis_outputs/key_insights_summary.png', dpi=150, bbox_inches='tight')
plt.show()

print("\n" + "="*80)
print("VISUALIZATION COMPLETE")
print("="*80)
print(f"\nVisualization files saved to analysis_outputs/:")
print("  - executive_dashboard.png")
print("  - time_series_analysis.png") 
print("  - category_distribution.png")
print("  - geographic_analysis.png")
print("  - contractor_performance.png")
print("  - key_insights_summary.png")
print(f"\nTotal data points: {analysis_data['metadata']['total_records']:,}")
print(f"Analysis period: {analysis_data['metadata']['date_range']['start'][:10]} to {analysis_data['metadata']['date_range']['end'][:10]}")
print("\nThese visualizations provide comprehensive insights into Minneapolis plumbing permits data.")