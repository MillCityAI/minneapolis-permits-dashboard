# CCS Permits Dataset Overview

## Dataset Summary

The CCS Permits dataset contains building permit records from Minneapolis. This comprehensive dataset tracks various types of construction and renovation permits issued by the city.

### Dataset Dimensions
- **Total Records**: 358,301 permits
- **Total Columns**: 26 fields
- **Date Range**: December 2016 to June 2025

## Key Fields

The dataset includes the following 26 columns:
- **Location Data**: X, Y, Display, APN, Longitude, Latitude, Neighborhoods_Desc, Wards
- **Applicant Information**: applicantName, fullName, applicantAddress1, applicantCity
- **Permit Details**: permitNumber, permitType, occupancyType, workType, status, milestone
- **Financial Information**: value, totalFees
- **Housing Units**: dwellingUnitsNew, dwellingUnitsEliminated
- **Dates**: issueDate, completeDate
- **Other**: comments, OBJECTID

## Permit Type Distribution

| Permit Type | Count | Percentage |
|------------|-------|------------|
| Plumbing | 143,220 | 40.0% |
| Residential | 96,696 | 27.0% |
| Mechanical | 76,115 | 21.2% |
| Commercial | 41,146 | 11.5% |
| Wrecking | 912 | 0.3% |
| Site | 212 | 0.1% |

## Permit Status Distribution

| Status | Count | Percentage |
|--------|-------|------------|
| Closed | 317,237 | 88.5% |
| Issued | 25,041 | 7.0% |
| Open | 8,795 | 2.5% |
| Cancelled | 7,216 | 2.0% |
| Other | 12 | <0.1% |

## Financial Analysis

### Permit Values
- **Total Value**: $31,427,300,478.98
- **Average Value**: $87,712.01
- **Median Value**: $0.00
- **Maximum Value**: $143,905,050.00
- **Minimum Value**: $0.00

### Permit Fees
- **Total Fees Collected**: $589,038,646.56
- **Average Fee**: $1,661.53
- **Median Fee**: $133.40
- **Maximum Fee**: $57,521,596.60

## Geographic Distribution

### Top 10 Neighborhoods by Permit Count
1. Loring Park: 21,960 permits
2. Downtown West: 12,450 permits
3. Linden Hills: 9,518 permits
4. Howe: 9,122 permits
5. Hiawatha: 8,824 permits
6. Standish: 8,750 permits
7. Nicollet Island - East Bank: 8,714 permits
8. Fulton: 8,624 permits
9. Lynnhurst: 8,609 permits
10. Minnehaha: 7,390 permits

## Top Applicants

### Most Active Permit Applicants
1. CenterPoint Energy Resource Corp: 32,152 permits
2. Warners Stellian Co Inc: 12,073 permits
3. CENTERPOINT ENERGY: 9,163 permits
4. Standard Heating and Air Conditioning Inc: 6,313 permits
5. Urban Pine Plumbing and Mechanical Inc: 5,284 permits
6. MN Plumbing & Home Services INC: 4,578 permits
7. RENEWAL BY ANDERSEN CORP: 3,737 permits
8. UPTOWN PLUMBING HEATING AND COOLING: 2,712 permits
9. Horwitz LLC: 2,622 permits
10. ZEMAN CONSTRUCTION CO: 2,544 permits

## Occupancy Type Distribution

| Occupancy Type | Count | Description |
|----------------|-------|-------------|
| SFD | 177,163 | Single Family Dwelling |
| MFD | 52,871 | Multi-Family Dwelling |
| Comm | 33,473 | Commercial |
| TFD | 9,275 | Two-Family Dwelling |
| TH | 3,262 | Townhouse |
| 3to4 | 1,074 | 3 to 4 Unit Building |
| Mixed | 634 | Mixed Use |
| Accessory | 350 | Accessory Structure |
| Res | 32 | Residential (General) |

## Work Type Distribution (Top 10)

| Work Type | Count | Description |
|-----------|-------|-------------|
| Res | 104,766 | Residential |
| Misc | 63,930 | Miscellaneous |
| Remodel | 55,700 | Remodeling |
| ExistRes | 53,133 | Existing Residential |
| ComNoFdBv | 23,240 | Commercial No Foundation Below Grade |
| Comm-MFD | 11,761 | Commercial Multi-Family Dwelling |
| ComMin | 9,251 | Commercial Minor |
| RoofWind | 6,979 | Roof and Windows |
| Addition | 6,021 | Addition |
| ComMFDRR | 5,475 | Commercial MFD Repair/Replace |

## Data Quality

### Missing Values Summary
- **Location Data**: Display (13), APN (58), Neighborhoods_Desc (2,324), Wards (2,328)
- **Housing Units**: dwellingUnitsNew and dwellingUnitsEliminated (221,010 each)
- **Financial**: totalFees (3,786)
- **Comments**: 5,174 missing
- **Dates**: completeDate (39,656)
- **Applicant Info**: fullName (24,626), applicantAddress1 (125), applicantCity (60)

## Key Insights

1. **Plumbing permits dominate**: Making up 40% of all permits, likely due to regular maintenance and upgrades required for water and gas systems.

2. **Utility companies are major applicants**: CenterPoint Energy accounts for over 41,000 permits combined, reflecting ongoing infrastructure maintenance.

3. **Most permits are completed**: 88.5% of permits have a "Closed" status, indicating good project completion rates.

4. **Significant economic impact**: With over $31 billion in total permit values and nearly $600 million in fees collected, the construction sector represents substantial economic activity.

5. **Urban concentration**: Downtown areas (Loring Park, Downtown West) show the highest permit activity, reflecting ongoing urban development.

6. **Residential focus**: Single-family dwellings (SFD) represent nearly half of all permits when considering occupancy types.

## Data Sources and Notes

- **Source**: CCS (City Coordinating System) Permits Database
- **Coverage**: Minneapolis, Minnesota
- **Update Frequency**: Dataset appears to be regularly updated with recent permits from 2025
- **Coordinate System**: X/Y coordinates and Longitude/Latitude are provided for geographic analysis