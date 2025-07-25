# Minneapolis Building Permits Analysis Documentation

## Overview

This comprehensive analysis categorized and analyzed 358,301 building permits from Minneapolis's CCS (City Construction Services) database, mapping them to specific use cases defined by the city's permit application types.

## Analysis Summary

### Categorization Results
- **Total Permits**: 358,301
- **Successfully Categorized**: 100% into sub-categories
- **Mapped to Specific Use Cases**: 75.6% (270,716 permits)
- **Unmapped Use Cases**: 24.4% (87,585 permits) - these have sub-categories but couldn't be mapped to specific use cases

### Key Findings by Category

#### 1. **Plumbing (40.0% of all permits)**
- Total Permits: 143,258
- Total Value: $84,501 (mostly $0 due to data reporting)
- Top Use Cases:
  - Gas meter moves: 36,565 permits (CenterPoint Energy dominates)
  - Water heater replacements: 27,459 permits
  - Dishwasher installations: 7,044 permits
- Key Insight: Utility companies (CenterPoint) account for majority of plumbing permits

#### 2. **Building (37.5% of all permits)**
- Total Permits: 134,239
- Total Value: $26.3 billion (78% of all construction value)
- Top Use Cases:
  - Remodels: 43,814 permits ($12.8B value, avg $291K)
  - Roofing/Siding/Windows: 39,767 permits ($684M value)
  - Accessory structures: 21,310 permits ($4.9B value)
- Average Processing Time: 250-557 days depending on complexity

#### 3. **Mechanical (21.2% of all permits)**
- Total Permits: 76,075
- Total Value: $4.4 billion
- Top Use Cases:
  - A/C or Heat pump replacements: 22,058 permits
  - Furnace replacements: 16,804 permits
  - Boiler replacements: 8,123 permits
- Notable Trend: Heat pump installations showing significant growth

#### 4. **Solar (0.8% of all permits)**
- Total Permits: 2,993
- Total Value: $72.3 million
- Average System Value: $24,153
- Market Leader: All Energy Solar (1,338 permits, 44.7% market share)
- Average Processing Time: 189 days (faster than average)

#### 5. **Other Categories**
- **Wrecking/Demolition**: 912 permits ($27.5M value)
- **Sign Installation**: 612 permits ($166.4M value)
- **Soil Erosion**: 212 permits ($448.2M value)

### Top Permit Applicants

1. **CenterPoint Energy Resource Corp**: 32,152 permits (97% plumbing)
2. **Warners Stellian Co Inc**: 12,073 permits (99% plumbing/appliances)
3. **CENTERPOINT ENERGY**: 9,163 permits (72% plumbing)
4. **Standard Heating and Air Conditioning**: 6,313 permits (99% mechanical)
5. **Urban Pine Plumbing and Mechanical**: 5,284 permits (100% plumbing)

### Geographic Patterns
- **Most Active Neighborhoods**:
  1. Loring Park (high-rise residential/commercial)
  2. Downtown West (commercial development)
  3. Linden Hills (residential renovations)
  4. Howe (diverse permit types)
  5. Standish (residential focus)

### Processing Time Analysis
- **Fastest**: Plumbing permits (avg 147-424 days)
- **Moderate**: Mechanical permits (avg 169-433 days)
- **Slowest**: Building permits (avg 250-557 days)
- **New Construction**: Longest at 557 days average

## Files Generated

1. **HTML Reports**:
   - `permit_analysis_by_category.html` - Interactive dashboard with category breakdowns
   - `applicant_analysis.html` - Top 100 permit applicants analysis

2. **CSV Data Files**:
   - `use_case_analysis.csv` - Detailed statistics for each use case
   - `applicant_analysis.csv` - Top 100 applicants with specializations
   - `category_summary.csv` - High-level category statistics
   - `annual_trends_by_category.csv` - Year-over-year trends
   - `seasonal_patterns_by_category.csv` - Monthly patterns

3. **Supporting Files**:
   - `categorize_permits.py` - Script for categorizing permits
   - `detailed_analysis.py` - Script for generating analyses
   - `uncategorized_sample.csv` - Sample of permits needing better categorization

## Methodology

### Categorization Logic
Permits were categorized using a hierarchical approach:
1. **Primary**: Based on `permitType` field (Plumbing, Mechanical, Res, Commercial, etc.)
2. **Secondary**: Keywords in `comments` field to determine specific use cases
3. **Fallback**: `workType` field for additional context

### Mapping Challenges
- 24.4% of permits couldn't be mapped to specific use cases due to:
  - Generic comments (e.g., "repairs", "maintenance")
  - Missing or unclear descriptions
  - Work types not covered in the use case definitions

### Data Quality Notes
- Many plumbing permits show $0 value (likely not tracked for simple replacements)
- Processing times calculated only for completed permits
- Some applicant names have variations (e.g., "CENTERPOINT ENERGY" vs "CenterPoint Energy Resource Corp")

## Recommendations for Improved Analysis

1. **Enhance Categorization**:
   - Add more keyword mappings for common work descriptions
   - Create separate category for "maintenance/repair" vs new installations
   - Implement machine learning for better comment parsing

2. **Data Quality**:
   - Standardize applicant names
   - Require value entry for all permits
   - Add structured fields for common work types

3. **Additional Analysis Opportunities**:
   - Correlate permit activity with property values
   - Analyze permit chains (e.g., demolition followed by new construction)
   - Study seasonal patterns by permit type
   - Track contractor performance metrics

## Usage Instructions

To view the analysis results:
1. Open `permit_analysis_by_category.html` in a web browser for the main dashboard
2. Open `applicant_analysis.html` for contractor/applicant insights
3. Use the CSV files for detailed data exploration in Excel or other tools

To re-run the analysis with updated data:
1. Ensure the conda environment is activated: `conda activate mcai_env`
2. Run: `python categorize_permits.py` to categorize permits
3. Run: `python detailed_analysis.py` to generate reports

## Contact

For questions about this analysis or to request additional insights, please contact the data analysis team.