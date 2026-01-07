# State Comparison Dashboard

An interactive Python desktop application for comparing U.S. states based on safety metrics and housing affordability. This tool helps individuals and families make informed relocation decisions by analyzing real-time crime data and rental costs across all 50 states. *REQUIRES PRIVATE API KEY PLEASE MAKE YOUR OWN IN THE COMMENTED CODE OR HAVE THE CSV FILE IN THE SAME DIRECTORY*

## Problem Statement

**Target Audience:** Individuals and families considering relocation within the United States

**Problem:** Making relocation decisions is complex and overwhelming. People need to balance multiple factors including safety, affordability, and quality of life, but lack a centralized tool to compare states objectively using real-time data.

**Solution:** This dashboard aggregates crime statistics and rental cost data from authoritative government sources, providing an interactive comparison tool that helps users identify states that best match their priorities for safety and affordability.

**Measurable Impact:**
- Reduces research time from hours to minutes
- Provides objective, data-driven comparisons
- Enables customized analysis based on individual priorities
- Delivers real-time insights from authoritative government sources

## Project Description

The State Comparison Dashboard is a comprehensive data analysis tool that:
- Fetches live crime statistics from the FBI Crime Data Explorer API
- Retrieves current rental market data from the HUD Fair Market Rent API
- Processes and normalizes data for all 50 U.S. states
- Provides interactive visualizations and statistical analysis
- Enables customizable scoring based on user preferences

The application features two comparison modes: individual state comparison (2-3 states) and regional analysis (Northeast, South, Midwest, West), with six visualization panels showing overall scores, safety vs. affordability tradeoffs, crime trends, rental costs, and statistical distributions.

## Installation

### Prerequisites

- Python 3.7 or higher
- Internet connection (required for initial data fetch)
- Approximately 5 MB of disk space for cached data

### Step 1: Install Dependencies

Install required Python libraries using pip:

```bash
pip install pandas matplotlib numpy scipy requests
```

**Note on tkinter:** This library usually comes pre-installed with Python. If you encounter an import error:
- **Ubuntu/Debian:** `sudo apt-get install python3-tk`
- **macOS:** Included with Python from python.org
- **Windows:** Included with standard Python installation

Alternatively, install from requirements.txt:

```bash
pip install -r requirements.txt
```

### Step 2: Download Files

Download these files to the same directory:
- `StateDashboard.py` (main application file)
- `requirements.txt` (optional, for easier installation)

### Step 3: Run the Application

Navigate to the directory containing the files and execute:

```bash
python StateDashboard.py
```

**First Run (2-3 minutes):**
The application will automatically:
1. Fetch 2024 crime data from FBI Crime Data Explorer API for all 50 states
2. Retrieve current rental prices from HUD Fair Market Rent API
3. Process, clean, and merge the datasets
4. Calculate safety and affordability scores
5. Save processed data as `state_data.csv` for faster future loading

**Subsequent Runs (instant):**
The application loads from the cached `state_data.csv` file.

## Usage

### Quick Start Guide

1. **Launch the application**
   ```bash
   python StateDashboard.py
   ```

2. **Select comparison mode**
   - Choose "Compare States" for individual state analysis
   - Choose "Compare Regions" for regional comparisons

3. **Select locations**
   - State Mode: Select 2-3 states from dropdown menus
   - Regional Mode: Select 2-4 regions to compare

4. **Customize your analysis**
   - Adjust the weight slider (Safety 0% - 100% Affordability)
   - Select bedroom count (1, 2, 3, or 4 bedrooms)
   - Toggle "Show Distribution" for statistical analysis views

5. **Interpret results**
   - View six interactive visualization panels
   - Read detailed statistics in the text output panel
   - Compare head-to-head metrics

### State Comparison Mode

**Purpose:** Compare individual states side-by-side

