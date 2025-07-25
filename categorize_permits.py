#!/usr/bin/env python3
"""
Categorize Minneapolis building permits based on use case definitions.
Maps permits to sub-categories and use cases for targeted analysis.
"""

import pandas as pd
import numpy as np
import re
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Define the use case mappings based on the provided categories
USE_CASE_MAPPINGS = {
    'Building': {
        'use_cases': [
            'Accessory (detached garage, pools, sheds)',
            'Addition (Room, story, decks, dormers)',
            'Dwelling Unit Finish',
            'Flat roof only',
            'New Construction',
            'Remodel',
            'Reroofs (shingle/pitched roof only), Siding, Window Replacements'
        ],
        'keywords': {
            'Accessory (detached garage, pools, sheds)': ['garage', 'shed', 'pool', 'accessory', 'detached'],
            'Addition (Room, story, decks, dormers)': ['addition', 'deck', 'dormer', 'story', 'expand'],
            'Dwelling Unit Finish': ['dwelling', 'unit finish', 'finish basement', 'finish attic'],
            'Flat roof only': ['flat roof', 'tpo', 'epdm', 'rubber roof', 'membrane'],
            'New Construction': ['new construction', 'new building', 'new home', 'new sfh', 'new sfd'],
            'Remodel': ['remodel', 'renovation', 'kitchen', 'bathroom', 'interior'],
            'Reroofs (shingle/pitched roof only), Siding, Window Replacements': ['reroof', 'shingle', 'siding', 'window', 'replace window']
        }
    },
    'Mechanical': {
        'use_cases': [
            'A/C or Heat pump add on or replacement',
            'Add or replace space heating unit',
            'Air cleaner',
            'Bath fans',
            'Change out boiler (incidental piping included)',
            'Change out furnace (plenum work included)',
            'Dryer vent',
            'Extend heat/cool/vent system in an existing non-conditioned space',
            'Fin Tube Radiation &/or In-floor heat',
            'Fresh air intake',
            'Gas piping (include linear feet)',
            'HRV/ERV',
            'Humidifier',
            'Kitchen vent (CFM)',
            'Remove existing heat/cool/vent system and install a new system',
            'Solid fuel Heat device',
            'Supply or return openings'
        ],
        'keywords': {
            'A/C or Heat pump add on or replacement': ['air condition', 'a/c', 'ac ', 'heat pump', 'cooling', 'mini split'],
            'Change out furnace (plenum work included)': ['furnace', 'heating unit', 'forced air'],
            'Change out boiler (incidental piping included)': ['boiler', 'hot water heat', 'hydronic'],
            'Kitchen vent (CFM)': ['kitchen vent', 'range hood', 'exhaust hood', 'cfm'],
            'Bath fans': ['bath fan', 'bathroom fan', 'exhaust fan'],
            'Gas piping (include linear feet)': ['gas line', 'gas piping', 'gas meter'],
            'HRV/ERV': ['hrv', 'erv', 'heat recovery', 'energy recovery'],
            'Dryer vent': ['dryer vent', 'dryer exhaust']
        }
    },
    'Plumbing': {
        'use_cases': [
            'Backflow device (non-testable)',
            'Bathtub install',
            'Bathtub/shower combo install',
            'Coffee maker',
            'Commercial disposal',
            'Dishwasher install',
            'Drinking fountain',
            'Electric Water Heater',
            'Water heater',
            'Floor Drain',
            'Gas generator',
            'Gas meter',
            'Grease interceptor',
            'Hose Bibb',
            'Ice maker install',
            'Laundry dryer',
            'Laundry tub',
            'Laundry washer - standpipe',
            'Lavatory - bathroom sink install',
            'Mop sink',
            'Outdoor grill, fire pit',
            'Range/Cooktop',
            'Roof Drain',
            'Shower install',
            'Sink',
            'Sink - kitchen',
            'Toilet install',
            'Tub or shower valve',
            'Urinal'
        ],
        'keywords': {
            'Water heater': ['water heater', 'hot water', 'tank replacement'],
            'Toilet install': ['toilet', 'water closet', 'wc'],
            'Shower install': ['shower', 'shower valve', 'shower install'],
            'Bathtub install': ['bathtub', 'tub install', 'bath install'],
            'Sink - kitchen': ['kitchen sink', 'disposal', 'garbage disposal'],
            'Dishwasher install': ['dishwasher'],
            'Lavatory - bathroom sink install': ['lavatory', 'bathroom sink', 'lav sink'],
            'Gas meter': ['gas meter', 'meter move'],
            'Backflow device (non-testable)': ['backflow', 'rpz', 'backflow preventer']
        }
    },
    'Solar': {
        'use_cases': ['Solar panels'],
        'keywords': {
            'Solar panels': ['solar', 'photovoltaic', 'pv system', 'solar panel', 'solar array']
        }
    },
    'Wrecking': {
        'use_cases': ['Demolition'],
        'keywords': {
            'Demolition': ['demolition', 'demo', 'wreck', 'tear down', 'remove building']
        }
    },
    'Moving': {
        'use_cases': [
            'Commercial',
            'Move Accessory of Utility Structure',
            'Multi Family Dwelling',
            'Single Family Dwelling',
            'Townhome',
            'Two Family Dwelling'
        ],
        'keywords': {
            'Move Accessory of Utility Structure': ['move', 'relocate', 'building move']
        }
    },
    'Sign': {
        'use_cases': ['Sign installation'],
        'keywords': {
            'Sign installation': ['sign', 'signage', 'billboard']
        }
    },
    'Fence': {
        'use_cases': ['Fence over 7 feet'],
        'keywords': {
            'Fence over 7 feet': ['fence', 'fencing', 'privacy fence']
        }
    },
    'Soil erosion': {
        'use_cases': [
            'Grading, landscaping, paving, sidewalk, driveway, curb cut',
            'New building construction or addition',
            'Trenching',
            'Wrecking a building'
        ],
        'keywords': {
            'Grading, landscaping, paving, sidewalk, driveway, curb cut': ['grading', 'landscaping', 'paving', 'sidewalk', 'driveway', 'curb cut', 'erosion control']
        }
    }
}

