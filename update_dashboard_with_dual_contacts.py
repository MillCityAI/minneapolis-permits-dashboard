#!/usr/bin/env python3
"""
Update the contractor dashboard to show both permit contact person and license contact person
"""

import pandas as pd
import os

def update_contact_data():
    """Add license contact person column to the existing data"""
    
    # Load the current data
    print("Loading current contractor data...")
    df = pd.read_csv('plumber_contacts_with_verified_info.csv')
    
    # Add a new column for license contact person
    # Since the PDF doesn't contain individual names, we'll mark as "Not Available"
    df['License_Contact_Person'] = 'Not Available'
    
    # Rename the existing Contact_Person to be more specific
    df.rename(columns={'Contact_Person': 'Permit_Contact_Person'}, inplace=True)
    
    # Reorder columns to put contact persons together
    columns_order = [
        'Company_Name',
        'Permit_Contact_Person',
        'License_Contact_Person',
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
    
    df = df[columns_order]
    
    # Save the updated data
    output_file = 'plumber_contacts_dual_contacts.csv'
    df.to_csv(output_file, index=False)
    print(f"Saved updated data to: {output_file}")
    
    # Also update the call list
    call_ready = df[df['Phone_Number'].notna()].copy()
    call_ready_file = 'reports/drill_down_reports/data/plumbing_contractors_call_list.csv'
    
    # Rename columns for the dashboard format
    call_ready.rename(columns={
        'Company_Name': 'applicant_name',
        'Total_Permits': 'total_permits',
        'Last_Permit_Date': 'last_permit_date',
        'Activity_Level': 'activity_level'
    }, inplace=True)
    
    # Save the call list
    os.makedirs('reports/drill_down_reports/data', exist_ok=True)
    call_ready.to_csv(call_ready_file, index=False)
    print(f"Saved call list to: {call_ready_file}")
    
    # Show sample of the data
    print("\n=== SAMPLE DATA WITH DUAL CONTACTS ===")
    sample = df.head(5)
    print(sample[['Company_Name', 'Permit_Contact_Person', 'License_Contact_Person', 'Phone_Number']].to_string(index=False))
    
    return df

def generate_updated_dashboard(df):
    """Generate the HTML dashboard with dual contact columns"""
    
    # Prepare data for the dashboard
    dashboard_data = []
    
    for _, row in df.iterrows():
        dashboard_data.append({
            'company': row['Company_Name'],
            'permitContact': row['Permit_Contact_Person'] if pd.notna(row['Permit_Contact_Person']) else 'Not Available',
            'licenseContact': row['License_Contact_Person'],
            'phone': row['Phone_Number'] if pd.notna(row['Phone_Number']) else '',
            'email': row['Email'] if pd.notna(row['Email']) else '',
            'permits': int(row['Total_Permits']),
            'lastPermit': str(row['Last_Permit_Date'])[:10] if pd.notna(row['Last_Permit_Date']) else '',
            'activityLevel': row['Activity_Level'] if pd.notna(row['Activity_Level']) else '',
            'source': row['Contact_Info_Source'] if pd.notna(row['Contact_Info_Source']) else 'Generated',
            'confidence': row['Contact_Confidence'] if pd.notna(row['Contact_Confidence']) else 'Low'
        })
    
    # Calculate statistics
    total_contractors = len(df)
    with_phone = df['Phone_Number'].notna().sum()
    with_email = df['Email'].notna().sum()
    with_both = (df['Phone_Number'].notna() & df['Email'].notna()).sum()
    
    # Generate the JavaScript data
    js_data = 'const contractorData = ' + str(dashboard_data).replace("'", '"')
    
    # Read the template (we'll use the existing dashboard as a template)
    with open('reports/drill_down_reports/contractor_contact_dashboard_live.html', 'r') as f:
        html_content = f.read()
    
    # Find the data section and update it
    start_marker = 'const contractorData = ['
    end_marker = '];'
    
    start_idx = html_content.find(start_marker)
    end_idx = html_content.find(end_marker, start_idx) + len(end_marker)
    
    # Replace the data
    new_html = html_content[:start_idx] + js_data + ';' + html_content[end_idx:]
    
    # Update the table headers to include both contact columns
    old_headers = '''<tr>
                        <th onclick="sortTable('company')">Company Name ↕</th>
                        <th>Phone</th>
                        <th>Email</th>
                        <th onclick="sortTable('permits')">Permits ↕</th>
                        <th onclick="sortTable('lastPermit')">Last Permit ↕</th>
                        <th>Activity Level</th>
                        <th>Source</th>
                    </tr>'''
    
    new_headers = '''<tr>
                        <th onclick="sortTable('company')">Company Name ↕</th>
                        <th>Permit Contact</th>
                        <th>License Contact</th>
                        <th>Phone</th>
                        <th>Email</th>
                        <th onclick="sortTable('permits')">Permits ↕</th>
                        <th onclick="sortTable('lastPermit')">Last Permit ↕</th>
                        <th>Activity Level</th>
                        <th>Source</th>
                    </tr>'''
    
    new_html = new_html.replace(old_headers, new_headers)
    
    # Update the row rendering function
    old_row_function = '''row.innerHTML = `
                <td>${contractor.company}</td>
                <td>${phoneCell}</td>
                <td>${emailCell}</td>
                <td>${contractor.permits.toLocaleString()}</td>
                <td>${contractor.lastPermit}</td>
                <td><span class="activity-badge activity-${activityClass}">${contractor.activityLevel}</span></td>
                <td><span class="source-badge source-${sourceClass}">${contractor.source}</span></td>
            `;'''
    
    new_row_function = '''row.innerHTML = `
                <td>${contractor.company}</td>
                <td>${contractor.permitContact}</td>
                <td>${contractor.licenseContact}</td>
                <td>${phoneCell}</td>
                <td>${emailCell}</td>
                <td>${contractor.permits.toLocaleString()}</td>
                <td>${contractor.lastPermit}</td>
                <td><span class="activity-badge activity-${activityClass}">${contractor.activityLevel}</span></td>
                <td><span class="source-badge source-${sourceClass}">${contractor.source}</span></td>
            `;'''
    
    new_html = new_html.replace(old_row_function, new_row_function)
    
    # Save the updated dashboard
    output_file = 'reports/drill_down_reports/contractor_contact_dashboard_dual.html'
    with open(output_file, 'w') as f:
        f.write(new_html)
    
    print(f"\nSaved updated dashboard to: {output_file}")
    
    return output_file

if __name__ == "__main__":
    # Update the data
    df = update_contact_data()
    
    # Generate the updated dashboard
    dashboard_file = generate_updated_dashboard(df)
    
    print("\n=== UPDATE COMPLETE ===")
    print(f"1. Updated CSV data: plumber_contacts_dual_contacts.csv")
    print(f"2. Updated dashboard: {dashboard_file}")
    print("\nThe dashboard now shows both:")
    print("- Permit Contact Person (from city permit data)")
    print("- License Contact Person (marked as 'Not Available' since PDF doesn't contain individual names)")