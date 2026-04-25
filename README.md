# IPL Auction 2023 Data Analysis Dashboard

A comprehensive Streamlit dashboard for analyzing IPL Auction 2023 data, including detailed player ROI calculations, team strategies, uncapped gems identification, and statistical insights.

## Features

✨ **Player ROI Analysis**: Filter by team/player, view detailed metrics, top 10 performers
💼 **Team Strategy Breakdown**: Budget distribution, role-wise spending, team comparisons
💎 **Uncapped Gems**: Identify high-ROI uncapped (debutant) players
🪑 **Bench Warmers**: Analyze overpaid underperformers and wasted budget
📊 **Statistical Analysis**: Chi-square tests, t-tests with interpretations
📈 **Visual Analysis**: ROI histograms, box plots, scatter plots, team comparisons
📋 **Data Overview**: Summary statistics and comprehensive data exploration

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Place CSV files** in the project directory with these exact names:
   - `iplauction2023.csv` - IPL Auction 2023 data
   - `cricket_data.csv` - Player stats (runs, wickets, matches)
   - `ipl_playoffs.csv` - IPL points table data

3. **Run the dashboard**:
   ```bash
   streamlit run app.py
   ```

The app will open in your browser (http://localhost:8501)

## Dataset Information

### iplauction2023.csv
Auction details for IPL 2023 including:
- Player names
- Player roles (Bowler, Batter, Allrounder, WK-Batter)
- Base & final prices (in lacs)
- Teams (franchises)
- Auction status (SOLD, UNSOLD, RETAINED)

### cricket_data.csv
Career and season statistics including:
- Player year-wise performance
- Runs scored, wickets taken
- Matches played (batting & bowling)
- Batting averages and strike rates
- Bowling averages and economy rates

### ipl_playoffs.csv
IPL playoff & tournament data

## Key Metrics

- **ROI (Return on Investment)**: Performance Score / Price
  - Performance Score = Runs/Match + (Wickets/Match × 20)
  - Normalized metrics handle players without complete stats

- **Uncapped Gems**: Players above 75th percentile ROI with no prior IPL stats
- **Bench Warmers**: High-price players with ROI below 25th percentile
- **Team Strategy**: Budget allocation across player roles

## Technologies Used

- **Streamlit**: Interactive web dashboard
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Matplotlib & Seaborn**: Data visualizations
- **SciPy**: Statistical tests

## Usage

1. Navigate through sections using the sidebar menu
2. Use filters to compare specific teams or players
3. Hover over charts for detailed information
4. View statistical tests for data-driven insights
5. Export data using the data overview section

## Dashboard Sections

### 🎯 Player ROI Analysis
- Filter players by team
- View top 10 ROI performers
- Compare individual player metrics

### 💼 Team Strategy Breakdown
- Role-wise budget distribution
- Spending patterns by team
- Player performance by team

### 💎 Uncapped Gems
- Players with high ROI but no prior IPL experience
- Identify valuable debutants
- Visualize uncapped player performance

### 🪑 Bench Warmers
- Identify overpaid underperformers
- Team-wise wasted budget analysis
- Overspending trends

### 📊 Statistical Analysis
- Chi-square test: Role vs Performance
- T-test: Capped vs Uncapped players
- P-values and interpretations

### 📈 Visual Analysis
- ROI distribution histograms
- Role-wise performance boxes
- Price vs Performance scatter plots
- Team-wise ROI comparisons

### 📋 Data Overview
- Summary statistics
- Data quality metrics
- Full dataset exploration

## Data Sources

- **IPL Auction 2023**: Original auction data
- **IPL Player Stats**: Historical and 2023 performance data
- **IPL Playoffs**: Tournament structure data

## Notes

- Analysis focuses strictly on 2023 auction data
- Normalized metrics used for fair ROI calculation
- Missing values handled with appropriate defaults
- All prices in crores (₹ Cr)
- ROI calculations handle division by zero safely

## Author

Created for comprehensive IPL auction analysis using Streamlit