def categorize_permit(row):
    """
    Categorize a single permit based on permitType, workType, and comments.
    Returns (sub_category, use_case) tuple.
    """
    permit_type = str(row['permitType']).lower()
    work_type = str(row['workType']).lower()
    comments = str(row['comments']).lower()
    
    # First, try to match based on permitType
    if permit_type == 'plumbing':
        sub_category = 'Plumbing'
    elif permit_type == 'mechanical':
        sub_category = 'Mechanical'
    elif permit_type in ['res', 'residential']:
        sub_category = 'Building'
    elif permit_type == 'commercial':
        if 'sign' in comments:
            sub_category = 'Sign'
        else:
            sub_category = 'Building'
    elif permit_type == 'wrecking':
        sub_category = 'Wrecking'
    elif permit_type == 'site':
        sub_category = 'Soil erosion'
    else:
        sub_category = None
    
    # Now find the specific use case
    use_case = None
    
    if sub_category:
        if sub_category in USE_CASE_MAPPINGS:
            # Check keywords in comments for best match
            for uc, keywords in USE_CASE_MAPPINGS[sub_category]['keywords'].items():
                for keyword in keywords:
                    if keyword in comments or keyword in work_type:
                        use_case = uc
                        break
                if use_case:
                    break
            
            # If no keyword match, use workType to guess
            if not use_case:
                if sub_category == 'Building':
                    if work_type == 'remodel':
                        use_case = 'Remodel'
                    elif work_type == 'addition':
                        use_case = 'Addition (Room, story, decks, dormers)'
                    elif work_type == 'misc':
                        if 'window' in comments:
                            use_case = 'Reroofs (shingle/pitched roof only), Siding, Window Replacements'
                        elif 'roof' in comments:
                            if 'flat' in comments:
                                use_case = 'Flat roof only'
                            else:
                                use_case = 'Reroofs (shingle/pitched roof only), Siding, Window Replacements'
                    elif work_type == 'accessory':
                        use_case = 'Accessory (detached garage, pools, sheds)'
                    elif 'new' in work_type:
                        use_case = 'New Construction'
                elif sub_category == 'Mechanical':
                    if 'furnace' in comments:
                        use_case = 'Change out furnace (plenum work included)'
                    elif 'a/c' in comments or 'air condition' in comments:
                        use_case = 'A/C or Heat pump add on or replacement'
                    elif 'water heater' in comments:
                        # This might be plumbing, recategorize
                        sub_category = 'Plumbing'
                        use_case = 'Water heater'
                elif sub_category == 'Plumbing':
                    if 'water heater' in comments:
                        use_case = 'Water heater'
                    elif 'toilet' in comments:
                        use_case = 'Toilet install'
                    elif 'shower' in comments:
                        use_case = 'Shower install'
                elif sub_category == 'Wrecking':
                    use_case = 'Demolition'
    
    # Check for solar specifically
    if 'solar' in comments:
        sub_category = 'Solar'
        use_case = 'Solar panels'
    
    return sub_category, use_case

