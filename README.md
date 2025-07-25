# Minneapolis Building Permits Analysis Dashboard

A comprehensive analysis dashboard for Minneapolis building permits data, providing detailed insights into permit categories, applicants, and trends.

## 🏗️ Live Dashboard

[View Live Dashboard](https://your-deployed-url.onrender.com) *(URL will be updated after deployment)*

## 📊 What's Included

### Main Reports
- **Category Overview**: Analysis of all 7 permit categories (Building, Mechanical, Plumbing, Solar, Wrecking, Sign, Soil Erosion)
- **Top 100 Applicants**: Ranking of most active permit applicants by volume and value
- **Detailed Category Reports**: In-depth drill-down analysis for each category

### Key Metrics
- **358,301** total permits analyzed
- **$31.4 billion** in total construction value
- **21,139** unique applicants
- **7** major permit categories

## 🗂️ Data Source

**Primary Dataset**: Minneapolis Community Planning & Economic Development (CPED)
- Source file: `CCS_Permits.csv` (358,301 records)
- Use case mapping: `Mpls Use Cases - Minneapolis (1).csv`
- Analysis period: Complete permit database through July 2025

## 📁 Repository Structure

```
/
├── index.html                          # Main dashboard landing page
├── reports/                            # All analysis reports
│   ├── permit_analysis_by_category.html
│   ├── applicant_analysis.html
│   ├── use_case_analysis.csv
│   └── drill_down_reports/
│       ├── summary_dashboard.html
│       ├── building_detailed_report.html
│       ├── mechanical_detailed_report.html
│       ├── plumbing_detailed_report.html
│       ├── solar_detailed_report.html
│       ├── wrecking_detailed_report.html
│       ├── sign_detailed_report.html
│       └── soil_erosion_detailed_report.html
├── scripts/                            # Analysis Python scripts
├── README.md
└── .gitignore
```

## 🛠️ Technology Stack

- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Styling**: Modern CSS Grid and Flexbox
- **Data Processing**: Python with pandas
- **Hosting**: Render (static site hosting)
- **Version Control**: GitHub

## 📈 Analysis Features

### Category Analysis
- Permit volume and value breakdowns
- Processing time analysis
- Use case categorization
- Top applicants by category

### Applicant Analysis
- Top 100 applicants by permit volume
- Contractor vs. property owner classification
- Specialization patterns
- Performance metrics

### Detailed Reports
- Complete applicant lists (not limited to top 100)
- Abandonment analysis (cancelled, withdrawn, stop work orders)
- Geographic distribution patterns
- Temporal trends and seasonality
- Processing time analysis
- Downloadable CSV data

## 🚀 Deployment

This dashboard is automatically deployed via:
1. **GitHub Integration**: Push to main branch triggers deployment
2. **Render Static Hosting**: Free tier with 100GB bandwidth
3. **Custom Domain**: Can be configured post-deployment

## 📊 Key Insights

### Permit Distribution
- **Plumbing**: 40.0% (143,258 permits)
- **Building**: 37.5% (134,239 permits)  
- **Mechanical**: 21.2% (76,075 permits)
- **Other categories**: 1.3% combined

### Top Use Cases
1. **Gas meter installations**: 36,565 permits
2. **Water heater replacements**: 27,459 permits
3. **A/C and heat pump installations**: 22,058 permits
4. **Remodeling projects**: 43,814 permits

### Processing Efficiency
- **Average processing time**: 275-468 days (varies by category)
- **Abandonment rate**: 2.0% overall (7,227 permits)
- **Completion rate**: 82.8-90.4% (varies by category)

## 🏢 Top Applicants

1. **CenterPoint Energy Resource Corp**: 36,566 permits (gas meters)
2. **Urban Pine Plumbing and Mechanical**: 14,738 permits
3. **Standard Heating and Air Conditioning**: 11,756 permits
4. **RENEWAL BY ANDERSEN CORP**: 8,826 permits (windows/siding)
5. **ZEMAN CONSTRUCTION CO**: 6,824 permits (remodeling)

## 📅 Last Updated

**July 25, 2025** - Complete dataset through 2025

## 📝 License

This project is for research and analysis purposes. Data is publicly available from Minneapolis CPED.

## 🤝 Contributing

This is a research project by MillCityAI. For questions or suggestions, please open an issue.

---

**MillCityAI Research** | *Building insights from city data*