**Steps:**
1. Select "Compare States" from the mode dropdown
2. Choose 2-3 states from dropdown menus (prevents duplicate selections)
3. Adjust safety/affordability weight slider (default: 50/50)
4. Select preferred bedroom count for rental data
5. Toggle "Show Distribution" to view box plots instead of averages
6. Analyze the six visualization panels and text output

**Best for:** Narrowing down specific state options for relocation

### Regional Comparison Mode

**Purpose:** Analyze and compare U.S. geographic regions

**Steps:**
1. Select "Compare Regions" from the mode dropdown
2. Choose 2-4 regions (Northeast, South, Midwest, West)
3. Adjust weights and settings as desired
4. View top 5 states within each region
5. Explore regional crime patterns and trends

**Best for:** Understanding geographic patterns and identifying promising regions before drilling down to specific states

### Understanding Metrics

| Metric | Range | Description |
|--------|-------|-------------|
| **Overall Score** | 0-100 | Weighted combination of safety and affordability based on your preference settings (higher is better) |
| **Safety Score** | 0-100 | Inverse logarithmic transformation of crime rates (higher means lower crime) |
| **Affordability Score** | 0-100 | Inverse relationship to rental costs, normalized nationally (higher means lower rent) |
| **Crime Rate** | Per 100k | Combined violent and property crime incidents per 100,000 residents (lower is safer) |
| **Rent** | $/month | Average fair market rent for selected bedroom count |

**How Scoring Works:**
- Overall Score = (Safety Score × Safety Weight) + (Affordability Score × Affordability Weight)
- Safety Score uses inverse logarithmic transformation to handle wide range of crime rates
- Affordability Score normalizes rental costs against national averages
- All scores are on 0-100 scale for easy comparison

## Features

### Data Acquisition
- **Automated data fetching** from two authoritative government APIs
- **FBI Crime Data Explorer API:** Monthly violent and property crime rates for 2024
- **HUD Fair Market Rent API:** Current rental prices for 1-4 bedroom apartments
- **All 50 states coverage:** Comprehensive U.S. data
- **Smart caching:** Saves processed data locally for faster subsequent launches

### Data Processing & Analysis
- **Data cleaning:** Handles missing values and outliers
- **Normalization:** Scales diverse metrics to comparable ranges
- **Statistical analysis:** Calculates means, distributions, trends, and correlations
- **Trend detection:** Linear regression with directional indicators (↑↓→)
- **Score calculation:** Customizable weighted scoring system

### Visualization Dashboard

**Six-panel layout (3x2 grid):**

1. **Overall Score Comparison:** Bar chart showing composite scores for selected states/regions
2. **Safety vs. Affordability:** Scatter plot revealing tradeoffs between metrics
3. **Crime Rate Analysis:** Monthly trends or box plot distributions
4. **Rent Comparison:** Cost analysis across selections with bar charts or distributions
5. **Top States Ranking:** Lists top 5 states by region with scores
6. **Monthly Crime Trends:** Seasonal patterns showing crime variations throughout the year

**Interactive features:**
- Real-time updates as settings change
- Distribution toggle for statistical depth
- Color-coded visualizations for easy interpretation
- Detailed labels and legends

### Customization Options
- **Adjustable weighting:** Slider to prioritize safety (0%) vs. affordability (100%)
- **Bedroom selection:** Choose 1, 2, 3, or 4-bedroom rental data
- **Distribution views:** Toggle between averages and full statistical distributions
- **Regional filtering:** Focus analysis on specific U.S. regions
- **Dynamic scoring:** Scores recalculate instantly with preference changes

## Data Sources

### FBI Crime Data Explorer API
- **Source:** Federal Bureau of Investigation Crime Data Explorer
- **URL:** https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi
- **Data:** Monthly violent and property crime rates by state
- **Year:** 2024
- **Coverage:** All 50 U.S. states
- **Update Frequency:** Monthly
- **Metrics:** Violent crime rate (per 100k), Property crime rate (per 100k)

