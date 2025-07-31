#!/usr/bin/env python3
"""
Upload plumber contacts to Google Sheets
"""

import pandas as pd
import time

def prepare_csv_for_sheets():
    """Read CSV and prepare data for Google Sheets upload"""
    
    print("Reading plumber contacts CSV...")
    df = pd.read_csv('plumber_contacts_Claude.csv')
    
    # Convert all data to strings to avoid any type issues
    for col in df.columns:
        df[col] = df[col].astype(str).replace('nan', '')
    
    # Save as a temporary CSV with proper formatting
    temp_filename = 'plumber_contacts_for_sheets.csv'
    df.to_csv(temp_filename, index=False)
    
    print(f"Prepared {len(df)} rows for upload")
    print(f"Saved to temporary file: {temp_filename}")
    
    # Show sample of data
    print("\nFirst 5 rows:")
    print(df.head())
    
    return temp_filename, len(df)

if __name__ == "__main__":
    temp_file, row_count = prepare_csv_for_sheets()
    
    print(f"\n✅ Data prepared for Google Sheets upload")
    print(f"   Total rows: {row_count}")
    print(f"   Temporary file: {temp_file}")
    print("\nThe file is ready to be uploaded to Google Sheets.")