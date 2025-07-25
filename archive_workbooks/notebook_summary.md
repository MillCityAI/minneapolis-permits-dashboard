# Minneapolis Rental Licenses Analysis - Summary

## Setup Complete ✓

### Environment
- **Active Environment**: mcai_env (Python 3.10.16)
- **Required Packages Installed**: pandas, numpy, matplotlib, seaborn, jupyter, notebook

### Notebook Created
- **File**: `rental_licenses_exploration.ipynb`
- **Status**: Ready to run with all dependencies installed

### Dataset
- **File**: `source/Active_Rental_Licenses.csv`
- **Records**: 23,075 active rental licenses
- **Total Units**: 120,328 licensed units
- **Date Range**: 1991-2025

### Notebook Contents

1. **Data Loading & Overview**
   - Dataset shape and structure
   - Column information (38 columns)
   - Data types and missing values

2. **Data Cleaning**
   - Date conversion for issueDate and expirationDate
   - Handling missing values in ward data (255 missing)

3. **License Categories Analysis**
   - Distribution of license types (CHOWN, CONV, etc.)
   - Status breakdown (Active vs Delinquent)

4. **Geographic Analysis**
   - Distribution by ward (1-13)
   - Top neighborhoods by license count
   - Geographic scatter plots

5. **Licensed Units Analysis**
   - Statistics on units per property
   - Total units by ward

6. **Short-Term Rental Analysis**
   - Percentage of short-term vs long-term rentals

7. **Time-based Analysis**
   - Licenses issued by year (trend analysis)
   - Upcoming expirations tracking

8. **Owner Analysis**
   - Top property owners
   - Out-of-state ownership patterns

9. **Geographic Visualization**
   - Map scatter plots of all properties
   - Color-coded visualization by ward

10. **Summary Statistics**
    - Comprehensive summary of key metrics

### How to Run

```bash
# Activate the environment
source ~/miniconda3/bin/activate mcai_env

# Launch Jupyter Notebook
jupyter notebook rental_licenses_exploration.ipynb
```

The notebook is now running at: http://localhost:8888/tree?token=9905de85f4f5584d6fc9d8d605917ad784f16bbdcc78ac55

### Notes
- The matplotlib style has been fixed to handle different seaborn versions
- All required packages are installed in the mcai_env
- The notebook includes comprehensive error handling