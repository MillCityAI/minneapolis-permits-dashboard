import pandas as pd
import re

# Load data
df = pd.read_csv('source/CCS_Permits.csv')
df['issueDate'] = pd.to_datetime(df['issueDate'], errors='coerce')
df['issue_year'] = df['issueDate'].dt.year

# Find roofing permits
roof_keywords = ['roof', 'Roof', 'ROOF', 'shingle', 'reroof', 'tear off']
roof_mask = df['comments'].str.contains('|'.join(roof_keywords), case=False, na=False) | (df['workType'] == 'RoofWind')
roof_permits = df[roof_mask].copy()

print(f'Total roofing-related permits: {len(roof_permits):,}')
print(f'Percentage of all permits: {len(roof_permits)/len(df)*100:.2f}%')
print(f'\nRoofing permits by year:')
yearly = roof_permits['issue_year'].value_counts().sort_index()
for year, count in yearly.items():
    if pd.notna(year) and year >= 2017:
        print(f'  {int(year)}: {count:,}')

print(f'\nProject value statistics:')
value_data = roof_permits[roof_permits['value'] > 0]
print(f'  Average project value: ${value_data["value"].mean():,.2f}')
print(f'  Median project value: ${value_data["value"].median():,.2f}')
print(f'  Total roofing project value: ${roof_permits["value"].sum():,.2f}')

print(f'\nTop 10 roofing contractors:')
top_contractors = roof_permits['applicantName'].value_counts().head(10)
for i, (name, count) in enumerate(top_contractors.items(), 1):
    print(f'  {i}. {name}: {count} permits')

# Analyze permit types
print(f'\nPermit types for roofing work:')
print(roof_permits['permitType'].value_counts())

# Work types
print(f'\nWork types for roofing:')
print(roof_permits['workType'].value_counts().head(10))