### HUD Fair Market Rent API
- **Source:** U.S. Department of Housing and Urban Development
- **URL:** https://www.huduser.gov/portal/dataset/fmr-api.html
- **Data:** Fair Market Rent for 1-4 bedroom apartments
- **Year:** 2024
- **Coverage:** State averages across all counties
- **Metrics:** Average rental costs by bedroom count

## Technical Implementation

### Architecture

**Data Pipeline:**
1. API data fetching with error handling and retry logic
2. Data cleaning and validation (handle missing values, outliers)
3. Data merging and normalization
4. Score calculation using weighted algorithms
5. Statistical analysis (trends, distributions, correlations)
6. Real-time visualization rendering

**Key Libraries:**
- **pandas:** Data manipulation and analysis
- **matplotlib:** Data visualization and charting
- **numpy:** Numerical computations
- **scipy:** Statistical analysis and regression
- **requests:** API calls and data fetching
- **tkinter:** GUI framework

### Scoring Methodology

**Safety Score Calculation:**
```
crime_rate = violent_rate + property_rate
safety_score = 100 - (log(crime_rate) * normalization_factor)
```
Uses inverse logarithmic transformation to handle wide range of crime rates while maintaining meaningful differences.

**Affordability Score Calculation:**
```
affordability_score = 100 - ((rent - min_rent) / (max_rent - min_rent) * 100)
```
Normalizes rental costs across states to 0-100 scale, where higher scores indicate lower costs.

**Overall Score:**
```
overall_score = (safety_score × safety_weight) + (affordability_score × affordability_weight)
```
Weighted average based on user-defined priorities.

### Crime Trend Analysis
- Linear regression for trend detection over 12-month period
- Slope analysis to determine trend direction
- Directional indicators: ↑ (increasing), ↓ (decreasing), → (stable)
- Seasonal pattern identification through monthly averaging

## Troubleshooting

### Common Issues

**Problem:** `ModuleNotFoundError` for pandas, matplotlib, etc.
**Solution:** Install missing dependencies: `pip install [package-name]`

**Problem:** API request failures or timeout errors
**Solution:** Check internet connection. Government APIs can be slow or temporarily unavailable. Wait a few minutes and try again.

**Problem:** `tkinter` import error
**Solution:** Install tkinter for your operating system (see Installation section Step 1)

**Problem:** Data appears outdated
**Solution:** Delete `state_data.csv` file and restart application to fetch fresh data

**Problem:** Slow performance or laggy visualizations
**Solution:** Reduce number of states/regions being compared, or close resource-intensive applications

**Problem:** Some states show missing data
**Solution:** API may be temporarily unavailable for certain states. Try refreshing or check API status.

## Team Members

This project was developed collaboratively by:

- **Taehoon** - Data acquisition and API integration setup
- **Rish** - Crime trends analysis and visualization development, slides
- **Irene** - Relocation analysis methodology and scoring algorithms
- **Jessica** - Data cleaning and processing, dashboard development, safety/affordability scoring system, code integration and testing, README documentation

## Citations

### Data Sources

**FBI Crime Data:**
Federal Bureau of Investigation. (2024). *Crime Data Explorer: Summarized State-Level Data*. Retrieved from https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi

**HUD Rental Data:**
U.S. Department of Housing and Urban Development. (2024). *Fair Market Rent Documentation System API*. HUD User. Retrieved from https://www.huduser.gov/portal/dataset/fmr-api.html

### APIs Used

**FBI Crime Data Explorer API**
- Endpoint: `https://api.usa.gov/crime/fbi/cde/summarized/state/`
- Data: Monthly violent and property crime rates by state (2024)
- API Key: Public key provided by FBI Crime Data Explorer

**HUD Fair Market Rent API**
- Endpoint: `https://www.huduser.gov/hudapi/public/fmr/statedata/`
- Data: Fair Market Rent for 1-4 bedroom apartments by state (2024)
- Authorization: Bearer token for HUD User API

### Dashboard Architecture & Visualization