def main():
    print("Loading Minneapolis permits data...")
    
    # Load the data
    df = pd.read_csv('source/CCS_Permits.csv', low_memory=False)
    print(f"Loaded {len(df)} permits")
    
    # Apply categorization
    print("\nCategorizing permits...")
    df[['sub_category', 'use_case']] = df.apply(
        lambda row: pd.Series(categorize_permit(row)), axis=1
    )
    
    # Calculate statistics
    total_permits = len(df)
    categorized = df[df['sub_category'].notna()]
    uncategorized = df[df['sub_category'].isna()]
    
    print(f"\nCategorization Results:")
    print(f"Total permits: {total_permits:,}")
    print(f"Categorized: {len(categorized):,} ({len(categorized)/total_permits*100:.1f}%)")
    print(f"Uncategorized: {len(uncategorized):,} ({len(uncategorized)/total_permits*100:.1f}%)")
    
    # Save categorized data
    print("\nSaving categorized data...")
    df.to_csv('categorized_permits.csv', index=False)
    
    # Save uncategorized for review
    if len(uncategorized) > 0:
        uncategorized.to_csv('uncategorized_permits.csv', index=False)
        print(f"Saved {len(uncategorized)} uncategorized permits for review")
    
    # Generate summary statistics
    print("\nGenerating category summary...")
    category_summary = []
    
    for sub_cat in df['sub_category'].dropna().unique():
        cat_data = df[df['sub_category'] == sub_cat]
        
        summary = {
            'sub_category': sub_cat,
            'total_permits': len(cat_data),
            'percentage': len(cat_data) / total_permits * 100,
            'total_value': cat_data['value'].sum(),
            'avg_value': cat_data['value'].mean(),
            'total_fees': cat_data['totalFees'].sum(),
            'avg_fees': cat_data['totalFees'].mean()
        }
        category_summary.append(summary)
    
    # Save summary
    summary_df = pd.DataFrame(category_summary)
    summary_df = summary_df.sort_values('total_permits', ascending=False)
    summary_df.to_csv('category_summary.csv', index=False)
    
    # Print summary
    print("\nCategory Summary:")
    print("-" * 80)
    print(f"{'Sub-Category':<20} {'Permits':>10} {'%':>6} {'Total Value':>15} {'Avg Value':>12}")
    print("-" * 80)
    
    for _, row in summary_df.iterrows():
        print(f"{row['sub_category']:<20} {row['total_permits']:>10,} {row['percentage']:>5.1f}% "
              f"${row['total_value']:>14,.0f} ${row['avg_value']:>11,.0f}")
    
    print("\nCategorization complete!")
    print("Files created:")
    print("  - categorized_permits.csv (full dataset with categories)")
    print("  - category_summary.csv (summary statistics)")
    print("  - uncategorized_permits.csv (permits needing review)")

if __name__ == "__main__":
    main()