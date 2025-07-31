#!/usr/bin/env python3
"""
Remove the License Contact Person column from the dashboard since it's always "Not Available"
"""

import pandas as pd
import json

def generate_dashboard_without_license_contact():
    """Generate the HTML dashboard without the license contact column"""
    
    # Load the original data (before dual contacts)
    df = pd.read_csv('plumber_contacts_with_verified_info.csv')
    
    # Prepare JavaScript data
    contractors_data = []
    for _, row in df.iterrows():
        contractors_data.append({
            'company': row['Company_Name'],
            'contact': row['Contact_Person'] if pd.notna(row['Contact_Person']) else '',
            'phone': row['Phone_Number'] if pd.notna(row['Phone_Number']) else '',
            'email': row['Email'] if pd.notna(row['Email']) else '',
            'permits': int(row['Total_Permits']),
            'lastPermit': str(row['Last_Permit_Date'])[:10] if pd.notna(row['Last_Permit_Date']) else '',
            'activityLevel': row['Activity_Level'] if pd.notna(row['Activity_Level']) else '',
            'daysSince': int(row['Days_Since_Last_Permit']) if pd.notna(row['Days_Since_Last_Permit']) else 999,
            'source': row['Contact_Info_Source'] if pd.notna(row['Contact_Info_Source']) else 'Generated',
            'confidence': row['Contact_Confidence'] if pd.notna(row['Contact_Confidence']) else 'Low'
        })
    
    # Calculate statistics
    total_contractors = len(df)
    with_phone = df['Phone_Number'].notna().sum()
    with_email = df['Email'].notna().sum()
    with_both = (df['Phone_Number'].notna() & df['Email'].notna()).sum()
    
    # Generate HTML
    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Plumbing Contractor Contact Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: white;
            padding: 40px;
            box-shadow: 0 0 20px rgba(0,0,0,0.1);
            border-radius: 8px;
        }}
        h1 {{
            color: #1565c0;
            border-bottom: 3px solid #1565c0;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #424242;
            margin-top: 40px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }}
        .stat-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #1565c0;
            text-align: center;
        }}
        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: #1565c0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
            margin-top: 5px;
        }}
        .success-card {{
            border-left-color: #4caf50;
        }}
        .success-card .stat-value {{
            color: #4caf50;
        }}
        .warning-card {{
            border-left-color: #ff9800;
        }}
        .warning-card .stat-value {{
            color: #ff9800;
        }}
        .filter-controls {{
            background-color: #f5f5f5;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
        }}
        .filter-controls input, .filter-controls select {{
            padding: 8px;
            margin: 5px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }}
        .download-btn {{
            background-color: #4caf50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin: 10px 5px;
        }}
        .download-btn:hover {{
            background-color: #45a049;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #555;
            cursor: pointer;
            user-select: none;
        }}
        th:hover {{
            background-color: #e9ecef;
        }}
        tr:hover {{
            background-color: #f8f9fa;
        }}
        .verified-contact {{
            background-color: #e8f5e9;
        }}
        .has-contact {{
            background-color: #fff3e0;
        }}
        .no-contact {{
            color: #999;
            font-style: italic;
        }}
        .contact-info {{
            color: #1565c0;
            text-decoration: none;
        }}
        .contact-info:hover {{
            text-decoration: underline;
        }}
        .activity-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .activity-very-active {{
            background-color: #4caf50;
            color: white;
        }}
        .activity-active {{
            background-color: #8bc34a;
            color: white;
        }}
        .activity-moderate {{
            background-color: #ff9800;
            color: white;
        }}
        .activity-low {{
            background-color: #ff5722;
            color: white;
        }}
        .activity-inactive {{
            background-color: #9e9e9e;
            color: white;
        }}
        .source-badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }}
        .source-licensed {{
            background-color: #2196f3;
            color: white;
        }}
        .source-generated {{
            background-color: #9e9e9e;
            color: white;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div style="margin-bottom: 20px;">
            <a href="../../index.html" style="color: #1565c0; text-decoration: none; font-weight: bold;">← Dashboard Home</a>
            <span style="margin: 0 10px;">|</span>
            <a href="summary_dashboard.html" style="color: #1565c0; text-decoration: none; font-weight: bold;">Category Summary</a>
            <span style="margin: 0 10px;">|</span>
            <a href="plumbing_detailed_report.html" style="color: #1565c0; text-decoration: none; font-weight: bold;">Plumbing Report</a>
        </div>
        
        <h1>Plumbing Contractor Contact Dashboard</h1>
        <p style="color: #666;">Verified contact information from Minnesota plumbing license database matched with permit data</p>
        
        <div class="stat-grid">
            <div class="stat-card">
                <div class="stat-value" id="totalContractors">{total_contractors}</div>
                <div class="stat-label">Total Contractors</div>
            </div>
            <div class="stat-card success-card">
                <div class="stat-value" id="withPhone">{with_phone}</div>
                <div class="stat-label">With Phone Numbers</div>
            </div>
            <div class="stat-card success-card">
                <div class="stat-value" id="withEmail">{with_email}</div>
                <div class="stat-label">With Email Addresses</div>
            </div>
            <div class="stat-card warning-card">
                <div class="stat-value" id="withBoth">{with_both}</div>
                <div class="stat-label">With Both</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">42.4%</div>
                <div class="stat-label">Match Success Rate</div>
            </div>
        </div>

        <div class="filter-controls">
            <input type="text" id="searchBox" placeholder="Search contractors, emails, phones..." style="width: 300px;">
            <select id="contactFilter">
                <option value="all">All Contractors</option>
                <option value="with-phone">With Phone Numbers</option>
                <option value="with-email">With Email Addresses</option>
                <option value="with-both">With Both</option>
                <option value="verified">Verified Contacts Only</option>
                <option value="no-contact">No Contact Info</option>
            </select>
            <select id="activityFilter">
                <option value="all">All Activity Levels</option>
                <option value="very-active">Very Active (< 30 days)</option>
                <option value="active">Active (30-90 days)</option>
                <option value="moderate">Moderate (90-180 days)</option>
                <option value="low">Low (180-365 days)</option>
                <option value="inactive">Inactive (> 1 year)</option>
            </select>
            <button class="download-btn" onclick="downloadCSV()">Download CSV</button>
            <button class="download-btn" onclick="downloadCallList()">Download Call List</button>
        </div>

        <h2>Contractor Directory</h2>
        <table id="contractorTable">
            <thead>
                <tr>
                    <th onclick="sortTable('company')">Company Name ↕</th>
                    <th onclick="sortTable('contact')">Contact Person ↕</th>
                    <th>Phone</th>
                    <th>Email</th>
                    <th onclick="sortTable('permits')">Permits ↕</th>
                    <th onclick="sortTable('lastPermit')">Last Permit ↕</th>
                    <th>Activity Level</th>
                    <th>Source</th>
                </tr>
            </thead>
            <tbody id="tableBody">
            </tbody>
        </table>
    </div>

    <script>
        // Contractor data
        const contractorData = {json.dumps(contractors_data, indent=2)};

        // Initialize
        let currentData = [...contractorData];
        populateTable(currentData);
        updateStats();

        function populateTable(data) {{
            const tbody = document.getElementById('tableBody');
            tbody.innerHTML = '';
            
            data.forEach(contractor => {{
                const row = tbody.insertRow();
                
                // Determine activity class
                let activityClass = 'inactive';
                if (contractor.activityLevel.includes('Very Active')) activityClass = 'very-active';
                else if (contractor.activityLevel.includes('Active (30-90')) activityClass = 'active';
                else if (contractor.activityLevel.includes('Moderate')) activityClass = 'moderate';
                else if (contractor.activityLevel.includes('Low')) activityClass = 'low';
                
                // Determine source class
                const sourceClass = contractor.source === 'Licensed Data' ? 'licensed' : 'generated';
                
                // Build phone cell
                let phoneCell = '<span class="no-contact">No phone</span>';
                if (contractor.phone) {{
                    phoneCell = `<a href="tel:${{contractor.phone}}" class="contact-info">${{contractor.phone}}</a>`;
                }}
                
                // Build email cell
                let emailCell = '<span class="no-contact">No email</span>';
                if (contractor.email) {{
                    emailCell = `<a href="mailto:${{contractor.email}}" class="contact-info">${{contractor.email}}</a>`;
                }}
                
                row.innerHTML = `
                    <td>${{contractor.company}}</td>
                    <td>${{contractor.contact || 'N/A'}}</td>
                    <td>${{phoneCell}}</td>
                    <td>${{emailCell}}</td>
                    <td>${{contractor.permits.toLocaleString()}}</td>
                    <td>${{contractor.lastPermit}}</td>
                    <td><span class="activity-badge activity-${{activityClass}}">${{contractor.activityLevel}}</span></td>
                    <td><span class="source-badge source-${{sourceClass}}">${{contractor.source}}</span></td>
                `;
            }});
        }}

        function updateStats() {{
            const filtered = currentData;
            document.getElementById('totalContractors').textContent = filtered.length;
            document.getElementById('withPhone').textContent = filtered.filter(c => c.phone).length;
            document.getElementById('withEmail').textContent = filtered.filter(c => c.email).length;
            document.getElementById('withBoth').textContent = filtered.filter(c => c.phone && c.email).length;
        }}

        // Sorting
        let sortOrder = {{}};
        function sortTable(column) {{
            sortOrder[column] = !sortOrder[column];
            const ascending = sortOrder[column];
            
            currentData.sort((a, b) => {{
                let aVal = a[column];
                let bVal = b[column];
                
                if (column === 'permits' || column === 'daysSince') {{
                    aVal = parseInt(aVal) || 0;
                    bVal = parseInt(bVal) || 0;
                }}
                
                if (column === 'lastPermit') {{
                    aVal = new Date(aVal || '1900-01-01');
                    bVal = new Date(bVal || '1900-01-01');
                }}
                
                if (aVal < bVal) return ascending ? -1 : 1;
                if (aVal > bVal) return ascending ? 1 : -1;
                return 0;
            }});
            
            populateTable(currentData);
        }}

        // Filtering
        document.getElementById('contactFilter').addEventListener('change', applyFilters);
        document.getElementById('activityFilter').addEventListener('change', applyFilters);
        document.getElementById('searchBox').addEventListener('input', applyFilters);

        function applyFilters() {{
            const contactFilter = document.getElementById('contactFilter').value;
            const activityFilter = document.getElementById('activityFilter').value;
            const searchTerm = document.getElementById('searchBox').value.toLowerCase();
            
            let filtered = [...contractorData];
            
            // Contact filter
            if (contactFilter === 'with-phone') {{
                filtered = filtered.filter(c => c.phone);
            }} else if (contactFilter === 'with-email') {{
                filtered = filtered.filter(c => c.email);
            }} else if (contactFilter === 'with-both') {{
                filtered = filtered.filter(c => c.phone && c.email);
            }} else if (contactFilter === 'verified') {{
                filtered = filtered.filter(c => c.source === 'Licensed Data');
            }} else if (contactFilter === 'no-contact') {{
                filtered = filtered.filter(c => !c.phone && !c.email);
            }}
            
            // Activity filter
            if (activityFilter !== 'all') {{
                const activityMap = {{
                    'very-active': 'Very Active',
                    'active': 'Active (30-90',
                    'moderate': 'Moderate',
                    'low': 'Low',
                    'inactive': 'Inactive'
                }};
                filtered = filtered.filter(c => c.activityLevel.includes(activityMap[activityFilter]));
            }}
            
            // Search filter
            if (searchTerm) {{
                filtered = filtered.filter(c => 
                    c.company.toLowerCase().includes(searchTerm) ||
                    (c.contact && c.contact.toLowerCase().includes(searchTerm)) ||
                    (c.phone && c.phone.includes(searchTerm)) ||
                    (c.email && c.email.toLowerCase().includes(searchTerm))
                );
            }}
            
            currentData = filtered;
            populateTable(currentData);
            updateStats();
        }}

        // Download functions
        function downloadCSV() {{
            const headers = ['Company Name', 'Contact Person', 'Phone', 'Email', 'Total Permits', 'Last Permit', 'Activity Level', 'Days Since Last', 'Source', 'Confidence'];
            const rows = currentData.map(c => [
                c.company,
                c.contact || '',
                c.phone || '',
                c.email || '',
                c.permits,
                c.lastPermit,
                c.activityLevel,
                c.daysSince,
                c.source,
                c.confidence
            ]);
            
            const csv = [headers, ...rows].map(row => row.map(cell => `"${{String(cell).replace(/"/g, '""')}}"`).join(',')).join('\\n');
            
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'plumber_contacts_' + new Date().toISOString().split('T')[0] + '.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }}

        function downloadCallList() {{
            const callListData = currentData.filter(c => c.phone);
            const headers = ['Company Name', 'Contact Person', 'Phone', 'Email', 'Total Permits', 'Last Activity', 'Confidence'];
            const rows = callListData.map(c => [
                c.company,
                c.contact || '',
                c.phone,
                c.email || '',
                c.permits,
                c.activityLevel,
                c.confidence
            ]);
            
            const csv = [headers, ...rows].map(row => row.map(cell => `"${{String(cell).replace(/"/g, '""')}}"`).join(',')).join('\\n');
            
            const blob = new Blob([csv], {{ type: 'text/csv' }});
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'plumber_call_list_' + new Date().toISOString().split('T')[0] + '.csv';
            a.click();
            window.URL.revokeObjectURL(url);
        }}
    </script>
</body>
</html>'''
    
    # Save the dashboard
    output_file = 'reports/drill_down_reports/contractor_contact_dashboard_live.html'
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print(f"Updated dashboard: {output_file}")
    print(f"Removed the License Contact Person column")
    print(f"Total contractors: {total_contractors}")
    print(f"With phone: {with_phone}")
    print(f"With email: {with_email}")
    print(f"With both: {with_both}")
    
    return output_file

if __name__ == "__main__":
    generate_dashboard_without_license_contact()