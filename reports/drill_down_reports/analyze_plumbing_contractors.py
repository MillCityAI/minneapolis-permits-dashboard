#!/usr/bin/env python3
"""
Filter and analyze plumbing contractor data, appending 'warp' to the CSV output file.
"""

import pandas as pd

def main():
    # Load existing plumbing contractors data
    df = pd.read_csv('data/plumbing_all_applicants.csv')
    
    # Filter only contractors
    contractor_df = df[df['applicant_type'] == 'Contractor']

    # Sort contractors by total_permits in descending order
    sorted_df = contractor_df.sort_values(by='total_permits', ascending=False)

    # Select relevant columns
    selected_columns = [
        'applicant_name', 'total_permits', 'completion_rate', 'abandonment_rate',
        'primary_use_case'
    ]
    output_df = sorted_df[selected_columns]

    # Export the results to CSV
    output_filename = 'plumbing_leads_warp.csv'
    output_df.to_csv(output_filename, index=False)

    print(f'Filtered contractor data saved to {output_filename}')

if __name__ == '__main__':
    main()
