# Product Requirements Document
## Minneapolis Permits Data Analysis & Market Intelligence Platform

### Document Version
- Version: 1.0
- Date: July 23, 2025
- Author: System Generated PRD

---

## 1. Executive Summary

This PRD outlines the development of a comprehensive data analysis and market intelligence platform for Minneapolis building permits. The platform will analyze 10 years of permit data to identify market opportunities, track industry trends, and provide actionable insights for different market segments and customer personas.

### Key Objectives
- Transform raw permit data into actionable market intelligence
- Identify high-growth segments and market leaders
- Provide multi-level analysis from overview to detailed segment insights
- Enable data-driven decision making for business development

---

## 2. Problem Statement

### Current Challenges
1. **Data Complexity**: The Minneapolis permits dataset contains extensive information but lacks structured analysis
2. **Market Blindness**: Difficult to identify market trends, opportunities, and key players without proper segmentation
3. **Actionable Insights Gap**: Raw data doesn't translate to business opportunities
4. **Segment Understanding**: Limited visibility into specific market segments' dynamics

### Business Opportunity
By analyzing 10 years of permit data across defined segments, we can:
- Identify underserved markets
- Track market growth patterns
- Discover key players and potential partners/customers
- Understand regulatory patterns and processing inefficiencies

---

## 3. User Personas

### Primary Users
1. **Business Development Manager**
   - Needs: Market size data, growth trends, competitor analysis
   - Goals: Identify new business opportunities and potential customers
   
2. **Strategic Analyst**
   - Needs: Deep market insights, trend analysis, segment performance
   - Goals: Make data-driven recommendations for market entry

3. **Sales Executive**
   - Needs: Lead lists, market leader identification, contact information
   - Goals: Target high-value prospects in growing segments

### Secondary Users
1. **Executive Leadership**
   - Needs: High-level market overview, growth opportunities
   - Goals: Strategic decision making

2. **Marketing Manager**
   - Needs: Market segment characteristics, customer profiles
   - Goals: Targeted marketing campaigns

---

## 4. Functional Requirements

### Phase 1: Exploratory Data Analysis (Jupyter Notebook)

#### 4.1 Data Processing & Cleaning
- Load and parse CCS_Permits.csv (10 years of data)
- Handle missing values and data quality issues
- Standardize date formats and categorical variables
- Merge with segmentation data from "Mpls Use Cases - Minneapolis (1).csv"

#### 4.2 Comprehensive Analysis Dimensions
1. **Temporal Analysis**
   - Yearly trends by segment
   - Seasonal patterns
   - Growth rates (YoY, CAGR)
   - Processing time trends

2. **Geographic Analysis**
   - Permits by neighborhood
   - Ward-level analysis
   - Heat maps of activity
   - Geographic clustering

3. **Segment Analysis**
   - Volume by category/subcategory
   - Value distribution
   - Rejection rates
   - Processing times
   - Fee analysis

4. **Market Leader Analysis**
   - Top applicants by segment
   - Market share calculation
   - Frequency analysis
   - Success rate comparison

5. **Financial Analysis**
   - Total market value by segment
   - Average project values
   - Fee revenue analysis
   - Value concentration

#### 4.3 Executive Summary Generation
- Key findings and insights
- Market opportunity scoring
- Risk factors
- Recommendations for further investigation

### Phase 2: Web-Based Intelligence Platform

#### 4.4 Technical Architecture
- Static HTML/CSS/JavaScript website
- Self-contained (no backend required)
- Responsive design for all devices
- Fast loading and navigation

#### 4.5 Navigation Structure
```
Home (Overview Dashboard)
├── Segment Categories
│   ├── Construction
│   │   ├── Building
│   │   ├── Electrical
│   │   ├── Mechanical
│   │   └── Plumbing
│   ├── Renovation
│   ├── Commercial
│   └── Residential
├── Geographic View
├── Timeline Analysis
└── Market Leaders
```

#### 4.6 Page Requirements

**Level 1: Overview Dashboard**
- Executive summary cards
- Key metrics visualization
- Segment comparison chart
- Market size treemap
- Growth trend indicators
- Quick navigation to segments

**Level 2: Segment Pages**
- Segment-specific metrics
- Growth charts
- Geographic distribution
- Top players list
- Processing time analysis
- Drill-down navigation

**Level 3: Detailed Analysis**
- Sub-segment breakdowns
- Individual player profiles
- Time series analysis
- Comparative metrics
- Export capabilities

