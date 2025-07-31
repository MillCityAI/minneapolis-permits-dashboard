#!/usr/bin/env python3
"""
Prepare active plumbers data for batch upload to Google Sheets
"""

import pandas as pd
import json

def prepare_batch_data():
    """Prepare active plumbers data in batches for Google Sheets"""
    
    # Read the active plumbers CSV
    df = pd.read_csv('plumber_contacts_active_only_Claude.csv')
    
    # Select top 20 active plumbers (most active based on permit volume)
    top_plumbers = df.head(20)
    
    # Create formatted output for each row
    rows_output = []
    for idx, row in top_plumbers.iterrows():
        row_text = f"""Row {idx + 2}:
Company: {row['Company_Name']}
Contact: {row['Contact_Person']}
Address: {row['Address']}
City: {row['City']}
Total Permits: {row['Total_Permits']}
Activity Level: {row['Activity_Level']}
Days Since Last: {row['Days_Since_Last_Permit']}
Avg Per Year: {row['Avg_Permits_Per_Year']}
Service Areas: {row['Service_Areas'][:100]}...
Top Work Types: {row['Top_Work_Types']}
Total Fees: ${row['Total_Fees_Paid']:,.2f}
First Permit: {row['First_Permit_Date']}
Last Permit: {row['Last_Permit_Date']}
"""
        rows_output.append(row_text)
    
    # Save to file for reference
    with open('active_plumbers_batch.txt', 'w') as f:
        f.write('\n'.join(rows_output))
    
    print(f"Prepared {len(top_plumbers)} active plumber records")
    print("\nTop 5 most active plumbers by permit volume:")
    print(top_plumbers[['Company_Name', 'Total_Permits', 'Activity_Level', 'City']].head())
    
    return top_plumbers

if __name__ == "__main__":
    prepare_batch_data()