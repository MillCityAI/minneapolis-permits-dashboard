#!/usr/bin/env python3
"""
Process specific contractors requested by user
"""

import json
import pandas as pd
import os
from datetime import datetime
import re
from typing import Dict, List, Optional
import time
from contractor_research import ContractorResearcher


def main():
    """Process the specific contractors requested by the user"""
    
    # List of contractors to process (as provided by user)
    requested_contractors = [
        "Horowitz LLC",
        "Weld and Sons Plumbing", 
        "Norblum Plumbing",
        "Champion Plumbing",
        "Grabau Plumbing",
        "Peters Plumbing", 
        "Master Plumbing Services",
        "Gilbert Mechanical",
        "Eric Nelson Plumbing",
        "Good Almond Construction and Maintenance",
        "Northern Mechanical Contractors",
        "Northern Air Corp",
        "Budget Plumbing Company",
        "Denius Plumbing Company",
        "T.J.K. Plumbing",
        "Bar Web Piperite Plumbing",
        "Liberty Plumbing"
    ]
    
    # Path to the contractor CSV file
    csv_path = "/home/pds/millcityai/Research/plumber_contacts_with_verified_info.csv"
    
    # Create researcher instance
    researcher = ContractorResearcher(csv_path)
    
    print(f"Looking for {len(requested_contractors)} specific contractors...")
    print("Requested contractors:")
    for i, name in enumerate(requested_contractors, 1):
        print(f"  {i:2d}. {name}")
    
    # Load the CSV data
    df = pd.read_csv(csv_path)
    
    # Find matching contractors
    found_contractors = []
    not_found = []
    
    for requested_name in requested_contractors:
        # Try exact match first
        exact_match = df[df['Company_Name'].str.strip() == requested_name.strip()]
        
        if not exact_match.empty:
            found_contractors.append((requested_name, exact_match.iloc[0]))
            continue
        
        # Try case-insensitive match
        case_match = df[df['Company_Name'].str.lower().str.strip() == requested_name.lower().strip()]
        
        if not case_match.empty:
            found_contractors.append((requested_name, case_match.iloc[0]))
            continue
            
        # Try partial matching for common variations
        variations_to_try = [
            requested_name.replace(" LLC", "").strip(),
            requested_name.replace(" Inc", "").strip(), 
            requested_name.replace(" Plumbing", "").strip(),
            requested_name.replace("Plumbing ", "").strip(),
            requested_name + " LLC",
            requested_name + " Inc",
            requested_name + " Co",
        ]
        
        found_variation = False
        for variation in variations_to_try:
            partial_match = df[df['Company_Name'].str.contains(variation, case=False, na=False, regex=False)]
            if not partial_match.empty:
                print(f"  Found '{requested_name}' as '{partial_match.iloc[0]['Company_Name']}'")
                found_contractors.append((requested_name, partial_match.iloc[0]))
                found_variation = True
                break
        
        if not found_variation:
            not_found.append(requested_name)
    
    print(f"\n✅ Found {len(found_contractors)} contractors")
    print(f"❌ Could not find {len(not_found)} contractors")
    
    if not_found:
        print("\nContractors not found:")
        for name in not_found:
            print(f"  - {name}")
        
        # Show similar company names for manual verification
        print("\nSimilar company names in database:")
        for name in not_found:
            similar = df[df['Company_Name'].str.contains(name.split()[0], case=False, na=False)]
            if not similar.empty:
                print(f"\n  Similar to '{name}':")
                for _, row in similar.head(3).iterrows():
                    print(f"    - {row['Company_Name']}")
    
    # Process found contractors
    if found_contractors:
        print(f"\nProcessing {len(found_contractors)} contractors...")
        results = []
        
        for requested_name, contractor_row in found_contractors:
            print(f"\nProcessing: {contractor_row['Company_Name']} (requested as: {requested_name})")
            result = researcher.process_contractor(contractor_row)
            results.append(result)
            time.sleep(0.5)  # Be respectful with any future API calls
        
        # Update the index file with all contractors (existing + new)
        existing_index_path = "contractor_profiles/contractor_index.json"
        if os.path.exists(existing_index_path):
            with open(existing_index_path, 'r') as f:
                existing_index = json.load(f)
        else:
            existing_index = []
        
        # Add new contractors to index
        for result in results:
            clean_name = researcher.clean_company_name(result['company_info']['company_name'])
            new_entry = {
                'company_name': result['company_info']['company_name'],
                'total_permits': result['performance_metrics']['permit_data']['total_permits'],
                'phone': result['contact_info']['main_phone'],
                'html_file': f"{clean_name}.html",
                'json_file': f"{clean_name}_data.json"
            }
            
            # Check if already exists (avoid duplicates)
            exists = any(entry['company_name'] == new_entry['company_name'] for entry in existing_index)
            if not exists:
                existing_index.append(new_entry)
        
        # Sort by total permits descending
        existing_index.sort(key=lambda x: x['total_permits'], reverse=True)
        
        # Save updated index
        with open(existing_index_path, 'w') as f:
            json.dump(existing_index, f, indent=2)
        
        print(f"\n✅ Successfully processed {len(results)} contractors!")
        print(f"📁 Updated index with {len(existing_index)} total contractors")
        print(f"📁 Files saved in: contractor_profiles/")
        
        # Update dashboard links
        print("\n🔗 Updating dashboard links...")
        from update_dashboard_links import update_dashboard
        update_dashboard()


if __name__ == "__main__":
    main()