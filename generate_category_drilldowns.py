#!/usr/bin/env python3
"""
Generate detailed drill-down reports for each permit sub-category.
Creates comprehensive HTML reports with complete applicant lists and detailed metrics.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def load_and_prepare_data():
    """Load permit data and apply categorization."""
    print("Loading and preparing permit data...")
    
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
    
    # Calculate processing days
    df['processing_days'] = (df['completeDate'] - df['issueDate']).dt.days
    
    # Extract year and month
    df['issue_year'] = df['issueDate'].dt.year
    df['issue_month'] = df['issueDate'].dt.month
    
    # Define status categories
    df['is_completed'] = df['status'] == 'Closed'
    df['is_active'] = df['status'].isin(['Issued', 'Open', 'In Process'])
    df['is_abandoned'] = df['status'].isin(['Cancelled', 'Withdrawn', 'Stop Work', 'Void'])
    
    print(f"Loaded {len(df)} permits")
    return df

def analyze_category_applicants(df, category):
    """Analyze all applicants for a specific category."""
    cat_df = df[df['sub_category'] == category]
    
    # Get all applicants
    applicant_stats = []
    
    for applicant in cat_df['applicantName'].unique():
        if pd.isna(applicant):
            continue
            
        app_data = cat_df[cat_df['applicantName'] == applicant]
        
        # Calculate use case breakdown
        use_case_counts = app_data['use_case'].value_counts()
        primary_use_case = use_case_counts.index[0] if len(use_case_counts) > 0 else 'N/A'
        
        stats = {
            'applicant_name': applicant,
            'total_permits': len(app_data),
            'completed_permits': len(app_data[app_data['is_completed']]),
            'active_permits': len(app_data[app_data['is_active']]),
            'abandoned_permits': len(app_data[app_data['is_abandoned']]),
            'completion_rate': len(app_data[app_data['is_completed']]) / len(app_data) * 100,
            'abandonment_rate': len(app_data[app_data['is_abandoned']]) / len(app_data) * 100,
            'total_value': app_data['value'].sum(),
            'avg_value': app_data['value'].mean(),
            'total_fees': app_data['totalFees'].sum(),
            'avg_processing_days': app_data[app_data['is_completed']]['processing_days'].mean(),
            'neighborhoods_served': app_data['Neighborhoods_Desc'].nunique(),
            'primary_use_case': primary_use_case,
            'use_case_diversity': len(use_case_counts)
        }
        
        # Determine applicant type
        if any(keyword in applicant.lower() for keyword in ['llc', 'inc', 'corp', 'company', 'heating', 'plumbing', 'electric', 'construction', 'builders']):
            stats['applicant_type'] = 'Contractor'
        else:
            stats['applicant_type'] = 'Property Owner'
        
        applicant_stats.append(stats)
    
    # Convert to DataFrame and sort
    applicant_df = pd.DataFrame(applicant_stats)
    applicant_df = applicant_df.sort_values('total_permits', ascending=False)
    
    return applicant_df

def generate_category_report(df, category, abandonment_data):
    """Generate detailed HTML report for a specific category."""
    print(f"\nGenerating report for {category}...")
    
    # Filter data for this category
    cat_df = df[df['sub_category'] == category]
    
    if len(cat_df) == 0:
        print(f"No data for {category}, skipping...")
        return
    
    # Get applicant analysis
    applicant_df = analyze_category_applicants(df, category)
    
    # Save applicant CSV
    csv_filename = f"drill_down_reports/data/{category.lower().replace(' ', '_')}_all_applicants.csv"
    applicant_df.to_csv(csv_filename, index=False)
    print(f"  Saved {len(applicant_df)} applicants to CSV")
    
    # Get abandonment data for this category
    cat_abandonment = abandonment_data[abandonment_data['category'] == category]
    
    # Calculate statistics
    total_permits = len(cat_df)
    total_value = cat_df['value'].sum()
    avg_value = cat_df['value'].mean()
    median_value = cat_df['value'].median()
    total_fees = cat_df['totalFees'].sum()
    
    # Status breakdown
    status_counts = cat_df['status'].value_counts()
    
    # Use case breakdown
    use_case_stats = []
    for use_case in cat_df['use_case'].dropna().unique():
        uc_data = cat_df[cat_df['use_case'] == use_case]
        use_case_stats.append({
            'use_case': use_case,
            'count': len(uc_data),
            'value': uc_data['value'].sum(),
            'avg_value': uc_data['value'].mean(),
            'completion_rate': len(uc_data[uc_data['is_completed']]) / len(uc_data) * 100
        })
    use_case_df = pd.DataFrame(use_case_stats).sort_values('count', ascending=False)
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{category} Permits - Detailed Analysis</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #1565c0;
            border-bottom: 3px solid #1565c0;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #424242;
            margin-top: 40px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        h3 {{
            color: #616161;
            margin-top: 30px;
        }}
        .nav-bar {{
            background-color: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 30px;
        }}
        .nav-bar a {{
            margin-right: 20px;
            text-decoration: none;
            color: #1565c0;
            font-weight: bold;
        }}
        .nav-bar a:hover {{
            text-decoration: underline;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #1565c0;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #1565c0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .warning-card {{
            border-left-color: #ff9800;
        }}
        .warning-card .stat-value {{
            color: #ff9800;
        }}
        .danger-card {{
            border-left-color: #f44336;
        }}
        .danger-card .stat-value {{
            color: #f44336;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #1565c0;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .section {{
            margin: 40px 0;
            padding: 30px;
            background-color: #fafafa;
            border-radius: 8px;
        }}
        .progress-bar {{
            width: 100%;
            height: 20px;
            background-color: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
        }}
        .progress-fill {{
            height: 100%;
            background-color: #4caf50;
            transition: width 0.3s;
        }}
        .contractor {{
            background-color: #e3f2fd;
        }}
        .top-performer {{
            background-color: #c8e6c9;
        }}
        .download-link {{
            display: inline-block;
            margin: 20px 0;
            padding: 10px 20px;
            background-color: #1565c0;
            color: white;
            text-decoration: none;
            border-radius: 5px;
        }}
        .download-link:hover {{
            background-color: #0d47a1;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="nav-bar">
            <a href="summary_dashboard.html">← Back to Summary</a>
            <a href="../permit_analysis_by_category.html">Category Overview</a>
            <a href="../applicant_analysis.html">Top 100 Applicants</a>
        </div>
        
        <h1>{category} Permits - Detailed Analysis</h1>
        <p style="color: #666;">Generated: {datetime.now().strftime("%B %d, %Y")} | Total Records: {total_permits:,}</p>
        
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value">{total_permits:,}</div>
                <div class="stat-label">Total Permits</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${total_value/1e6:.1f}M</div>
                <div class="stat-label">Total Value</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${avg_value:,.0f}</div>
                <div class="stat-label">Average Value</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">${median_value:,.0f}</div>
                <div class="stat-label">Median Value</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(applicant_df):,}</div>
                <div class="stat-label">Unique Applicants</div>
            </div>
            <div class="stat-card warning-card">
                <div class="stat-value">{status_counts.get('Issued', 0) + status_counts.get('Open', 0):,}</div>
                <div class="stat-label">Active Permits</div>
            </div>
            <div class="stat-card danger-card">
                <div class="stat-value">{(status_counts.get('Cancelled', 0) + status_counts.get('Withdrawn', 0)) / total_permits * 100:.1f}%</div>
                <div class="stat-label">Abandonment Rate</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Status Breakdown</h2>
            <table style="max-width: 600px;">
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>Count</th>
                        <th>Percentage</th>
                        <th>Visual</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add status rows
    for status, count in status_counts.items():
        pct = count / total_permits * 100
        color = '#4caf50' if status == 'Closed' else '#ff9800' if status in ['Issued', 'Open'] else '#f44336'
        html += f"""
                    <tr>
                        <td>{status}</td>
                        <td>{count:,}</td>
                        <td>{pct:.1f}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {pct}%; background-color: {color};"></div>
                            </div>
                        </td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Use Case Breakdown</h2>
            <table>
                <thead>
                    <tr>
                        <th>Use Case</th>
                        <th>Permits</th>
                        <th>% of Category</th>
                        <th>Total Value</th>
                        <th>Avg Value</th>
                        <th>Completion Rate</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add use case rows
    for _, uc in use_case_df.iterrows():
        html += f"""
                    <tr>
                        <td>{uc['use_case']}</td>
                        <td>{uc['count']:,}</td>
                        <td>{uc['count']/total_permits*100:.1f}%</td>
                        <td>${uc['value']:,.0f}</td>
                        <td>${uc['avg_value']:,.0f}</td>
                        <td>{uc['completion_rate']:.1f}%</td>
                    </tr>
"""
    
    html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Complete Applicant Analysis</h2>
            <p>Total unique applicants: {len(applicant_df):,}</p>
            <p>Contractors: {len(applicant_df[applicant_df['applicant_type'] == 'Contractor']):,} | 
               Property Owners: {len(applicant_df[applicant_df['applicant_type'] == 'Property Owner']):,}</p>
            
            <a href="data/{category.lower().replace(' ', '_')}_all_applicants.csv" class="download-link">
                Download Complete Applicant List (CSV)
            </a>
            
            <h3>Top 50 Applicants by Volume</h3>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Applicant Name</th>
                        <th>Type</th>
                        <th>Permits</th>
                        <th>Completion Rate</th>
                        <th>Abandonment Rate</th>
                        <th>Total Value</th>
                        <th>Avg Days</th>
                        <th>Primary Use Case</th>
                        <th>Neighborhoods</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    # Add top 50 applicants
    for idx, row in applicant_df.head(50).iterrows():
        row_class = 'contractor' if row['applicant_type'] == 'Contractor' else ''
        if row['completion_rate'] > 95:
            row_class += ' top-performer'
        
        html += f"""
                    <tr class="{row_class}">
                        <td>{idx + 1}</td>
                        <td>{row['applicant_name'][:50]}</td>
                        <td>{row['applicant_type']}</td>
                        <td>{row['total_permits']:,}</td>
                        <td>{row['completion_rate']:.1f}%</td>
                        <td style="color: {'red' if row['abandonment_rate'] > 10 else 'green'}">{row['abandonment_rate']:.1f}%</td>
                        <td>${row['total_value']:,.0f}</td>
                        <td>{row['avg_processing_days']:.0f}</td>
                        <td>{row['primary_use_case']}</td>
                        <td>{row['neighborhoods_served']}</td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Geographic Distribution</h2>
"""
    
    # Top neighborhoods
    neighborhood_counts = cat_df['Neighborhoods_Desc'].value_counts().head(20)
    
    html += """
            <h3>Top 20 Neighborhoods</h3>
            <table style="max-width: 800px;">
                <thead>
                    <tr>
                        <th>Neighborhood</th>
                        <th>Permits</th>
                        <th>% of Category</th>
                        <th>Visual</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    max_count = neighborhood_counts.iloc[0] if len(neighborhood_counts) > 0 else 1
    for neighborhood, count in neighborhood_counts.items():
        pct = count / total_permits * 100
        bar_width = (count / max_count) * 100
        
        html += f"""
                    <tr>
                        <td>{neighborhood}</td>
                        <td>{count:,}</td>
                        <td>{pct:.1f}%</td>
                        <td>
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {bar_width}%;"></div>
                            </div>
                        </td>
                    </tr>
