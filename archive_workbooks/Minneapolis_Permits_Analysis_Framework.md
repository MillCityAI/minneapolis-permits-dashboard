# Minneapolis Permits Analysis Framework

## Overview
A data-driven analysis framework that automatically generates web reports from Minneapolis permit data (2015-2025) using the hierarchical structure defined in the use cases CSV.

**Core Principle: All data and insights must be directly derived from the provided datasets. No assumptions or estimations.**

---

## Data Architecture

### 1. Hierarchical Structure (from Use Cases CSV)
```
Category
├── Sub-Category
    └── Use Case (specific permit types)
```

Example:
```
Construction
├── Building
│   ├── Accessory (detached garage, pools, sheds)
│   ├── Dwelling Unit Finish
│   ├── New Construction
│   ├── Addition (Room, story, decks, dormers)
│   ├── Reroofs, Siding, Window Replacements
│   ├── Remodel
│   └── Flat roof only
├── Mechanical
│   ├── Fin Tube Radiation &/or In-floor heat
│   ├── Ductwork
│   ├── A/C replacement
│   └── Furnace replacement
├── Plumbing
│   ├── Bathtub install
│   ├── Shower install
│   ├── Toilet install
│   ├── Water Heater
│   ├── Gas appliances
│   └── [20+ other specific types]
└── Electrical
    ├── Circuit Installation
    ├── Service upgrades
    └── [other types]
```

### 2. Time Horizons
- **3-year**: 2023-2025
- **5-year**: 2020-2025  
- **10-year**: 2015-2025

### 3. Key Metrics to Extract

**For each Category → Sub-Category → Use Case:**

1. **Volume Metrics**
   - Total permits (actual count from data)
   - Permits by year (actual counts)
   - Monthly distribution (actual counts)
   - Geographic distribution (actual neighborhoods/wards from data)

2. **Approval Metrics**
   - Approval rate = (Status='Closed' count) / Total count
   - Rejection rate = (Status='Cancelled' count) / Total count
   - In-progress rate = (Status='Issued' or 'Inspection') / Total
   - Exact status distribution from data

3. **Timeline Metrics**
   - Processing time = completeDate - issueDate (only for records with both dates)
   - Report: mean, median, min, max, standard deviation
   - Only calculate for records with valid dates
   - Note any records with missing dates

4. **Applicant Analysis**
   - Identify homeowner vs contractor from applicantName field
   - Count exact occurrences
   - List top applicants with exact permit counts
   - Geographic distribution based on applicantAddress1

5. **Financial Metrics**
   - Sum of actual 'value' field
   - Average based on non-zero values only
   - Sum of actual 'totalFees' field
   - Note records with missing financial data

---

## Data Integrity Rules

### 1. Data Handling
- **Missing Data**: Explicitly note and exclude from calculations
- **Invalid Data**: Flag and report (e.g., negative values, future completion dates)
- **Calculations**: Only use records with complete data for each metric
- **Reporting**: Always show sample size (n=X) for each calculation

### 2. Citation Requirements
- Every metric must reference source: "Source: CCS_Permits.csv"
- Date range of data used
- Number of records included in calculation
- Any filters or exclusions applied

### 3. Web Research Citations (Future Phase)
- Company information: Include source URL and access date
- Market data: Cite specific source and date
- No unsourced claims or estimates

---

## Implementation Structure

### Phase 1: Data Pipeline (Jupyter Notebook)

```python
# Core components with data integrity checks:

1. data_loader.py
   - Load CCS_Permits.csv with validation
   - Load use cases mapping
   - Report data quality metrics
   - Flag any anomalies

2. data_processor.py
   - Map permits to hierarchy (only exact matches)
   - Calculate metrics (with sample sizes)
   - Handle missing data explicitly
   - Generate data quality report

3. analysis_notebook.ipynb
   - Document all calculations
   - Show sample data
   - Include data quality checks
   - Export only verified data
```

### Phase 2: Auto-Updating Web Framework

