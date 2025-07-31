#!/usr/bin/env python3
"""
Quick view of top contractors with verified contact information
"""

import pandas as pd

# Load the call list
df = pd.read_csv('reports/drill_down_reports/data/plumbing_contractors_call_list.csv')

# Filter for verified contacts only
verified = df[df['Contact_Info_Source'] == 'Licensed Data'].head(20)

print("TOP 20 CONTRACTORS WITH VERIFIED CONTACT INFORMATION")
print("=" * 80)
print(f"{'Company':<40} {'Phone':<15} {'Permits':<10}")
print("-" * 80)

for _, row in verified.iterrows():
    company = row['applicant_name'][:40]
    phone = row['Phone_Number']
    permits = row['total_permits']
    print(f"{company:<40} {phone:<15} {permits:<10,}")

print(f"\nTotal contractors with phone numbers: {len(df)}")
print(f"With verified (licensed) data: {(df['Contact_Info_Source'] == 'Licensed Data').sum()}")
print(f"With generated emails: {(df['Contact_Info_Source'] == 'Generated').sum()}")