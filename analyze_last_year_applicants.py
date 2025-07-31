#!/usr/bin/env python3
"""
Analyze Minneapolis building permits from the last year (June 2024 - June 2025).
Focus on active contractors with contact information for sales outreach.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

def load_and_filter_data():
    """Load permits data and filter to last year only."""
    print("Loading permit data...")
    
    # Load the data
    df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)
    
    # Convert date columns
    df['issueDate'] = pd.to_datetime(df['issueDate'], errors='coerce')
    df['completeDate'] = pd.to_datetime(df['completeDate'], errors='coerce')
    
    # Filter to last year (June 2024 onwards)
    cutoff_date = pd.Timestamp('2024-06-01', tz='UTC')
    df_last_year = df[df['issueDate'] >= cutoff_date].copy()
    
    # Calculate processing days
    df_last_year['processing_days'] = (df_last_year['completeDate'] - df_last_year['issueDate']).dt.days
    
    # Add month/year for trending
    df_last_year['issue_month'] = df_last_year['issueDate'].dt.to_period('M')
    
    print(f"Total permits in dataset: {len(df)}")
    print(f"Permits in last year (since June 2024): {len(df_last_year)}")
    
    return df_last_year

def categorize_permits(df):
    """Add permit categories based on permitType."""
    # Define major categories
    def get_major_category(permit_type):
        if pd.isna(permit_type):
            return 'Other'
        
        permit_type_upper = str(permit_type).upper()
        
        if 'PLUMB' in permit_type_upper:
            return 'Plumbing'
        elif 'MECH' in permit_type_upper:
            return 'Mechanical'
        elif 'SOLAR' in permit_type_upper:
            return 'Solar'
        elif 'SIGN' in permit_type_upper:
            return 'Sign'
        elif 'WRECK' in permit_type_upper or 'DEMO' in permit_type_upper:
            return 'Wrecking/Demo'
        elif 'SOIL' in permit_type_upper or 'EROSION' in permit_type_upper:
            return 'Soil Erosion'
        elif any(x in permit_type_upper for x in ['RES', 'COM', 'BLDG']):
            return 'Building'
        else:
            return 'Other'
    
    df['major_category'] = df['permitType'].apply(get_major_category)
    return df

def analyze_applicants(df):
    """Analyze top applicants with detailed metrics."""
    print("\nAnalyzing applicants...")
    
    # Get top applicants by volume
    applicant_stats = []
    top_applicants = df['applicantName'].value_counts().head(100)
    
    for applicant, total_permits in top_applicants.items():
        if pd.isna(applicant):
            continue
            
        applicant_data = df[df['applicantName'] == applicant]
        
        # Get contact info (use most common address/city)
        address_counts = applicant_data['applicantAddress1'].value_counts()
        city_counts = applicant_data['applicantCity'].value_counts()
        
        primary_address = address_counts.index[0] if len(address_counts) > 0 else 'N/A'
        primary_city = city_counts.index[0] if len(city_counts) > 0 else 'N/A'
        
        # Category breakdown
        category_breakdown = applicant_data['major_category'].value_counts()
        primary_category = category_breakdown.index[0] if len(category_breakdown) > 0 else 'Unknown'
        category_focus_pct = (category_breakdown.iloc[0] / total_permits * 100) if len(category_breakdown) > 0 else 0
        
        # Geographic coverage
        neighborhoods = applicant_data['Neighborhoods_Desc'].value_counts()
        top_neighborhoods = neighborhoods.head(3).index.tolist() if len(neighborhoods) > 0 else []
        
        # Project values
        avg_value = applicant_data['value'].mean()
        total_value = applicant_data['value'].sum()
        
        # Success metrics
        completed = len(applicant_data[applicant_data['status'] == 'Closed'])
        completion_rate = (completed / total_permits * 100) if total_permits > 0 else 0
        
        # Monthly trend
        monthly_permits = applicant_data.groupby('issue_month').size()
        avg_monthly = monthly_permits.mean() if len(monthly_permits) > 0 else 0
        
        # Processing speed
        avg_processing = applicant_data['processing_days'].mean()
        
        stats = {
            'Company Name': applicant,
            'Business Address': primary_address,
            'City': primary_city,
            'Total Permits (Last Year)': total_permits,
            'Primary Category': primary_category,
            'Category Focus %': round(category_focus_pct, 1),
            'Avg Monthly Permits': round(avg_monthly, 1),
            'Total Project Value': round(total_value, 2),
            'Avg Project Value': round(avg_value, 2),
            'Top Neighborhoods': ', '.join(top_neighborhoods[:3]),
            'Completion Rate %': round(completion_rate, 1),
            'Avg Processing Days': round(avg_processing, 1) if pd.notna(avg_processing) else 'N/A'
        }
        
        # Add category breakdown
        for cat in ['Plumbing', 'Mechanical', 'Building', 'Solar']:
            count = category_breakdown.get(cat, 0)
            stats[f'{cat} Permits'] = count
        
        applicant_stats.append(stats)
    
    return pd.DataFrame(applicant_stats)

def generate_monthly_trends(df):
    """Generate monthly permit trends for top applicants."""
    print("\nGenerating monthly trends...")
    
    # Get top 20 applicants
    top_20 = df['applicantName'].value_counts().head(20).index
    
    trends = []
    for applicant in top_20:
        applicant_data = df[df['applicantName'] == applicant]
        monthly = applicant_data.groupby('issue_month').size()
        
        for month, count in monthly.items():
            trends.append({
                'Applicant': applicant,
                'Month': str(month),
                'Permits': count
            })
    
    return pd.DataFrame(trends)

def generate_sales_report(applicant_df):
    """Generate a sales-focused CSV report."""
    print("\nGenerating sales report...")
    
    # Select and reorder columns for sales team
    sales_columns = [
        'Company Name',
        'Business Address', 
        'City',
        'Total Permits (Last Year)',
        'Avg Monthly Permits',
        'Primary Category',
        'Category Focus %',
        'Plumbing Permits',
        'Mechanical Permits',
        'Building Permits',
        'Solar Permits',
        'Total Project Value',
        'Avg Project Value',
        'Top Neighborhoods',
        'Completion Rate %'
    ]
    
    sales_df = applicant_df[sales_columns].copy()
    
    # Add a notes column for sales team
    sales_df['Sales Notes'] = sales_df.apply(lambda row: 
        f"Specializes in {row['Primary Category']} ({row['Category Focus %']}% of work). " +
        f"Active in {row['Top Neighborhoods']}. " +
        f"Averaging {row['Avg Monthly Permits']} permits/month.",
        axis=1
    )
    
    return sales_df

def generate_html_report(applicant_df, trends_df):
    """Generate HTML report for last year's active contractors."""
    print("\nGenerating HTML report...")
    
    # Calculate summary statistics
    total_contractors = len(applicant_df)
    total_permits = int(applicant_df['Total Permits (Last Year)'].sum())
    avg_monthly = int(applicant_df['Total Permits (Last Year)'].sum() / 12)
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minneapolis Permits - Active Contractors (Last Year)</title>
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
        .date-range {
            background-color: #e8f5e9;
            padding: 10px 20px;
            border-radius: 5px;
            display: inline-block;
            margin-bottom: 20px;
            font-weight: bold;
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
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }
        th {
            background-color: #f5f5f5;
            font-weight: 600;
            color: #424242;
            position: sticky;
            top: 0;
            z-index: 10;
        }
        tr:hover {
            background-color: #f8f9fa;
        }
        .company-name {
            font-weight: 600;
            color: #1565c0;
        }
        .category-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .plumbing { background-color: #e3f2fd; color: #1565c0; }
        .mechanical { background-color: #fce4ec; color: #c2185b; }
        .building { background-color: #e8f5e9; color: #2e7d32; }
        .solar { background-color: #fff3e0; color: #ef6c00; }
        .download-section {
            margin-top: 40px;
            padding: 20px;
            background-color: #e8f5e9;
            border-radius: 8px;
            text-align: center;
        }
        .download-btn {
            display: inline-block;
            padding: 12px 24px;
            background-color: #2e7d32;
            color: white;
            text-decoration: none;
            border-radius: 5px;
            font-weight: 600;
            margin: 10px;
        }
        .download-btn:hover {
            background-color: #1b5e20;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Active Contractors Analysis - Last Year</h1>
        <div class="date-range">June 2024 - June 2025</div>
        
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value">""" + str(total_contractors) + """</div>
                <div class="stat-label">Active Contractors</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + f"{total_permits:,}" + """</div>
                <div class="stat-label">Total Permits</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">""" + f"{avg_monthly:,}" + """</div>
                <div class="stat-label">Avg Monthly Permits</div>
            </div>
        </div>
        
        <h2>Top 50 Most Active Contractors</h2>
        <p>Sorted by total permit volume in the last year. Click company names for detailed view.</p>
        
        <table>
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Company Name</th>
                    <th>Location</th>
                    <th>Permits</th>
                    <th>Primary Category</th>
                    <th>Avg/Month</th>
                    <th>Total Value</th>
                    <th>Top Areas</th>
                </tr>
            </thead>
            <tbody>
"""
    
    # Add top 50 contractors to table
    for idx, row in applicant_df.head(50).iterrows():
        category_class = row['Primary Category'].lower().replace('/', '').replace(' ', '')
        
        html += f"""
                <tr>
                    <td>{idx + 1}</td>
                    <td class="company-name">{row['Company Name']}</td>
                    <td>{row['City']}</td>
                    <td>{row['Total Permits (Last Year)']:,}</td>
                    <td><span class="category-badge {category_class}">{row['Primary Category']}</span></td>
                    <td>{row['Avg Monthly Permits']}</td>
                    <td>${row['Total Project Value']:,.0f}</td>
                    <td>{row['Top Neighborhoods']}</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
        
        <div class="download-section">
            <h3>Download Full Data</h3>
            <p>Get complete contractor information including contact details and detailed metrics.</p>
            <a href="last_year_contractors_sales.csv" class="download-btn">Download Sales CSV</a>
            <a href="last_year_contractors_full.csv" class="download-btn">Download Full Report</a>
        </div>
    </div>
</body>
</html>
"""
    
    return html

def main():
    """Main execution function."""
    print("Minneapolis Permits - Last Year Analysis")
    print("=" * 50)
    
    # Load and prepare data
    df = load_and_filter_data()
    df = categorize_permits(df)
    
    # Analyze applicants
    applicant_df = analyze_applicants(df)
    
    # Generate monthly trends
    trends_df = generate_monthly_trends(df)
    
    # Generate sales report
    sales_df = generate_sales_report(applicant_df)
    
    # Save CSV files
    print("\nSaving CSV files...")
    applicant_df.to_csv('last_year_contractors_full.csv', index=False)
    sales_df.to_csv('last_year_contractors_sales.csv', index=False)
    trends_df.to_csv('last_year_monthly_trends.csv', index=False)
    
    # Generate HTML report
    html_content = generate_html_report(applicant_df, trends_df)
    with open('last_year_active_contractors.html', 'w') as f:
        f.write(html_content)
    
    print("\nAnalysis complete!")
    print(f"Generated files:")
    print("  - last_year_contractors_full.csv (Full analysis)")
    print("  - last_year_contractors_sales.csv (Sales-focused)")
    print("  - last_year_monthly_trends.csv (Monthly trends)")
    print("  - last_year_active_contractors.html (Web report)")
    
    # Print summary
    print(f"\nTop 5 contractors by volume:")
    for idx, row in applicant_df.head(5).iterrows():
        print(f"  {idx+1}. {row['Company Name']} - {row['Total Permits (Last Year)']} permits")

if __name__ == "__main__":
    main()