```
project/
├── data/
│   ├── raw/
│   │   ├── CCS_Permits.csv
│   │   └── use_cases.csv
│   └── processed/
│       ├── metrics_3yr.json
│       ├── metrics_5yr.json
│       ├── metrics_10yr.json
│       └── data_quality_report.json
├── scripts/
│   ├── process_data.py      # Main processing script
│   └── generate_web.py      # HTML generation
├── web/
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── pages/
│       ├── categories/
│       ├── subcategories/
│       └── use_cases/
└── run_analysis.sh          # One-click update script
```

### Key Features for Data Integrity

1. **Validation Pipeline**
   - Check data types
   - Validate date ranges
   - Confirm geographic coordinates
   - Verify financial values

2. **Transparent Reporting**
   - Show exact record counts
   - Display calculation methods
   - Note exclusions and why
   - Provide raw data access

3. **Audit Trail**
   ```json
   {
     "metric": "average_processing_time",
     "value": 45.2,
     "unit": "days",
     "calculation": "mean(completeDate - issueDate)",
     "sample_size": 1234,
     "excluded_records": 56,
     "exclusion_reason": "missing completeDate",
     "source": "CCS_Permits.csv",
     "date_range": "2015-01-01 to 2025-01-15"
   }
   ```

---

## Detailed Analysis Examples

### Plumbing Deep Dive

For the Plumbing category, analyze exactly what's in the data:
- Count permits for each plumbing type in use cases CSV
- Match permitType='Plumbing' records
- Cross-reference with workType and comments fields
- Report only found matches

**Metrics based on actual data:**
- Exact permit counts by type
- Actual applicant names and counts
- Real processing times from date fields
- Actual neighborhoods from data
- No extrapolation beyond what's recorded

---

## Web Output Structure

### Navigation Hierarchy
```
Home
├── Data Quality Report
├── Time Horizon Selector [3yr | 5yr | 10yr]
├── Categories Overview
│   ├── Construction
│   │   ├── Building
│   │   ├── Mechanical
│   │   ├── Plumbing
│   │   └── Electrical
├── Analytics Views
│   ├── Geographic Analysis
│   ├── Temporal Trends
│   ├── Applicant Analysis
│   └── Financial Overview
└── Data Export & Sources
```

### Page Components

**Every page includes:**
- Source citation
- Sample size (n=)
- Date range of data
- Calculation methodology
- Data quality notes
- Export raw data option

**Metrics displayed:**
- Only calculated values
- No projections or estimates
- Clear labeling of what's measured
- Missing data explicitly noted

---

## Automation Workflow with Validation

1. **Data Validation**
   ```python
   # validate_data.py
   - Check file integrity
   - Validate required columns
   - Report data quality issues
   - Generate validation report
   ```

2. **Processing with Checks**
   ```python
   # process_data.py
   - Load and validate data
   - Calculate only from complete records
   - Document all exclusions
   - Export metrics with metadata
   ```

3. **Web Generation with Sources**
   ```python
   # generate_web.py
   - Include source citations
   - Add calculation notes
   - Display sample sizes
   - Link to raw data
   ```

---

## Data Quality Standards

### Required for Each Metric
1. **Source**: Which file and fields used
2. **Sample Size**: Number of records included
3. **Exclusions**: Number excluded and why
4. **Method**: Exact calculation performed
5. **Date Range**: Period covered by data

### Handling Edge Cases
- **Missing issueDate**: Exclude from timeline analysis
- **Zero value**: Include in counts, note in averages
- **Multiple permits per address**: Count each separately
- **Unclear applicant type**: Create "Unknown" category

### Reporting Format
```
Metric: Average Processing Time - Plumbing Permits
Value: 23.4 days
Source: CCS_Permits.csv (issueDate, completeDate fields)
Records analyzed: 1,234 of 1,290 total plumbing permits
Excluded: 56 records (missing completeDate)
Date range: 2015-01-01 to 2025-01-15
Calculation: mean(completeDate - issueDate) where both dates present
```

---

## Future Enhancement: Web Research

When adding external research:
1. **Company Data**
   - Source: [Website URL]
   - Accessed: [Date]
   - Data point: [Specific fact]

2. **Industry Information**
   - Publication: [Name]
   - Date: [Publication date]
   - Page/Section: [Reference]

3. **No Unsourced Claims**
   - If data isn't available, state "Data not available"
   - Never estimate or assume

---

This framework ensures complete data integrity and transparency in all analyses and reports.