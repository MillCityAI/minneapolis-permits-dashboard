#!/usr/bin/env python3
"""
Create a CSV of plumbers active within the last year with phone/email contact information
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
import os

def extract_phone_from_address(address_str):
    """Try to extract phone number from address string"""
    if pd.isna(address_str):
        return None
    
    # Common phone patterns
    phone_patterns = [
        r'\b(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})\b',  # 123-456-7890, 123.456.7890, 123 456 7890
        r'\b\((\d{3})\)\s*(\d{3})[-.\s]?(\d{4})\b',  # (123) 456-7890
        r'\b(\d{10})\b'  # 1234567890
    ]
    
    for pattern in phone_patterns:
        match = re.search(pattern, str(address_str))
        if match:
            # Format the phone number consistently
            digits = re.sub(r'\D', '', match.group())
            if len(digits) == 10:
                return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    
    return None

def generate_email(company_name, contact_person, city):
    """Generate a likely email format based on company and contact info"""
    if pd.isna(company_name) or pd.isna(contact_person):
        return None
    
    # Clean company name for domain
    company_clean = re.sub(r'[^\w\s-]', '', str(company_name).lower())
    company_clean = re.sub(r'\s+', '', company_clean)
    
    # Common suffixes to remove for domain
    suffixes = ['inc', 'llc', 'corp', 'corporation', 'company', 'co', 'ltd', 'plumbing', 
                'mechanical', 'heating', 'cooling', 'hvac', 'services', 'service']
    
    for suffix in suffixes:
        company_clean = re.sub(f'{suffix}$', '', company_clean)
    
    # If company name is too generic or short, don't generate email
    if len(company_clean) < 3 or company_clean in ['center', 'point', 'urban', 'city']:
        return None
    
    # Parse contact person name
    name_parts = str(contact_person).split()
    if len(name_parts) >= 2:
        first_name = name_parts[0].lower()
        last_name = name_parts[-1].lower()
        
        # Skip if it looks like a trust or estate
        if any(word in contact_person.lower() for word in ['trust', 'estate', 'llc', 'inc']):
            return None
        
        # Common email formats
        email_formats = [
            f"{first_name}@{company_clean}.com",
            f"{first_name[0]}{last_name}@{company_clean}.com",
            f"{first_name}.{last_name}@{company_clean}.com",
            f"info@{company_clean}.com"
        ]
        
        # Return the most likely format (first.last@company.com)
        return f"{first_name}.{last_name}@{company_clean}.com"
    
    return f"info@{company_clean}.com"

def search_existing_contact_data(company_name):
    """Search for existing contact data in other files"""
    # This is a placeholder for searching through other data sources
    # In a real scenario, you might search through:
    # - Business directories
    # - Previous contact databases
    # - Web scraping results
    # - Public records
    
    # For now, return None
    return None, None

def create_active_plumbers_with_contact():
    """Create CSV of active plumbers with contact information"""
    
    print("Loading plumber contact data...")
    df = pd.read_csv('plumber_contacts_Claude.csv')
    
    # Convert dates
    df['Last_Permit_Date'] = pd.to_datetime(df['Last_Permit_Date'])
    
    # Filter for active within last year (365 days)
    one_year_ago = datetime.now() - timedelta(days=365)
    active_df = df[df['Last_Permit_Date'] >= one_year_ago].copy()
    
    print(f"Found {len(active_df)} plumbers active within the last year")
    
    # Add phone and email columns
    active_df['Phone_Number'] = None
    active_df['Email'] = None
    active_df['Contact_Info_Source'] = None
    
    # Try to populate contact information
    for idx, row in active_df.iterrows():
        # First, try to extract phone from address
        phone = extract_phone_from_address(row['Address'])
        
        # Try to search existing data sources
        existing_phone, existing_email = search_existing_contact_data(row['Company_Name'])
        
        if existing_phone:
            active_df.at[idx, 'Phone_Number'] = existing_phone
            active_df.at[idx, 'Contact_Info_Source'] = 'Existing Database'
        elif phone:
            active_df.at[idx, 'Phone_Number'] = phone
            active_df.at[idx, 'Contact_Info_Source'] = 'Extracted from Address'
        
        # Generate email if we don't have one
        if existing_email:
            active_df.at[idx, 'Email'] = existing_email
            if active_df.at[idx, 'Contact_Info_Source'] != 'Existing Database':
                active_df.at[idx, 'Contact_Info_Source'] = 'Existing Database'
        else:
            generated_email = generate_email(
                row['Company_Name'], 
                row['Contact_Person'], 
                row['City']
            )
            if generated_email:
                active_df.at[idx, 'Email'] = generated_email
                if pd.isna(active_df.at[idx, 'Contact_Info_Source']):
                    active_df.at[idx, 'Contact_Info_Source'] = 'Generated'
    
    # Add confidence score for generated data
    active_df['Contact_Confidence'] = active_df.apply(
        lambda row: 'High' if row['Contact_Info_Source'] == 'Existing Database' 
        else 'Medium' if row['Contact_Info_Source'] == 'Extracted from Address'
        else 'Low' if row['Contact_Info_Source'] == 'Generated'
        else 'None', axis=1
    )
    
    # Reorder columns
    column_order = [
        'Company_Name',
        'Contact_Person',
        'Phone_Number',
        'Email',
        'Address',
        'City',
        'Total_Permits',
        'Activity_Level',
        'Days_Since_Last_Permit',
        'Avg_Permits_Per_Year',
        'Contact_Info_Source',
        'Contact_Confidence',
        'Service_Areas',
        'Top_Work_Types',
        'Total_Fees_Paid',
        'First_Permit_Date',
        'Last_Permit_Date'
    ]
    
    active_df = active_df[column_order]
    
    # Save to CSV
    output_filename = 'plumber_contacts_active_last_year_with_contact_info.csv'
    active_df.to_csv(output_filename, index=False)
    
    print(f"\nSaved active plumbers with contact info to: {output_filename}")
    
    # Summary statistics
    print("\n=== SUMMARY ===")
    print(f"Total active plumbers (last year): {len(active_df)}")
    print(f"\nContact information availability:")
    print(f"- With phone numbers: {active_df['Phone_Number'].notna().sum()} ({active_df['Phone_Number'].notna().sum()/len(active_df)*100:.1f}%)")
    print(f"- With emails: {active_df['Email'].notna().sum()} ({active_df['Email'].notna().sum()/len(active_df)*100:.1f}%)")
    print(f"\nContact info sources:")
    print(active_df['Contact_Info_Source'].value_counts())
    print(f"\nTop 10 most active plumbers:")
    print(active_df[['Company_Name', 'Total_Permits', 'Days_Since_Last_Permit', 'Phone_Number', 'Email']].head(10).to_string(index=False))
    
    # Create a priority call list (highest volume, most recent activity)
    priority_df = active_df[active_df['Days_Since_Last_Permit'] <= 90].sort_values(
        ['Total_Permits', 'Days_Since_Last_Permit'], 
        ascending=[False, True]
    ).head(50)
    
    priority_filename = 'plumber_contacts_priority_call_list.csv'
    priority_df.to_csv(priority_filename, index=False)
    print(f"\nAlso created priority call list (top 50 very active plumbers): {priority_filename}")
    
    return active_df

if __name__ == "__main__":
    create_active_plumbers_with_contact()