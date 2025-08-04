#!/usr/bin/env python3
"""
Update all contractor HTML pages with the simplified template
"""

import json
import os
from pathlib import Path
import re
from datetime import datetime


def update_contractor_page(json_file_path, template_path, output_dir):
    """Update a single contractor page with the simplified template"""
    
    # Load contractor data
    with open(json_file_path, 'r') as f:
        contractor_data = json.load(f)
    
    # Load the simplified template
    with open(template_path, 'r') as f:
        template = f.read()
    
    # Format values for display
    def format_currency(value):
        try:
            return f"{float(value):,.0f}"
        except:
            return "0"
    
    def format_list(items):
        if isinstance(items, list):
            return ", ".join(str(item) for item in items if item)
        return str(items) if items else "Not Available"
    
    # Extract data from JSON
    company_info = contractor_data.get('company_info', {})
    contact_info = contractor_data.get('contact_info', {})
    location_info = contractor_data.get('location_info', {})
    performance = contractor_data.get('performance_metrics', {}).get('permit_data', {})
    metadata = contractor_data.get('metadata', {})
    
    # Prepare replacements
    replacements = {
        '{COMPANY_NAME}': company_info.get('company_name', 'Unknown Company'),
        '{LAST_UPDATED}': datetime.now().strftime('%B %d, %Y'),
        '{CONTACT_PERSON}': contact_info.get('primary_contact', {}).get('name') or 'Not Available',
        '{PHONE_NUMBER}': contact_info.get('main_phone') or 'Not Available',
        '{EMAIL}': contact_info.get('emails', {}).get('general') or 'Not Available',
        '{ADDRESS}': location_info.get('primary_address', {}).get('street') or 'Not Available',
        '{CITY}': location_info.get('primary_address', {}).get('city') or 'Minneapolis',
        '{TOTAL_PERMITS}': str(performance.get('total_permits', 0)),
        '{AVG_PERMITS_YEAR}': f"{performance.get('avg_permits_per_year', 0):.1f}",
        '{DAYS_SINCE_LAST}': str(performance.get('days_since_last_permit', 0)),
        '{TOTAL_FEES}': format_currency(performance.get('total_fees_paid', 0)),
        '{LEGAL_NAME}': company_info.get('legal_name') or company_info.get('company_name', 'Unknown'),
        '{LICENSE_MATCH}': metadata.get('verification_status', 'Not Verified'),
        '{CONTACT_CONFIDENCE}': metadata.get('verification_status', 'Unknown'),
        '{DATA_SOURCE}': metadata.get('data_source', 'Minneapolis Permits Database'),
        '{SPECIALTIES}': format_list(contractor_data.get('business_details', {}).get('specialties', ['Plumbing Services'])),
        '{TOP_WORK_TYPES}': format_list(performance.get('top_work_types', ['General Plumbing'])),
        '{ACTIVITY_LEVEL}': performance.get('activity_level', 'Unknown'),
        '{FIRST_PERMIT_DATE}': performance.get('first_permit_date', 'Not Available'),
        '{LAST_PERMIT_DATE}': performance.get('last_permit_date', 'Not Available'),
        '{SERVICE_AREAS}': format_list(location_info.get('service_areas', ['Minneapolis Area']))
    }
    
    # Replace all placeholders
    html_content = template
    for placeholder, value in replacements.items():
        html_content = html_content.replace(placeholder, str(value))
    
    # Generate output filename
    company_name = company_info.get('company_name', 'unknown')
    clean_name = re.sub(r'[^\w\s-]', '', company_name)
    clean_name = re.sub(r'[-\s]+', '_', clean_name).lower()
    output_file = os.path.join(output_dir, f"{clean_name}.html")
    
    # Write the updated HTML
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    return output_file, company_name


def main():
    """Update all contractor pages with the simplified template"""
    
    # Paths
    profiles_dir = Path("contractor_profiles")
    template_path = Path("contractor_detail_simple.html")
    
    # Find all contractor JSON files
    json_files = list(profiles_dir.glob("*_data.json"))
    
    print(f"Found {len(json_files)} contractor data files to process")
    
    # Process each contractor
    updated_count = 0
    for json_file in json_files:
        try:
            output_file, company_name = update_contractor_page(
                json_file, 
                template_path,
                profiles_dir
            )
            print(f"✓ Updated: {company_name}")
            updated_count += 1
        except Exception as e:
            print(f"✗ Error processing {json_file}: {str(e)}")
    
    print(f"\n✅ Successfully updated {updated_count} contractor pages")
    print("📁 All pages are now using the simplified template")
    print("🚀 Ready for immediate use - no backend required!")


if __name__ == "__main__":
    main()