#### 4.7 Interactive Features
- Filterable data tables
- Interactive charts (hover, zoom)
- Search functionality
- Comparison tools
- Data export options

### Phase 3: Market Intelligence Enhancement

#### 4.8 Customer Research Integration
- Placeholder for web research findings
- Company profiles template
- Contact information structure
- Business opportunity scoring

#### 4.9 Opportunity Scoring Model
- Market size factor
- Growth rate factor
- Competition density
- Regulatory complexity
- Entry barrier assessment

---

## 5. Non-Functional Requirements

### 5.1 Performance
- Page load time < 3 seconds
- Smooth interactions and transitions
- Efficient data handling for large datasets

### 5.2 Usability
- Intuitive navigation
- Clear data visualization
- Mobile-responsive design
- Accessibility compliance (WCAG 2.1)

### 5.3 Data Quality
- Accuracy validation
- Completeness checks
- Consistency verification
- Regular update capability

### 5.4 Security & Privacy
- No sensitive data exposure
- Compliance with data regulations
- Secure hosting considerations

---

## 6. Data Schema & Relationships

### 6.1 Primary Data Sources
1. **CCS_Permits.csv**
   - Location data (coordinates, addresses, neighborhoods, wards)
   - Permit details (type, status, work type)
   - Financial data (value, fees)
   - Timeline data (issue date, complete date)
   - Applicant information

2. **Mpls Use Cases - Minneapolis (1).csv**
   - Use case categorization
   - Category/Sub-category hierarchy
   - Persona mapping
   - Fee structures
   - Submission requirements

### 6.2 Derived Metrics
- Processing time = complete_date - issue_date
- Rejection rate = cancelled/total by segment
- Market share = applicant permits/total segment permits
- Growth rate = (current year - previous year)/previous year

---

## 7. Success Metrics

### 7.1 Analysis Quality
- Coverage of all major segments
- Identification of top 20 players per segment
- Accurate trend detection
- Actionable insights generation

### 7.2 Platform Usability
- User task completion rate > 90%
- Information discovery time < 2 minutes
- Data accuracy validation > 99%

### 7.3 Business Impact
- Identification of 10+ market opportunities
- Market sizing accuracy
- Lead generation potential
- Strategic decision support

---

## 8. Implementation Phases

### Phase 1: Data Analysis Foundation (Week 1-2)
- Jupyter notebook development
- Comprehensive EDA
- Initial insights generation
- Executive summary creation

### Phase 2: Web Platform Development (Week 3-4)
- HTML/CSS/JavaScript structure
- Interactive visualizations
- Navigation implementation
- Responsive design

### Phase 3: Enhancement & Optimization (Week 5)
- Performance optimization
- Additional features
- User testing
- Documentation

### Phase 4: Market Intelligence Layer (Week 6+)
- Web research integration
- Company profiling
- Opportunity scoring
- Final recommendations

---

## 9. Risks & Mitigation

### 9.1 Data Quality Risks
- **Risk**: Incomplete or inconsistent data
- **Mitigation**: Robust cleaning and validation processes

### 9.2 Analysis Risks
- **Risk**: Misinterpretation of trends
- **Mitigation**: Multiple validation approaches, peer review

### 9.3 Technical Risks
- **Risk**: Performance issues with large datasets
- **Mitigation**: Data preprocessing, efficient visualization libraries

---

## 10. Future Enhancements

### 10.1 Potential Features
- Real-time data updates
- Predictive analytics
- API integration
- Automated reporting
- CRM integration

### 10.2 Extended Analysis
- Competitor benchmarking
- Economic impact correlation
- Weather/seasonal factors
- Regulatory change impact

---

## 11. Appendix

### 11.1 Sample Visualizations
- Market size treemap
- Growth trend line charts
- Geographic heat maps
- Market leader bar charts
- Processing time distributions

### 11.2 Technology Stack
- **Analysis**: Python, Pandas, Matplotlib, Seaborn, Plotly
- **Web**: HTML5, CSS3, JavaScript, D3.js, Chart.js
- **Hosting**: Static site hosting (GitHub Pages, Netlify, etc.)

### 11.3 Deliverables Checklist
- [ ] Jupyter notebook with comprehensive analysis
- [ ] Executive summary document
- [ ] Static website with navigation
- [ ] Segment analysis pages
- [ ] Market leader profiles
- [ ] Documentation and user guide

---

*This PRD serves as the foundational document for the Minneapolis Permits Analysis project. It should be reviewed and updated as new requirements emerge during development.*