"""
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Temporal Analysis</h2>
"""
    
    # Annual trends
    annual_counts = cat_df.groupby('issue_year').size()
    
    html += """
            <h3>Annual Permit Volume</h3>
            <table style="max-width: 600px;">
                <thead>
                    <tr>
                        <th>Year</th>
                        <th>Permits</th>
                        <th>YoY Change</th>
                    </tr>
                </thead>
                <tbody>
"""
    
    prev_count = None
    for year, count in annual_counts.items():
        if pd.notna(year) and year >= 2017:  # Focus on recent years
            yoy_change = ''
            if prev_count is not None:
                change = ((count - prev_count) / prev_count) * 100
                yoy_change = f"{change:+.1f}%"
                yoy_change = f'<span style="color: {"green" if change > 0 else "red"}">{yoy_change}</span>'
            
            html += f"""
                    <tr>
                        <td>{int(year)}</td>
                        <td>{count:,}</td>
                        <td>{yoy_change}</td>
                    </tr>
"""
            prev_count = count
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>Processing Time Analysis</h2>
"""
    
    # Processing time statistics
    completed_df = cat_df[cat_df['is_completed'] & cat_df['processing_days'].notna()]
    
    if len(completed_df) > 0:
        html += f"""
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{completed_df['processing_days'].mean():.0f}</div>
                    <div class="stat-label">Average Days</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{completed_df['processing_days'].median():.0f}</div>
                    <div class="stat-label">Median Days</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{completed_df['processing_days'].quantile(0.9):.0f}</div>
                    <div class="stat-label">90th Percentile</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{len(completed_df[completed_df['processing_days'] <= 30]):,}</div>
                    <div class="stat-label">Completed in 30 Days</div>
                </div>
            </div>
