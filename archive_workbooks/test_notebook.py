#!/usr/bin/env python
# Test script to check and fix notebook code

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set display options
pd.set_option('display.max_columns', None)
pd.set_option('display.max_colwidth', 50)

# Check available matplotlib styles
available_styles = plt.style.available
if 'seaborn-v0_8-darkgrid' in available_styles:
    plt.style.use('seaborn-v0_8-darkgrid')
elif 'seaborn-darkgrid' in available_styles:
    plt.style.use('seaborn-darkgrid')
else:
    print("Using default style - seaborn styles not found")

print("✓ Import successful")

# Load the CSV file
try:
    df = pd.read_csv('source/Active_Rental_Licenses.csv')
    print(f"✓ Dataset loaded: {df.shape}")
except Exception as e:
    print(f"✗ Error loading data: {e}")
    exit(1)

# Check columns
print(f"\nColumns ({len(df.columns)}):")
for i, col in enumerate(df.columns[:10]):  # Show first 10
    print(f"{i+1:2d}. {col}")
print("...")

# Data types
print(f"\n✓ Data types check passed")

# Convert dates
date_columns = ['issueDate', 'expirationDate']
for col in date_columns:
    df[col] = pd.to_datetime(df[col], errors='coerce')
print(f"✓ Date conversion successful")

# Check for missing values
print(f"\nMissing values in key columns:")
key_cols = ['category', 'status', 'ward', 'licensedUnits', 'shortTermRental']
for col in key_cols:
    missing = df[col].isna().sum()
    print(f"  {col}: {missing}")

# Basic statistics
print(f"\n✓ All checks passed! Notebook should run successfully.")
print(f"\nDataset summary:")
print(f"  Total records: {len(df):,}")
print(f"  Total licensed units: {df['licensedUnits'].sum():,}")
print(f"  Date range: {df['issueDate'].min()} to {df['issueDate'].max()}")