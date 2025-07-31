#!/usr/bin/env python3
"""
Extract plumber contact information from Minneapolis permit data
for creating a call sheet with 'Claude' appended to filename
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def extract_plumber_contacts():
    """Extract and process plumber contact information from permit data"""
    
    print("Loading permit data...")
    df = pd.read_csv('source/CCS_Permits.csv')
    
    # Filter for plumbing permits only
    plumbing_df = df[df['permitType'] == 'Plumbing'].copy()
    print(f"Found {len(plumbing_df)} plumbing permits")
    
    # Convert dates and ensure they are timezone-naive
    plumbing_df['issueDate'] = pd.to_datetime(plumbing_df['issueDate'], errors='coerce', utc=True).dt.tz_localize(None)
    plumbing_df['completeDate'] = pd.to_datetime(plumbing_df['completeDate'], errors='coerce', utc=True).dt.tz_localize(None)
    
    # Group by applicant to get unique plumbers with aggregated data
    plumber_summary = plumbing_df.groupby('applicantName').agg({
        'permitNumber': 'count',
        'applicantAddress1': 'first',
        'applicantCity': 'first',
        'fullName': 'first',
        'Neighborhoods_Desc': lambda x: ', '.join(sorted(set(x.dropna()))),
        'issueDate': ['min', 'max'],
        'value': 'sum',
        'totalFees': 'sum',
        'status': lambda x: x.value_counts().to_dict(),
        'workType': lambda x: x.value_counts().head(3).to_dict()
    }).reset_index()
    
    # Flatten column names
    plumber_summary.columns = [
        'Company_Name',
        'Total_Permits',
        'Address',
        'City',
        'Contact_Person',
        'Service_Areas',
        'First_Permit_Date',
        'Last_Permit_Date',
        'Total_Project_Value',
        'Total_Fees_Paid',
        'Status_Distribution',
        'Top_Work_Types'
    ]
    
    # Calculate days since last permit
    today = pd.Timestamp.now()
    plumber_summary['Days_Since_Last_Permit'] = (today - plumber_summary['Last_Permit_Date']).dt.days
    
    # Add activity classification
    plumber_summary['Activity_Level'] = pd.cut(
        plumber_summary['Days_Since_Last_Permit'],
        bins=[0, 30, 90, 180, 365, float('inf')],
        labels=['Very Active (< 30 days)', 'Active (30-90 days)', 
                'Moderate (90-180 days)', 'Low (180-365 days)', 'Inactive (> 1 year)']
    )
    
    # Calculate average permits per year
    plumber_summary['Years_Active'] = (
        (plumber_summary['Last_Permit_Date'] - plumber_summary['First_Permit_Date']).dt.days / 365.25
    ).round(1)
    plumber_summary['Avg_Permits_Per_Year'] = (
        plumber_summary['Total_Permits'] / plumber_summary['Years_Active'].replace(0, 1)
    ).round(1)
    
    # Clean up work types for readability
    plumber_summary['Top_Work_Types'] = plumber_summary['Top_Work_Types'].apply(
        lambda x: ', '.join([f"{k}: {v}" for k, v in x.items()]) if isinstance(x, dict) else ''
    )
    
    # Sort by total permits (highest volume first)
    plumber_summary = plumber_summary.sort_values('Total_Permits', ascending=False)
    
    # Select and reorder columns for call sheet
    call_sheet_columns = [
        'Company_Name',
        'Contact_Person',
        'Address',
        'City',
        'Total_Permits',
        'Activity_Level',
        'Days_Since_Last_Permit',
        'Avg_Permits_Per_Year',
        'Service_Areas',
        'Top_Work_Types',
        'Total_Fees_Paid',
        'First_Permit_Date',
        'Last_Permit_Date'
    ]
    
    call_sheet = plumber_summary[call_sheet_columns].copy()
    
    # Format dates for readability
    call_sheet['First_Permit_Date'] = call_sheet['First_Permit_Date'].dt.strftime('%Y-%m-%d')
    call_sheet['Last_Permit_Date'] = call_sheet['Last_Permit_Date'].dt.strftime('%Y-%m-%d')
    
    # Round numeric columns
    call_sheet['Total_Fees_Paid'] = call_sheet['Total_Fees_Paid'].round(2)
    
    # Save to CSV with 'Claude' appended
    output_filename = 'plumber_contacts_Claude.csv'
    call_sheet.to_csv(output_filename, index=False)
    print(f"\nSaved plumber contact list to: {output_filename}")
    
    # Create a summary report
    print("\n=== SUMMARY ===")
    print(f"Total unique plumbing companies: {len(call_sheet)}")
    print(f"\nActivity breakdown:")
    print(call_sheet['Activity_Level'].value_counts())
    print(f"\nTop 10 plumbers by permit volume:")
    print(call_sheet[['Company_Name', 'Total_Permits', 'Activity_Level']].head(10).to_string(index=False))
    
    # Also create a filtered version with only active plumbers
    active_plumbers = call_sheet[call_sheet['Days_Since_Last_Permit'] <= 180].copy()
    active_filename = 'plumber_contacts_active_only_Claude.csv'
    active_plumbers.to_csv(active_filename, index=False)
    print(f"\nAlso saved active plumbers only (last 180 days) to: {active_filename}")
    print(f"Active plumbers count: {len(active_plumbers)}")
    
    return call_sheet

if __name__ == "__main__":
    extract_plumber_contacts()