"""
    
    html += """
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML file
    filename = f"drill_down_reports/{category.lower().replace(' ', '_')}_detailed_report.html"
    with open(filename, 'w') as f:
        f.write(html)
    
    print(f"  Generated HTML report: {filename}")

def generate_summary_dashboard(df):
    """Generate summary dashboard linking to all category reports."""
    print("\nGenerating summary dashboard...")
    
    categories = df['sub_category'].dropna().unique()
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minneapolis Permits - Category Analysis Dashboard</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
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
        .category-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        .category-card {
            background-color: #f8f9fa;
            padding: 30px;
            border-radius: 8px;
            border-left: 4px solid #2e7d32;
            transition: transform 0.2s;
            cursor: pointer;
        }
        .category-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .category-title {
            font-size: 24px;
            font-weight: bold;
            color: #2e7d32;
            margin-bottom: 10px;
        }
        .category-stats {
            color: #666;
            font-size: 14px;
        }
        a {
            text-decoration: none;
            color: inherit;
        }
        .nav-links {
            margin: 20px 0;
            padding: 20px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        .nav-links a {
            margin-right: 20px;
            color: #2e7d32;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Minneapolis Permits - Category Analysis Dashboard</h1>
        <p style="color: #666;">Select a category for detailed drill-down analysis</p>
        
        <div class="nav-links">
            <a href="../permit_analysis_by_category.html">Overview Report</a>
            <a href="../applicant_analysis.html">Top 100 Applicants</a>
            <a href="../use_case_analysis.csv">Use Case Data</a>
        </div>
        
        <div class="category-grid">
"""
    
    # Add category cards
    for category in sorted(categories):
        if pd.isna(category):
            continue
            
        cat_data = df[df['sub_category'] == category]
        permit_count = len(cat_data)
        total_value = cat_data['value'].sum()
        completion_rate = len(cat_data[cat_data['status'] == 'Closed']) / permit_count * 100
        
        html += f"""
            <a href="{category.lower().replace(' ', '_')}_detailed_report.html">
                <div class="category-card">
                    <div class="category-title">{category}</div>
                    <div class="category-stats">
                        <p><strong>{permit_count:,}</strong> total permits</p>
                        <p><strong>${total_value/1e6:.1f}M</strong> total value</p>
                        <p><strong>{completion_rate:.1f}%</strong> completion rate</p>
                        <p style="margin-top: 10px;">Click for detailed analysis →</p>
                    </div>
                </div>
            </a>
"""
    
    html += """
        </div>
        
        <div style="margin-top: 40px; padding: 20px; background-color: #e8f5e9; border-radius: 5px;">
            <h2 style="color: #2e7d32;">Available Reports</h2>
            <p>Each category report includes:</p>
            <ul>
                <li>Complete applicant list (all applicants, not just top 100)</li>
                <li>Detailed abandonment analysis</li>
                <li>Use case breakdowns</li>
                <li>Geographic distribution</li>
                <li>Temporal trends</li>
                <li>Processing time analysis</li>
                <li>Downloadable CSV data files</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""
    
    with open('drill_down_reports/summary_dashboard.html', 'w') as f:
        f.write(html)
    
    print("  Generated summary dashboard")

def main():
    """Generate all category drill-down reports."""
    # Load and prepare data
    df = load_and_prepare_data()
    
    # Run abandonment analysis first
    print("\nRunning abandonment analysis...")
    import abandonment_analysis
    abandonment_analysis.main()
    
    # Load abandonment results
    abandonment_data = pd.read_csv('drill_down_reports/data/abandonment_analysis_by_category.csv')
    
    # Generate reports for each category
    categories = df['sub_category'].dropna().unique()
    
    for category in sorted(categories):
        generate_category_report(df, category, abandonment_data)
    
    # Generate summary dashboard
    generate_summary_dashboard(df)
    
    print("\n" + "="*60)
    print("DRILL-DOWN REPORT GENERATION COMPLETE")
    print("="*60)
    print("\nGenerated reports:")
    print("  - 7 detailed category HTML reports")
    print("  - 7 complete applicant CSV files")
    print("  - 1 summary dashboard")
    print("  - Abandonment analysis data")
    print("\nOpen drill_down_reports/summary_dashboard.html to start exploring!")

if __name__ == "__main__":
    main()