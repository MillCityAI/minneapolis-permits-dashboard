#!/usr/bin/env python3
"""
Detailed analysis of categorized Minneapolis building permits.
Generates comprehensive reports by category and use case.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_data():
    """Load the categorized permits data."""
    print("Loading categorized permits data...")
    
    # Load original data with categories
    df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)
    
    # Reapply categorization
    from categorize_permits import categorize_permit
    df[['sub_category', 'use_case']] = df.apply(
        lambda row: pd.Series(categorize_permit(row)), axis=1
    )
    
    # Convert date columns
    df['issueDate'] = pd.to_datetime(df['issueDate'], errors='coerce')
    df['completeDate'] = pd.to_datetime(df['completeDate'], errors='coerce')
    
    # Calculate processing days
    df['processing_days'] = (df['completeDate'] - df['issueDate']).dt.days
    
    # Extract year and month for temporal analysis
    df['issue_year'] = df['issueDate'].dt.year
    df['issue_month'] = df['issueDate'].dt.month
    
    print(f"Loaded {len(df)} permits")
    return df

def analyze_by_use_case(df):
    """Generate detailed analysis by use case."""
    print("\nAnalyzing by use case...")
    
    results = []
    
    # Get unique combinations of sub_category and use_case
    grouped = df.groupby(['sub_category', 'use_case'])
    
    for (sub_cat, use_case), group in grouped:
        if pd.isna(use_case):
            continue
            
        # Calculate statistics
        stats = {
            'sub_category': sub_cat,
            'use_case': use_case,
            'permit_count': len(group),
            'total_value': group['value'].sum(),
            'average_value': group['value'].mean(),
            'median_value': group['value'].median(),
            'total_fees': group['totalFees'].sum(),
            'average_fee': group['totalFees'].mean(),
            'avg_processing_days': group['processing_days'].mean(),
            'median_processing_days': group['processing_days'].median()
        }
        
        # Get top applicants
        top_applicants = group['applicantName'].value_counts().head(5)
        for i, (applicant, count) in enumerate(top_applicants.items()):
            stats[f'top_applicant_{i+1}'] = applicant
            stats[f'top_applicant_{i+1}_count'] = count
        
        # Get top neighborhoods
        top_neighborhoods = group['Neighborhoods_Desc'].value_counts().head(3)
        for i, (neighborhood, count) in enumerate(top_neighborhoods.items()):
            stats[f'top_neighborhood_{i+1}'] = neighborhood
            stats[f'top_neighborhood_{i+1}_count'] = count
        
        results.append(stats)
    
    # Create DataFrame and save
    use_case_df = pd.DataFrame(results)
    use_case_df = use_case_df.sort_values(['sub_category', 'permit_count'], ascending=[True, False])
    use_case_df.to_csv('use_case_analysis.csv', index=False)
    
    print(f"Generated use case analysis for {len(results)} use cases")
    return use_case_df

def analyze_applicants(df):
    """Analyze top permit applicants."""
    print("\nAnalyzing applicants...")
    
    # Overall top applicants
    top_100_applicants = df['applicantName'].value_counts().head(100)
    
    applicant_analysis = []
    
    for applicant, total_permits in top_100_applicants.items():
        applicant_data = df[df['applicantName'] == applicant]
        
        # Determine applicant type
        if any(keyword in applicant.lower() for keyword in ['llc', 'inc', 'corp', 'company', 'heating', 'plumbing', 'electric']):
            applicant_type = 'Contractor'
        else:
            applicant_type = 'Property Owner'
        
        # Calculate specialization
        category_counts = applicant_data['sub_category'].value_counts()
        primary_category = category_counts.index[0] if len(category_counts) > 0 else 'Unknown'
        specialization_pct = (category_counts.iloc[0] / total_permits * 100) if len(category_counts) > 0 else 0
        
        # Geographic coverage
        neighborhoods = applicant_data['Neighborhoods_Desc'].nunique()
        
        stats = {
            'applicant_name': applicant,
            'total_permits': total_permits,
            'applicant_type': applicant_type,
            'primary_category': primary_category,
            'specialization_pct': specialization_pct,
            'total_value': applicant_data['value'].sum(),
            'avg_project_value': applicant_data['value'].mean(),
            'neighborhoods_served': neighborhoods,
            'avg_processing_days': applicant_data['processing_days'].mean()
        }
        
        applicant_analysis.append(stats)
    
    # Save results
    applicant_df = pd.DataFrame(applicant_analysis)
    applicant_df.to_csv('applicant_analysis.csv', index=False)
    
    print(f"Analyzed top {len(applicant_df)} applicants")
    return applicant_df

def generate_html_report(df, use_case_df, applicant_df):
    """Generate comprehensive HTML report."""
    print("\nGenerating HTML reports...")
    
    # Master category analysis report
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minneapolis Permits - Category Analysis</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        h1 {
            color: #2e7d32;
            border-bottom: 3px solid #2e7d32;
            padding-bottom: 10px;
        }
        h2 {
            color: #1565c0;
            margin-top: 40px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        h3 {
            color: #424242;
            margin-top: 30px;
        }
        .stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .stat-card {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #2e7d32;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #2e7d32;
        }
        .stat-label {
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #2e7d32;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .category-section {
            margin: 40px 0;
            padding: 30px;
            background-color: #fafafa;
            border-radius: 8px;
        }
        .use-case-table {
            font-size: 14px;
        }
        .highlight {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #ffc107;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Minneapolis Building Permits - Category Analysis</h1>
        <p style="color: #666;">Generated: """ + datetime.now().strftime("%B %d, %Y") + """</p>
        
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value">""" + f"{len(df):,}" + """</div>
                <div class="stat-label">Total Permits Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">$""" + f"{df['value'].sum()/1e9:.1f}B" + """</div>
                <div class="stat-label">Total Construction Value</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">$""" + f"{df['totalFees'].sum()/1e6:.1f}M" + """</div>
                <div class="stat-label">Total Fees Collected</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + f"{df['sub_category'].nunique()}" + """</div>
                <div class="stat-label">Major Categories</div>
            </div>
        </div>
