#!/usr/bin/env python3
"""
Process the missing contractors with corrected names
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
    """Process the missing contractors with corrected names"""
    
    # Missing contractors with their actual names in the database
    missing_contractors = [
        "Horwitz LLC",  # Found as "Horwitz LLC" - exact match should work
        "Norblom Plumbing Co",  # Found as "Norblom Plumbing Co" - exact match should work
        "Budget Plumbing Corp",  # Found similar as "Budget Plumbing Corp"
        "Barr Web Industries Inc",  # Similar to "Bar Web Piperite Plumbing"
    ]
    
    # Path to the contractor CSV file
    csv_path = "/home/pds/millcityai/Research/plumber_contacts_with_verified_info.csv"
    
    # Create researcher instance
    researcher = ContractorResearcher(csv_path)
    
    print(f"Processing {len(missing_contractors)} missing contractors...")
    
    # Load the CSV data
    df = pd.read_csv(csv_path)
    
    # Find matching contractors
    found_contractors = []
    not_found = []
    
    for contractor_name in missing_contractors:
        # Try exact match first
        exact_match = df[df['Company_Name'].str.strip() == contractor_name.strip()]
        
        if not exact_match.empty:
            found_contractors.append(exact_match.iloc[0])
            print(f"✓ Found: {contractor_name}")
            continue
        
        # Try case-insensitive match
        case_match = df[df['Company_Name'].str.lower().str.strip() == contractor_name.lower().strip()]
        
        if not case_match.empty:
            found_contractors.append(case_match.iloc[0])
            print(f"✓ Found: {contractor_name} (case insensitive)")
            continue
            
        not_found.append(contractor_name)
        print(f"✗ Not found: {contractor_name}")
    
    # Process found contractors
    if found_contractors:
        print(f"\nProcessing {len(found_contractors)} contractors...")
        results = []
        
        for contractor_row in found_contractors:
            result = researcher.process_contractor(contractor_row)
            results.append(result)
            time.sleep(0.5)
        
        # Update the index file
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
        
        print(f"\n✅ Successfully processed {len(results)} additional contractors!")
        print(f"📁 Updated index with {len(existing_index)} total contractors")
        
        # Update dashboard links
        print("\n🔗 Updating dashboard links...")
        from update_dashboard_links import update_dashboard
        update_dashboard()
        
    else:
        print("\nNo additional contractors found to process.")


if __name__ == "__main__":
    main()