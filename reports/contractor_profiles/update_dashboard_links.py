#!/usr/bin/env python3
"""
Update the contractor dashboard to add clickable links to contractor detail pages
"""

import json
import re
from pathlib import Path


def clean_company_name(name):
    """Clean company name for file naming (same as in contractor_research.py)"""
    clean_name = re.sub(r'[^\w\s-]', '', name)
    clean_name = re.sub(r'[-\s]+', '_', clean_name)
    return clean_name.lower()


def update_dashboard():
    """Update the contractor dashboard HTML to add links to detail pages"""
    
    # Load the contractor index to know which contractors have detail pages
    index_path = Path("contractor_profiles/contractor_index.json")
    with open(index_path, 'r') as f:
        contractor_index = json.load(f)
    
    # Create a mapping of company names to their HTML files
    company_to_html = {
        item['company_name']: item['html_file'] 
        for item in contractor_index
    }
    
    # Read the dashboard HTML
    dashboard_path = Path("../drill_down_reports/contractor_contact_dashboard_live.html")
    with open(dashboard_path, 'r') as f:
        html_content = f.read()
    
    # Create list of companies with detail pages
    companies_with_details = list(company_to_html.keys())
    companies_json = json.dumps(companies_with_details)
    
    # Find the row.innerHTML assignment
    row_innerHTML_pattern = r"(row\.innerHTML = `\s*<td>\$\{contractor\.company\}</td>)"
    
    if row_innerHTML_pattern not in html_content and not re.search(row_innerHTML_pattern, html_content):
        # Try to find the exact pattern
        match = re.search(r'row\.innerHTML = `([^`]+)`', html_content)
        if match:
            old_row_content = match.group(1)
            # Replace the company cell
            new_row_content = old_row_content.replace(
                '<td>${contractor.company}</td>',
                '<td>${getCompanyLink(contractor.company)}</td>'
            )
            html_content = html_content.replace(
                f'row.innerHTML = `{old_row_content}`',
                f'row.innerHTML = `{new_row_content}`'
            )
    
    # Add the helper functions after contractorData
    helper_functions = f'''
        // List of contractors with detail pages
        const contractorsWithDetails = {companies_json};
        
        // Helper function to convert company name to filename
        function getContractorFileName(companyName) {{
            const cleanName = companyName
                .replace(/[^\\w\\s-]/g, '')
                .replace(/[-\\s]+/g, '_')
                .toLowerCase();
            return cleanName + '.html';
        }}
        
        // Helper function to get company link or plain text
        function getCompanyLink(companyName) {{
            if (contractorsWithDetails.includes(companyName)) {{
                const fileName = getContractorFileName(companyName);
                return `<a href="../contractor_profiles/contractor_profiles/${{fileName}}" 
                        style="color: #1565c0; text-decoration: none; font-weight: 500;"
                        onmouseover="this.style.textDecoration='underline'" 
                        onmouseout="this.style.textDecoration='none'">${{companyName}}</a>`;
            }}
            return companyName;
        }}
        '''
    
    # Find where to insert the helper functions (after contractorData definition)
    contractor_data_end = html_content.find('const contractorData = [')
    if contractor_data_end != -1:
        # Find the end of the contractorData array
        bracket_count = 0
        start_pos = html_content.find('[', contractor_data_end)
        for i in range(start_pos, len(html_content)):
            if html_content[i] == '[':
                bracket_count += 1
            elif html_content[i] == ']':
                bracket_count -= 1
                if bracket_count == 0:
                    insert_pos = html_content.find(';', i) + 1
                    break
        
        # Insert the helper functions
        html_content = html_content[:insert_pos] + '\n' + helper_functions + html_content[insert_pos:]
    
    # No need to replace row rendering since we're modifying cell creation directly
    
    # Add some CSS for better link styling if not already present
    if 'contractor-link' not in html_content:
        css_addition = '''
        /* Contractor detail page links */
        .contractor-link {
            color: #1565c0;
            text-decoration: none;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        
        .contractor-link:hover {
            text-decoration: underline;
            color: #0d47a1;
        }
        '''
        
        # Insert before closing </style> tag
        style_close_pos = html_content.rfind('</style>')
        if style_close_pos != -1:
            html_content = html_content[:style_close_pos] + css_addition + html_content[style_close_pos:]
    
    # Save the updated dashboard
    output_path = Path("../drill_down_reports/contractor_contact_dashboard_live_updated.html")
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    print(f"✅ Dashboard updated successfully!")
    print(f"📁 Saved to: {output_path}")
    print(f"🔗 Added links for {len(company_to_html)} contractors")
    
    # Also update the original file
    with open(dashboard_path, 'w') as f:
        f.write(html_content)
    print(f"✅ Original dashboard also updated: {dashboard_path}")


if __name__ == "__main__":
    update_dashboard()