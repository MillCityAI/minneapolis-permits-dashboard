#!/usr/bin/env python3
"""
Generate an interactive contractor contact dashboard with verified contact information
"""

import pandas as pd
import json

def generate_dashboard():
    """Generate the contractor contact dashboard with real data"""
    
    print("Loading contractor data...")
    
    # Load the merged contractor data
    df = pd.read_csv('reports/drill_down_reports/data/plumbing_contractors_with_contacts.csv')
    
    # Filter to contractors only
    contractors_df = df[df['applicant_type'] == 'Contractor'].copy()
    
    # Sort by total permits descending
    contractors_df = contractors_df.sort_values('total_permits', ascending=False)
    
    # Clean up empty strings and NaN values
    contractors_df['Phone_Number'] = contractors_df['Phone_Number'].fillna('')
    contractors_df['Email'] = contractors_df['Email'].fillna('')
    contractors_df['Contact_Person'] = contractors_df['Contact_Person'].fillna('')
    contractors_df['Contact_Info_Source'] = contractors_df['Contact_Info_Source'].fillna('None')
    contractors_df['Contact_Confidence'] = contractors_df['Contact_Confidence'].fillna('None')
    contractors_df['Activity_Level'] = contractors_df['Activity_Level'].fillna('Unknown')
    
    # Prepare data for JavaScript
    contractor_list = []
    for _, row in contractors_df.iterrows():
        phone = str(row['Phone_Number']) if row['Phone_Number'] and row['Phone_Number'] != 'nan' else ''
        email = str(row['Email']) if row['Email'] and row['Email'] != 'nan' else ''
        contact = str(row['Contact_Person']) if row['Contact_Person'] and row['Contact_Person'] != 'nan' else ''
        
        contractor_list.append({
            'company': str(row['applicant_name']),
            'contact': contact,
            'phone': phone,
            'email': email,
            'permits': int(row['total_permits']),
            'activity': str(row['Activity_Level']),
            'daysSince': int(row['Days_Since_Last_Permit']) if pd.notna(row['Days_Since_Last_Permit']) else 0,
            'source': str(row['Contact_Info_Source']),
            'confidence': str(row['Contact_Confidence'])
        })
    
    # Calculate statistics (count non-empty strings)
    total_contractors = len(contractors_df)
    with_phone = ((contractors_df['Phone_Number'] != '') & (contractors_df['Phone_Number'].notna())).sum()
    with_email = ((contractors_df['Email'] != '') & (contractors_df['Email'].notna())).sum()
    with_both = ((contractors_df['Phone_Number'] != '') & (contractors_df['Phone_Number'].notna()) & 
                 (contractors_df['Email'] != '') & (contractors_df['Email'].notna())).sum()
    
    # Read the template
    with open('reports/drill_down_reports/contractor_contact_dashboard.html', 'r') as f:
        html_content = f.read()
    
    # Update statistics in the HTML
    html_content = html_content.replace('>831</div>', f'>{total_contractors}</div>')
    html_content = html_content.replace('>251</div>', f'>{with_phone}</div>')
    html_content = html_content.replace('>377</div>', f'>{with_email}</div>')
    html_content = html_content.replace('>247</div>', f'>{with_both}</div>')
    
    # Replace the sample data with real data
    js_data = json.dumps(contractor_list, indent=2)
    html_content = html_content.replace(
        'const contractors = [',
        f'const contractors = {js_data};\n\n// Original sample data replaced with real data\nconst contractors_original = ['
    )
    
    # Save the updated dashboard
    output_file = 'reports/drill_down_reports/contractor_contact_dashboard_live.html'
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"\nGenerated live dashboard: {output_file}")
    print(f"\nStatistics:")
    print(f"- Total contractors: {total_contractors}")
    print(f"- With phone numbers: {with_phone} ({with_phone/total_contractors*100:.1f}%)")
    print(f"- With email addresses: {with_email} ({with_email/total_contractors*100:.1f}%)")
    print(f"- With both: {with_both} ({with_both/total_contractors*100:.1f}%)")
    
    # Also update the main plumbing report
    update_plumbing_report(contractors_df)

def update_plumbing_report(contractors_df):
    """Add contact information section to the plumbing detailed report"""
    
    # Calculate stats properly
    with_phone = ((contractors_df['Phone_Number'] != '') & (contractors_df['Phone_Number'].notna())).sum()
    with_email = ((contractors_df['Email'] != '') & (contractors_df['Email'].notna())).sum()
    with_both = ((contractors_df['Phone_Number'] != '') & (contractors_df['Phone_Number'].notna()) & 
                 (contractors_df['Email'] != '') & (contractors_df['Email'].notna())).sum()
    
    # Create a summary section for the plumbing report
    contact_summary = f"""
        <div class="section">
            <h2>Contractor Contact Information</h2>
            <p>Contact information has been enriched with data from the Minnesota plumbing license database.</p>
            
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-value">{len(contractors_df)}</div>
                    <div class="stat-label">Total Contractors</div>
                </div>
                <div class="stat-card" style="border-left-color: #4caf50;">
                    <div class="stat-value" style="color: #4caf50;">{with_phone}</div>
                    <div class="stat-label">With Phone Numbers</div>
                </div>
                <div class="stat-card" style="border-left-color: #4caf50;">
                    <div class="stat-value" style="color: #4caf50;">{with_email}</div>
                    <div class="stat-label">With Email Addresses</div>
                </div>
                <div class="stat-card" style="border-left-color: #ff9800;">
                    <div class="stat-value" style="color: #ff9800;">{with_both}</div>
                    <div class="stat-label">With Both</div>
                </div>
            </div>
            
            <p><a href="contractor_contact_dashboard_live.html" class="download-link">
                📊 View Interactive Contact Dashboard
            </a></p>
            
            <h3>Top Contractors with Verified Contact Information</h3>
            <table>
                <thead>
                    <tr>
                        <th>Company Name</th>
                        <th>Phone</th>
                        <th>Email</th>
                        <th>Total Permits</th>
                        <th>Contact Source</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # Add top 20 contractors with verified contacts
    verified = contractors_df[contractors_df['Contact_Info_Source'] == 'Licensed Data'].head(20)
    
    for _, row in verified.iterrows():
        contact_summary += f"""
                    <tr class="contractor">
                        <td>{row['applicant_name']}</td>
                        <td>{row['Phone_Number']}</td>
                        <td>{row['Email']}</td>
                        <td>{row['total_permits']:,}</td>
                        <td>{row['Contact_Info_Source']}</td>
                    </tr>
        """
    
    contact_summary += """
                </tbody>
            </table>
        </div>
    """
    
    # Save the contact summary section
    with open('reports/drill_down_reports/plumbing_contact_section.html', 'w') as f:
        f.write(contact_summary)
    
    print("\nCreated contact summary section for plumbing report")

if __name__ == "__main__":
    generate_dashboard()