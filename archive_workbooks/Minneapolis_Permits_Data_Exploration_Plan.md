# Minneapolis Permits Data Exploration Plan

## Overview
This document outlines a systematic approach to extract, organize, and present data from the Minneapolis permits dataset (2015-2025) without interpretation or business conclusions. The goal is to create clear, detailed reports that facilitate further discussion.

---

## Data Sources
1. **Primary Dataset**: `source/CCS_Permits.csv`
   - 10 years of Minneapolis building permits
   - Contains: location, permit details, financials, timeline, applicant info

2. **Segmentation Reference**: `Mpls Use Cases - Minneapolis (1).csv`
   - Categories and subcategories for permit classification
   - Use case definitions

---

## Phase 1: Jupyter Notebook - Data Extraction & Reporting

### 1.1 Initial Data Exploration
- Dataset dimensions (rows, columns)
- Column descriptions and data types
- Date range coverage
- Missing data summary

### 1.2 Segment-Based Data Extraction

For each category/subcategory combination:

**Volume Metrics**
- Total permit count
- Permits by year (2015-2025)
- Permits by month
- Permits by day of week

**Status Breakdown**
- Count by status (Closed, Issued, Cancelled, etc.)
- Status distribution percentages

**Geographic Distribution**
- Permits by neighborhood
- Permits by ward
- Top 10 neighborhoods
- Geographic coordinates distribution

**Timeline Metrics**
- Average days from issue to completion
- Distribution of processing times
- Minimum/maximum processing times
- Processing time by year

**Financial Metrics**
- Total project values
- Average project value
- Value distribution (quartiles)
- Total fees collected
- Average fee amount
- Fee as percentage of project value

**Applicant Analysis**
- Top 20 applicants by permit count
- Permit distribution among applicants
- Applicant location distribution

### 1.3 Cross-Segment Comparisons

**Comparative Tables**
- All segments by total permits
- All segments by total value
- All segments by average processing time
- All segments by rejection rate
- Year-over-year growth rates by segment

### 1.4 Data Quality Report
- Records with missing critical fields
- Data anomalies (e.g., negative values, future dates)
- Coordinate accuracy assessment

---

## Phase 2: Web-Based Data Presentation

### 2.1 Structure
```
index.html (Overview)
├── segments/
│   ├── [category-subcategory].html
│   └── comparison.html
├── geographic/
│   ├── neighborhoods.html
│   └── wards.html
├── temporal/
│   ├── yearly.html
│   └── monthly.html
└── applicants/
    └── top-performers.html
```

### 2.2 Overview Page Content
- Total permits count
- Date range
- Number of unique applicants
- Total project value
- Geographic coverage map
- Segment breakdown table

### 2.3 Segment Pages
Each segment page will display:
- Permit count and trend chart
- Status distribution pie chart
- Processing time histogram
- Geographic distribution map
- Top applicants table
- Monthly/yearly trends
- Value distribution chart

### 2.4 Data Tables
All data presented in:
- Sortable tables
- Downloadable CSV format
- Clear labeling
- Numerical precision (2 decimal places)

---

## Deliverables

### Jupyter Notebook Output
1. **Data_Exploration.ipynb**
   - All code for data processing
   - Inline visualizations
   - Extracted data tables
   - Export functions for web data

2. **Extracted_Data/**
   - CSV files for each segment
   - Summary statistics files
   - Cross-segment comparison files

### Web Platform
1. **Static Website**
   - Clean, navigable interface
   - All data visualizations
   - Downloadable data tables
   - No interpretation or recommendations

### Data Reports (Markdown)
1. **Segment_Reports/**
   - One file per segment
   - Pure data presentation
   - Tables and charts only

---

## Execution Timeline

**Week 1: Data Processing**
- Load and clean data
- Create segment mappings
- Calculate all metrics
- Generate initial reports

**Week 2: Visualization**
- Create all charts
- Build web structure
- Implement navigation
- Test data accuracy

**Week 3: Finalization**
- Quality checks
- Performance optimization
- Documentation
- Delivery

---

## Notes
- No business interpretation
- No recommendations
- No opportunity identification
- Just clear, accurate data presentation
- Focus on completeness and clarity