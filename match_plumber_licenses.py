#!/usr/bin/env python3
"""
Match plumber permit data with license data to add real contact information
"""

import pandas as pd
import pypdf
import re
from difflib import SequenceMatcher
from collections import defaultdict
import numpy as np

def extract_license_data_from_pdf(pdf_path):
    """Extract all plumber license data from PDF"""
    print(f"Extracting data from {pdf_path}...")
    
    licenses = []
    
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            
            # Split into lines
            lines = text.split('\n')
            
            for line in lines:
                # Skip header line
                if 'License Type' in line and 'Applicant Name' in line:
                    continue
                
                # Look for lines that start with L101 (license pattern)
                if line.strip().startswith('L101'):
                    parts = line.split()
                    
                    # Extract phone number
                    phone_match = re.search(r'(\d{3}-\d{3}-\d{4})', line)
                    phone = phone_match.group(1) if phone_match else None
                    
                    # Extract email
                    email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', line)
                    email = email_match.group(1).lower() if email_match else None
                    
                    # Extract company name (between APPROVED and address/phone)
                    approved_idx = line.find('APPROVED')
                    if approved_idx > 0:
                        after_approved = line[approved_idx + 8:].strip()
                        
                        # Find where address starts (numbers followed by text)
                        address_match = re.search(r'\d+\s+[A-Z]', after_approved)
                        if address_match:
                            company_name = after_approved[:address_match.start()].strip()
                        else:
                            # If no address, find phone or email
                            if phone_match:
                                company_name = after_approved[:after_approved.find(phone)].strip()
                            elif email_match:
                                company_name = after_approved[:after_approved.find(email)].strip()
                            else:
                                company_name = after_approved.strip()
                        
                        # Clean up company name
                        company_name = re.sub(r'\s+', ' ', company_name)
                        
                        if company_name and (phone or email):
                            licenses.append({
                                'license_company': company_name,
                                'license_phone': phone,
                                'license_email': email
                            })
    
    print(f"Extracted {len(licenses)} license records with contact info")
    return pd.DataFrame(licenses)