"""
    
    # Add category breakdowns
    for category in df['sub_category'].dropna().unique():
        cat_data = df[df['sub_category'] == category]
        cat_use_cases = use_case_df[use_case_df['sub_category'] == category]
        
        html += f"""
        <div class="category-section">
            <h2>{category}</h2>
            
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(cat_data):,}</div>
                    <div class="stat-label">Total Permits ({len(cat_data)/len(df)*100:.1f}%)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${cat_data['value'].sum()/1e6:.1f}M</div>
                    <div class="stat-label">Total Value</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">${cat_data['value'].mean():,.0f}</div>
                    <div class="stat-label">Average Value</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{cat_data['processing_days'].mean():.0f} days</div>
                    <div class="stat-label">Avg Processing Time</div>
                </div>
            </div>
            
            <h3>Use Case Breakdown</h3>
            <table class="use-case-table">
                <thead>
                    <tr>
                        <th>Use Case</th>
                        <th>Permits</th>
                        <th>Total Value</th>
                        <th>Avg Value</th>
                        <th>Avg Days</th>
                        <th>Top Applicant</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for _, uc in cat_use_cases.iterrows():
            top_applicant = uc.get('top_applicant_1', 'N/A')
            if pd.notna(top_applicant) and len(top_applicant) > 40:
                top_applicant = top_applicant[:40] + '...'
            
            html += f"""
                    <tr>
                        <td>{uc['use_case']}</td>
                        <td>{uc['permit_count']:,}</td>
                        <td>${uc['total_value']:,.0f}</td>
                        <td>${uc['average_value']:,.0f}</td>
                        <td>{uc['avg_processing_days']:.0f}</td>
                        <td>{top_applicant}</td>
                    </tr>
"""
        
        html += """
                </tbody>
            </table>
        </div>
"""
    
    html += """
    </div>
</body>
</html>
"""
    
    # Save master report
    with open('permit_analysis_by_category.html', 'w') as f:
        f.write(html)
    
    # Generate applicant analysis report
    applicant_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minneapolis Permits - Applicant Analysis</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }
        h1 {
            color: #d32f2f;
            border-bottom: 3px solid #d32f2f;
            padding-bottom: 10px;
        }
        h2 {
            color: #1976d2;
            margin-top: 40px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #1976d2;
            color: white;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .contractor {
            background-color: #e3f2fd;
        }
        .stat-summary {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin: 30px 0;
        }
        .stat-box {
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 36px;
            font-weight: bold;
            color: #d32f2f;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Top 100 Permit Applicants Analysis</h1>
        <p style="color: #666;">Generated: """ + datetime.now().strftime("%B %d, %Y") + """</p>
        
        <div class="stat-summary">
            <div class="stat-box">
                <div class="stat-number">""" + f"{len(applicant_df[applicant_df['applicant_type'] == 'Contractor'])}" + """</div>
                <div>Contractors</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">""" + f"{len(applicant_df[applicant_df['applicant_type'] == 'Property Owner'])}" + """</div>
                <div>Property Owners</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">""" + f"{applicant_df['total_permits'].sum():,}" + """</div>
                <div>Total Permits</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">$""" + f"{applicant_df['total_value'].sum()/1e9:.1f}B" + """</div>
                <div>Total Value</div>
            </div>
        </div>
        
        <h2>Top Applicants by Permit Volume</h2>
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Applicant Name</th>
                    <th>Type</th>
                    <th>Permits</th>
                    <th>Primary Category</th>
                    <th>Specialization</th>
                    <th>Total Value</th>
                    <th>Avg Value</th>
                    <th>Neighborhoods</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, row in applicant_df.iterrows():
        row_class = 'contractor' if row['applicant_type'] == 'Contractor' else ''
        
        applicant_html += f"""
                <tr class="{row_class}">
                    <td>{idx + 1}</td>
                    <td>{row['applicant_name']}</td>
                    <td>{row['applicant_type']}</td>
                    <td>{row['total_permits']:,}</td>
                    <td>{row['primary_category']}</td>
                    <td>{row['specialization_pct']:.0f}%</td>
                    <td>${row['total_value']:,.0f}</td>
                    <td>${row['avg_project_value']:,.0f}</td>
                    <td>{row['neighborhoods_served']}</td>
                </tr>
"""
    
    applicant_html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    
    with open('applicant_analysis.html', 'w') as f:
        f.write(applicant_html)
    
    print("Generated HTML reports")

def generate_temporal_analysis(df):
    """Generate temporal analysis by category."""
    print("\nGenerating temporal analysis...")
    
    # Annual trends by category
    annual_trends = df.groupby(['issue_year', 'sub_category']).size().reset_index(name='permit_count')
    annual_trends = annual_trends.pivot(index='issue_year', columns='sub_category', values='permit_count').fillna(0)
    annual_trends.to_csv('annual_trends_by_category.csv')
    
    # Seasonal patterns
    seasonal = df.groupby(['issue_month', 'sub_category']).size().reset_index(name='permit_count')
    seasonal = seasonal.pivot(index='issue_month', columns='sub_category', values='permit_count').fillna(0)
    seasonal.to_csv('seasonal_patterns_by_category.csv')
    
    print("Generated temporal analysis files")

def main():
    # Load data
    df = load_data()
    
    # Generate analyses
    use_case_df = analyze_by_use_case(df)
    applicant_df = analyze_applicants(df)
    
    # Generate reports
    generate_html_report(df, use_case_df, applicant_df)
    generate_temporal_analysis(df)
    
    # Generate summary statistics for uncategorized permits
    uncategorized = df[df['use_case'].isna()]
    if len(uncategorized) > 0:
        print(f"\nNote: {len(uncategorized):,} permits ({len(uncategorized)/len(df)*100:.1f}%) "
              f"could not be mapped to specific use cases")
        
        # Save sample of uncategorized for review
        uncategorized.sample(min(1000, len(uncategorized))).to_csv('uncategorized_sample.csv', index=False)
    
    print("\nAnalysis complete!")
    print("\nFiles generated:")
    print("  - permit_analysis_by_category.html (master category report)")
    print("  - applicant_analysis.html (top 100 applicants)")
    print("  - use_case_analysis.csv (detailed use case statistics)")
    print("  - applicant_analysis.csv (applicant details)")
    print("  - annual_trends_by_category.csv")
    print("  - seasonal_patterns_by_category.csv")

if __name__ == "__main__":
    main()