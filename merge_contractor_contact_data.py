#!/usr/bin/env python3
"""
Merge verified contact information with existing plumbing contractor data
"""

import pandas as pd
import os

def merge_contractor_contacts():
    """Merge verified contact data with plumbing applicant data"""
    
    print("Loading data files...")
    
    # Load the verified contact data
    contacts_df = pd.read_csv('plumber_contacts_with_verified_info.csv')
    
    # Check if plumbing applicants file exists
    applicant_file = 'reports/drill_down_reports/data/plumbing_all_applicants.csv'
    if os.path.exists(applicant_file):
        applicants_df = pd.read_csv(applicant_file)
        print(f"Loaded {len(applicants_df)} applicant records")
    else:
        print(f"Warning: {applicant_file} not found. Creating from contacts data...")
        # Create a basic applicants structure from contacts data
        applicants_df = contacts_df.copy()
        applicants_df['applicant_name'] = applicants_df['Company_Name']
        applicants_df['applicant_type'] = 'Contractor'
        applicants_df['total_permits'] = applicants_df['Total_Permits']
        applicants_df['completion_rate'] = 90.0  # Default
        applicants_df['abandonment_rate'] = 0.5  # Default
        applicants_df['primary_use_case'] = applicants_df['Top_Work_Types'].str.split(':').str[0]
    
    # Normalize company names for matching
    contacts_df['normalized_name'] = contacts_df['Company_Name'].str.upper().str.strip()
    applicants_df['normalized_name'] = applicants_df['applicant_name'].str.upper().str.strip()
    
    # Merge the data
    print("\nMerging contact information...")
    merged_df = applicants_df.merge(
        contacts_df[['normalized_name', 'Phone_Number', 'Email', 'Contact_Person', 
                     'Contact_Info_Source', 'Contact_Confidence', 'Matched_License_Company',
                     'Match_Confidence', 'Days_Since_Last_Permit', 'Activity_Level']],
        on='normalized_name',
        how='left'
    )
    
    # Fill in missing values
    merged_df['Phone_Number'] = merged_df['Phone_Number'].fillna('')
    merged_df['Email'] = merged_df['Email'].fillna('')
    merged_df['Contact_Person'] = merged_df['Contact_Person'].fillna('')
    merged_df['Contact_Info_Source'] = merged_df['Contact_Info_Source'].fillna('None')
    merged_df['Contact_Confidence'] = merged_df['Contact_Confidence'].fillna('None')
    
    # Create directory if it doesn't exist
    os.makedirs('reports/drill_down_reports/data', exist_ok=True)
    
    # Save the merged data
    output_file = 'reports/drill_down_reports/data/plumbing_contractors_with_contacts.csv'
    merged_df.to_csv(output_file, index=False)
    print(f"\nSaved merged data to: {output_file}")
    
    # Create call list (contractors with phone numbers)
    call_list = merged_df[
        (merged_df['Phone_Number'] != '') & 
        (merged_df['applicant_type'] == 'Contractor')
    ].sort_values('total_permits', ascending=False)
    
    call_list_file = 'reports/drill_down_reports/data/plumbing_contractors_call_list.csv'
    call_list.to_csv(call_list_file, index=False)
    print(f"Saved call list to: {call_list_file}")
    
    # Print statistics
    contractors = merged_df[merged_df['applicant_type'] == 'Contractor']
    print("\n=== CONTACT STATISTICS ===")
    print(f"Total contractors: {len(contractors)}")
    print(f"Contractors with phone: {(contractors['Phone_Number'] != '').sum()}")
    print(f"Contractors with email: {(contractors['Email'] != '').sum()}")
    print(f"Contractors with both: {((contractors['Phone_Number'] != '') & (contractors['Email'] != '')).sum()}")
    
    return merged_df

if __name__ == "__main__":
    merge_contractor_contacts()