def normalize_company_name(name):
    """Normalize company name for matching"""
    if pd.isna(name):
        return ""
    
    # Convert to uppercase
    name = str(name).upper()
    
    # Remove common punctuation
    name = re.sub(r'[.,\'"&-]', ' ', name)
    
    # Standardize common abbreviations
    replacements = {
        ' INCORPORATED': ' INC',
        ' CORPORATION': ' CORP',
        ' LIMITED LIABILITY COMPANY': ' LLC',
        ' LIMITED': ' LTD',
        ' COMPANY': ' CO',
        ' AND ': ' & ',
        'PLUMBING': 'PLUMBING',
        'HEATING': 'HEATING',
        'MECHANICAL': 'MECHANICAL'
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    return name

def fuzzy_match_companies(permit_name, license_name, threshold=0.85):
    """Check if two company names are a fuzzy match"""
    # Normalize both names
    norm_permit = normalize_company_name(permit_name)
    norm_license = normalize_company_name(license_name)
    
    # Exact match after normalization
    if norm_permit == norm_license:
        return True, 1.0
    
    # Calculate similarity
    similarity = SequenceMatcher(None, norm_permit, norm_license).ratio()
    
    # Check if one name contains the other (for subsidiaries)
    if norm_permit in norm_license or norm_license in norm_permit:
        similarity = max(similarity, 0.9)
    
    # Special case for very similar names
    if similarity >= threshold:
        return True, similarity
    
    # Check core business name (remove INC, LLC, etc)
    core_words = ['INC', 'LLC', 'CORP', 'LTD', 'CO', 'COMPANY', 'CORPORATION', 'LIMITED']
    
    permit_core = norm_permit
    license_core = norm_license
    
    for word in core_words:
        permit_core = permit_core.replace(word, '').strip()
        license_core = license_core.replace(word, '').strip()
    
    if permit_core and license_core:
        core_similarity = SequenceMatcher(None, permit_core, license_core).ratio()
        if core_similarity >= 0.9:
            return True, core_similarity
    
    return False, similarity

def match_and_update_contacts():
    """Match permit data with license data and update contact information"""
    
    # Load the active plumbers data
    print("\nLoading active plumber data...")
    df = pd.read_csv('plumber_contacts_active_last_year_with_contact_info.csv')
    print(f"Loaded {len(df)} active plumbers")
    
    # Extract license data
    license_df = extract_license_data_from_pdf('PLumbingLicenses.pdf')
    
    # Track matches
    match_stats = {
        'exact_matches': 0,
        'fuzzy_matches': 0,
        'no_matches': 0,
        'phone_added': 0,
        'email_added': 0
    }
    
    # Create columns for tracking
    df['Matched_License_Company'] = None
    df['Match_Confidence'] = None
    df['License_Phone'] = None
    df['License_Email'] = None
    
    print("\nMatching companies...")
    
    for idx, row in df.iterrows():
        permit_company = row['Company_Name']
        best_match = None
        best_score = 0
        
        # Try to find a match in license data
        for _, license_row in license_df.iterrows():
            is_match, score = fuzzy_match_companies(permit_company, license_row['license_company'])
            
            if is_match and score > best_score:
                best_match = license_row
                best_score = score
        
        # Update data if match found
        if best_match is not None:
            df.at[idx, 'Matched_License_Company'] = best_match['license_company']
            df.at[idx, 'Match_Confidence'] = f"{best_score:.2f}"
            
            if best_match['license_phone']:
                df.at[idx, 'License_Phone'] = best_match['license_phone']
                match_stats['phone_added'] += 1
                
            if best_match['license_email']:
                df.at[idx, 'License_Email'] = best_match['license_email']
                match_stats['email_added'] += 1
            
            if best_score == 1.0:
                match_stats['exact_matches'] += 1
            else:
                match_stats['fuzzy_matches'] += 1
        else:
            match_stats['no_matches'] += 1
    
    # Update the main phone and email columns
    # Use license data where available, otherwise keep generated emails
    df['Phone_Number'] = df['License_Phone']
    df['Email'] = df.apply(lambda x: x['License_Email'] if pd.notna(x['License_Email']) 
                           else x['Email'], axis=1)
    
    # Update contact info source
    df['Contact_Info_Source'] = df.apply(
        lambda x: 'Licensed Data' if pd.notna(x['License_Phone']) or pd.notna(x['License_Email'])
        else x['Contact_Info_Source'], axis=1
    )
    
    # Update confidence
    df['Contact_Confidence'] = df.apply(
        lambda x: 'High' if x['Contact_Info_Source'] == 'Licensed Data'
        else x['Contact_Confidence'], axis=1
    )
    
    # Sort by contact availability then permits
    # Create sort keys
    df['has_phone'] = df['Phone_Number'].notna()
    df['has_email'] = df['Email'].notna()
    df['has_both'] = df['has_phone'] & df['has_email']
    
    # Sort: both > either > none, then by permits
    df = df.sort_values(
        ['has_both', 'has_phone', 'has_email', 'Total_Permits'],
        ascending=[False, False, False, False]
    )
    
    # Remove temporary columns
    df = df.drop(columns=['has_phone', 'has_email', 'has_both'])
    
    # Clean up columns for final output
    final_columns = [
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
        'Matched_License_Company',
        'Match_Confidence',
        'Service_Areas',
        'Top_Work_Types',
        'Total_Fees_Paid',
        'First_Permit_Date',
        'Last_Permit_Date'
    ]
    
    df = df[final_columns]
    
    # Save main file
    output_file = 'plumber_contacts_with_verified_info.csv'
    df.to_csv(output_file, index=False)
    print(f"\nSaved updated contacts to: {output_file}")
    
    # Create call-ready file (only with phone numbers)
    call_ready = df[df['Phone_Number'].notna()].copy()
    call_ready_file = 'plumber_contacts_ready_to_call.csv'
    call_ready.to_csv(call_ready_file, index=False)
    print(f"Saved call-ready list to: {call_ready_file}")
    
    # Print statistics
    print("\n=== MATCH STATISTICS ===")
    print(f"Total companies processed: {len(df)}")
    print(f"Exact matches: {match_stats['exact_matches']}")
    print(f"Fuzzy matches: {match_stats['fuzzy_matches']}")
    print(f"No matches: {match_stats['no_matches']}")
    print(f"Total matched: {match_stats['exact_matches'] + match_stats['fuzzy_matches']} "
          f"({(match_stats['exact_matches'] + match_stats['fuzzy_matches'])/len(df)*100:.1f}%)")
    print(f"\nContact info added:")
    print(f"Phone numbers: {match_stats['phone_added']}")
    print(f"Email addresses: {match_stats['email_added']}")
    
    # Summary of final data
    print("\n=== FINAL DATA SUMMARY ===")
    print(f"Records with phone numbers: {df['Phone_Number'].notna().sum()} "
          f"({df['Phone_Number'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Records with emails: {df['Email'].notna().sum()} "
          f"({df['Email'].notna().sum()/len(df)*100:.1f}%)")
    print(f"Records with both: {(df['Phone_Number'].notna() & df['Email'].notna()).sum()} "
          f"({(df['Phone_Number'].notna() & df['Email'].notna()).sum()/len(df)*100:.1f}%)")
    
    # Show top companies with verified contact info
    print("\n=== TOP 10 COMPANIES WITH VERIFIED CONTACT INFO ===")
    top_verified = df[df['Contact_Info_Source'] == 'Licensed Data'].head(10)
    print(top_verified[['Company_Name', 'Phone_Number', 'Email', 'Total_Permits']].to_string(index=False))
    
    return df

if __name__ == "__main__":
    match_and_update_contacts()