The dashboard implementation draws inspiration from open-source Tkinter + Matplotlib dashboard patterns:

**Interactive Data Visualization Dashboard**
- Repository: [divagarva/Interactive-Data-Visualization-Dashboard-with-Python](https://github.com/divagarva/Interactive-Data-Visualization-Dashboard-with-Python)
- Reference for: Interactive dashboard creation using Tkinter and Matplotlib with dynamic plot generation

**Professional Dashboard Development Guide**
- Repository: [michaelgermini/Building-Professional-Dashboards-with-Python-and-Tkinter](https://github.com/michaelgermini/Building-Professional-Dashboards-with-Python-and-Tkinter)
- Reference for: Professional dashboard architecture patterns, data visualization best practices, and MVC design patterns

**Matplotlib-Tkinter Dashboard Template**
- Repository: [codefirstio/tkinter-matplotlib-dashboard](https://github.com/codefirstio/tkinter-matplotlib-dashboard)
- Reference for: FigureCanvasTkAgg integration patterns for embedding Matplotlib charts in Tkinter

### AI Assistance

This project utilized generative AI tools for technical guidance:

**Claude (Anthropic)** - Provided guidance on:
- Converting widget-based interactions to direct function calls for dashboard rendering
- Tkinter implementation and UI styling recommendations
- Code structure and integration best practices
- Python visualization techniques with matplotlib

**Note:** All AI-generated suggestions were reviewed, tested, and adapted by the team. The AI served as a technical advisor rather than generating complete code solutions.

## Technical Challenges & Solutions

### Challenge 1: API Rate Limiting
**Issue:** FBI and HUD APIs have occasional timeouts which caused issues to where the necessary API calls required to get county level crime data took too long and the requests returned a 503 error code after hours of running.
**Solution:** Implemented local caching system that saves processed data to CSV file, reducing API calls to once per data refresh. We also had to adjust scope and transition from the county level to state level crime and rent data.

### Challenge 2: Data Consistency
**Issue:** Some states had incomplete monthly crime data
**Solution:** Added data validation and error handling to gracefully handle missing values and provide user feedback

### Challenge 3: Real-time Visualization Updates
**Issue:** Matplotlib rendering can be slow when updating multiple plots
**Solution:** Optimized figure clearing and redrawing logic; implemented efficient data filtering before visualization

### Challenge 4: Score Normalization
**Issue:** Crime rates and rental costs have vastly different scales
**Solution:** Developed logarithmic transformation for crime data and percentage-based normalization for rents to create comparable 0-100 scores

## Future Improvements

Potential enhancements for future versions:

- **Additional data sources:** Cost of living indices, employment rates, weather data, school ratings
- **Export functionality:** Save reports as PDF or Excel files
- **Historical comparisons:** Track how states change over time with multi-year data
- **More visualizations:** Heat maps, correlation matrices, migration flow charts
- **Web version:** Browser-based dashboard for easier access without installation
- **Custom weighting profiles:** Save and load multiple preference configurations
- **Manual data refresh:** Button to update data without restarting application

## License

This project uses publicly available government data from the FBI and HUD. Please refer to their respective terms of use:
- [FBI Crime Data Explorer Terms](https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi)
- [HUD User Data Terms](https://www.huduser.gov/portal/about/terms_of_use.html)

## Disclaimer

This dashboard is for informational and educational purposes only. Crime rates and rental costs are subject to change and may not reflect real-time conditions. Always conduct thorough research and consult with professionals before making relocation decisions. The scores and rankings are based on the selected weighting preferences and may not reflect individual priorities or circumstances.

---

**Note:** API keys included in the source code are public keys provided by the respective government agencies. If you encounter rate limiting, you may need to obtain your own API keys from the [FBI Crime Data Explorer](https://cde.ucr.cjis.gov/LATEST/webapp/#/pages/docApi) and [HUD User Data](https://www.huduser.gov/portal/home.html) portals.
