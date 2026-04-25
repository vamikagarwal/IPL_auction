import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set page config
st.set_page_config(page_title="IPL Auction 2023 Dashboard", layout="wide")

# Configure styling
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Cache data loading
@st.cache_data
def load_data():
    st.write("📂 Loading datasets...")
    try:
        # Load auction data
        st.write("📊 Reading auction data...")
        auction_df = pd.read_csv('iplauction2023.csv')
        
        # Load player stats
        st.write("📈 Reading player statistics...")
        player_df = pd.read_csv('cricket_data.csv')
        
        # Load points table (optional)
        st.write("🏆 Reading points table...")
        points_df = pd.read_csv('ipl_playoffs.csv')
        
        return auction_df, player_df, points_df
    except FileNotFoundError as e:
        st.error(f"❌ CSV file not found: {str(e)}")
        st.error("Please ensure all CSV files are in the project directory.")
        return None, None, None
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None, None, None

# Data preprocessing
@st.cache_data
def preprocess_data(auction_df, player_df, points_df):
    try:
        st.write("🔧 Preprocessing auction data...")
        
        # Clean auction data
        auction_df = auction_df.copy()
        auction_df.columns = auction_df.columns.str.strip().str.lower()
        
        # Map column names from actual CSV
        auction_df = auction_df.rename(columns={
            'name': 'Player',
            'player style': 'Role',
            'final price (in lacs)': 'Price',
            'franchise': 'Team',
            'base price (in lacs)': 'BasePrice'
        })
        
        # Keep only necessary columns
        auction_df = auction_df[['Player', 'Team', 'Role', 'Price', 'status']].copy()
        
        # Add Year column for consistency
        auction_df['Year'] = 2023
        
        # Clean player data
        st.write("🔧 Preprocessing player statistics...")
        player_df = player_df.copy()
        player_df.columns = player_df.columns.str.strip().str.lower()
        
        # Create explicit rename mapping based on actual column names in cricket_data.csv
        rename_cols_player = {
            'player_name': 'Player',
            'year': 'Year',
            'runs_scored': 'Runs',
            'wickets_taken': 'Wickets',
            'matches_batted': 'Matches_Batted',
            'matches_bowled': 'Matches_Bowled'
        }
        
        # Only rename columns that exist
        rename_cols_player = {k: v for k, v in rename_cols_player.items() if k in player_df.columns}
        player_df = player_df.rename(columns=rename_cols_player)
        
        # Filter for 2023 data and remove "No stats" entries
        if 'Year' in player_df.columns:
            player_df = player_df[player_df['Year'] != 'No stats'].copy()
            player_df['Year'] = pd.to_numeric(player_df['Year'], errors='coerce')
            player_df_2023 = player_df[player_df['Year'] == 2023].copy()
        else:
            player_df_2023 = player_df.copy()
        
        # Ensure we have at least some data
        if len(player_df_2023) == 0:
            player_df_2023 = player_df.copy()
        
        # Handle missing values in player data - use the renamed column names
        if 'Runs' in player_df_2023.columns:
            player_df_2023['Runs'] = pd.to_numeric(player_df_2023['Runs'].astype(str), errors='coerce').fillna(0)
        else:
            player_df_2023['Runs'] = pd.Series([0] * len(player_df_2023), index=player_df_2023.index)
            
        if 'Wickets' in player_df_2023.columns:
            player_df_2023['Wickets'] = pd.to_numeric(player_df_2023['Wickets'].astype(str), errors='coerce').fillna(0)
        else:
            player_df_2023['Wickets'] = pd.Series([0] * len(player_df_2023), index=player_df_2023.index)
            
        if 'Matches_Batted' in player_df_2023.columns:
            player_df_2023['Matches_Batted'] = pd.to_numeric(player_df_2023['Matches_Batted'].astype(str), errors='coerce').fillna(1)
        else:
            player_df_2023['Matches_Batted'] = pd.Series([1] * len(player_df_2023), index=player_df_2023.index)
            
        if 'Matches_Bowled' in player_df_2023.columns:
            player_df_2023['Matches_Bowled'] = pd.to_numeric(player_df_2023['Matches_Bowled'].astype(str), errors='coerce').fillna(1)
        else:
            player_df_2023['Matches_Bowled'] = pd.Series([1] * len(player_df_2023), index=player_df_2023.index)
        
        # Compute normalized metrics
        player_df_2023['Runs_per_match'] = player_df_2023['Runs'] / player_df_2023['Matches_Batted'].replace(0, 1)
        player_df_2023['Wickets_per_match'] = player_df_2023['Wickets'] / player_df_2023['Matches_Bowled'].replace(0, 1)
        
        # Add Capped status (assume 1 if played in 2023)
        player_df_2023['Capped'] = 1
        
        # Select needed columns - only those that exist
        cols_to_select = [col for col in ['Player', 'Runs', 'Wickets', 'Matches_Batted', 'Matches_Bowled', 
                                           'Runs_per_match', 'Wickets_per_match', 'Capped'] if col in player_df_2023.columns]
        player_df_2023 = player_df_2023[cols_to_select].copy()
        
        st.write("🔗 Merging datasets...")
        # Merge auction and player data on Player name
        merged_df = pd.merge(auction_df, player_df_2023, on='Player', how='left')
        
        # Fill missing values
        merged_df['Runs'] = merged_df['Runs'].fillna(0)
        merged_df['Wickets'] = merged_df['Wickets'].fillna(0)
        merged_df['Matches_Batted'] = merged_df['Matches_Batted'].fillna(1)
        merged_df['Matches_Bowled'] = merged_df['Matches_Bowled'].fillna(1)
        merged_df['Runs_per_match'] = merged_df['Runs_per_match'].fillna(0)
        merged_df['Wickets_per_match'] = merged_df['Wickets_per_match'].fillna(0)
        merged_df['Capped'] = merged_df['Capped'].fillna(0)
        
        # ROI Calculation
        st.write("📊 Calculating ROI metrics...")
        merged_df['Performance_Score'] = merged_df['Runs_per_match'] + (merged_df['Wickets_per_match'] * 20)
        merged_df['ROI'] = np.where(merged_df['Price'] > 0, merged_df['Performance_Score'] / merged_df['Price'], 0)
        
        # Clean Role column
        merged_df['Role'] = merged_df['Role'].str.strip().str.title()
        
        st.write("✅ Data preprocessing complete!")
        return merged_df, points_df
    except Exception as e:
        st.error(f"❌ Error preprocessing data: {str(e)}")
        import traceback
        st.error(traceback.format_exc())
        return None, None

# Load and preprocess data
st.write("🚀 Initializing IPL Auction 2023 Dashboard...")
auction_df, player_df, points_df = load_data()
if auction_df is None:
    st.stop()

df, points_df = preprocess_data(auction_df, player_df, points_df)
if df is None:
    st.stop()

st.success("✅ Data loaded successfully!")

# Sidebar navigation
st.sidebar.title("🏏 IPL Auction 2023 Dashboard")
st.sidebar.markdown("---")
page = st.sidebar.radio("📍 Select Section", [
    "🎯 Player ROI Analysis",
    "💼 Team Strategy Breakdown", 
    "💎 Uncapped Gems",
    "🪑 Bench Warmers",
    "📊 Statistical Analysis",
    "📈 Visual Analysis",
    "📋 Data Overview"
])

# Player ROI Analysis
if page == "🎯 Player ROI Analysis":
    st.header("🎯 Player ROI Analysis")
    st.markdown("Analyze player return on investment based on performance metrics")
    
    col1, col2 = st.columns(2)
    with col1:
        team_filter = st.selectbox("Select Team", ["All"] + sorted(df['Team'].unique()))
    with col2:
        player_filter = st.selectbox("Select Player", ["All"] + sorted(df['Player'].unique()))
    
    filtered_df = df.copy()
    if team_filter != "All":
        filtered_df = filtered_df[filtered_df['Team'] == team_filter]
    if player_filter != "All":
        filtered_df = filtered_df[filtered_df['Player'] == player_filter]
    
    if not filtered_df.empty:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_roi = filtered_df['ROI'].mean()
            st.metric("Average ROI", f"{avg_roi:.4f}")
        with col2:
            total_price = filtered_df['Price'].sum()
            st.metric("Total Budget (Cr)", f"₹{total_price:.1f}")
        with col3:
            player_count = len(filtered_df)
            st.metric("Player Count", player_count)
    
    st.subheader("🏆 Top 10 Players by ROI")
    top10 = df.nlargest(10, 'ROI')[['Player', 'Team', 'Role', 'Price', 'ROI']]
    st.dataframe(top10, use_container_width=True)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    top10_plot = df.nlargest(10, 'ROI')
    sns.barplot(data=top10_plot, y='Player', x='ROI', ax=ax, palette='viridis')
    ax.set_title("Top 10 Players by ROI", fontsize=14, fontweight='bold')
    ax.set_xlabel("ROI Score")
    st.pyplot(fig)

# Team Strategy Breakdown
elif page == "💼 Team Strategy Breakdown":
    st.header("💼 Team Strategy Breakdown")
    st.markdown("Analyze how teams distributed their auction budget across player roles")
    
    st.subheader("💰 Budget Distribution by Role")
    col1, col2 = st.columns(2)
    
    with col1:
        fig, ax = plt.subplots(figsize=(8, 8))
        role_budget = df.groupby('Role')['Price'].sum()
        colors = plt.cm.Set3(np.linspace(0, 1, len(role_budget)))
        ax.pie(role_budget, labels=role_budget.index, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title("Total Budget by Role", fontsize=12, fontweight='bold')
        st.pyplot(fig)
    
    with col2:
        fig, ax = plt.subplots(figsize=(8, 6))
        role_stats = df.groupby('Role')['Price'].agg(['sum', 'count', 'mean'])
        role_stats.columns = ['Total Budget (₹ Cr)', 'Player Count', 'Avg Price (₹ Cr)']
        st.dataframe(role_stats, use_container_width=True)
    
    st.subheader("📊 Spending Histogram by Role")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(data=df, x='Price', hue='Role', ax=ax, multiple="stack", bins=20)
    ax.set_title("Price Distribution by Role", fontsize=12, fontweight='bold')
    ax.set_xlabel("Price (₹ Cr)")
    st.pyplot(fig)
    
    st.subheader("👥 Players with ROI Analysis")
    team_selected = st.selectbox("Filter by Team:", ["All"] + sorted(df['Team'].unique()), key='team_roi')
    if team_selected == "All":
        display_df = df
    else:
        display_df = df[df['Team'] == team_selected]
    
    st.dataframe(display_df[['Player', 'Team', 'Role', 'Price', 'Runs', 'Wickets', 'ROI']].sort_values('ROI', ascending=False), 
                 use_container_width=True)

# Uncapped Gems
elif page == "💎 Uncapped Gems":
    st.header("💎 Uncapped Gems - High ROI Performers")
    st.markdown("Identify uncapped players (no prior IPL experience) who delivered exceptional value")
    
    uncapped = df[df['Capped'] == 0]
    if len(uncapped) > 0:
        roi_75th = uncapped['ROI'].quantile(0.75)
        gems = uncapped[uncapped['ROI'] > roi_75th].sort_values('ROI', ascending=False)
        
        st.metric("Uncapped Gems Found", len(gems))
        
        if len(gems) > 0:
            st.subheader("💎 Top Uncapped Performers")
            st.dataframe(gems[['Player', 'Team', 'Role', 'Price', 'Runs', 'Wickets', 'ROI']], use_container_width=True)
            
            st.subheader("📊 Uncapped Gems ROI Visualization")
            fig, ax = plt.subplots(figsize=(12, 6))
            sns.barplot(data=gems.head(15), x='Player', y='ROI', ax=ax, palette='coolwarm')
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
            ax.set_title("Top 15 Uncapped Gems by ROI", fontsize=12, fontweight='bold')
            st.pyplot(fig)
        else:
            st.info("No uncapped gems found above 75th percentile")
    else:
        st.warning("No uncapped players in dataset")

# Bench Warmers
elif page == "🪑 Bench Warmers":
    st.header("🪑 Bench Warmers - Money Wasted")
    st.markdown("Identify overpaid players with underperformance")
    
    price_median = df['Price'].median()
    roi_25th = df['ROI'].quantile(0.25)
    
    bench_warmers = df[(df['Price'] > price_median) & (df['ROI'] < roi_25th)].sort_values('Price', ascending=False)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Price Threshold (₹ Cr)", f"{price_median:.1f}")
    with col2:
        st.metric("ROI Threshold", f"{roi_25th:.4f}")
    with col3:
        st.metric("Bench Warmers Found", len(bench_warmers))
    
    st.subheader("📉 Bench Warmer Details")
    st.dataframe(bench_warmers[['Player', 'Team', 'Role', 'Price', 'ROI', 'Runs', 'Wickets']], use_container_width=True)
    
    st.subheader("💸 Team-wise Wasted Budget")
    if len(bench_warmers) > 0:
        wasted_budget = bench_warmers.groupby('Team')['Price'].sum().reset_index().sort_values('Price', ascending=False)
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=wasted_budget, x='Team', y='Price', ax=ax, palette='Reds')
        ax.set_title("Wasted Budget by Team (₹ Cr)", fontsize=12, fontweight='bold')
        ax.set_ylabel("Total Wasted Budget (₹ Cr)")
        st.pyplot(fig)
    else:
        st.info("No bench warmers found with current thresholds")

# Statistical Analysis
elif page == "📊 Statistical Analysis":
    st.header("📊 Statistical Analysis")
    st.markdown("Deep dive into statistical relationships in the auction data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔄 Chi-Square Test: Role vs Performance")
        # Create performance categories using qcut for quantile-based binning
        try:
            # First create bins without labels to see how many we get
            performance_bins = pd.qcut(df['ROI'], q=3, duplicates='drop')
            num_bins = len(performance_bins.unique())
            
            # Create appropriate labels based on actual number of bins
            if num_bins == 3:
                labels = ['Low', 'Medium', 'High']
            elif num_bins == 2:
                labels = ['Low', 'High']
            else:
                labels = [f'Category_{i}' for i in range(num_bins)]
            
            # Re-create with proper labels
            df['Performance_Category'] = pd.qcut(df['ROI'], q=3, labels=labels, duplicates='drop')
            
            contingency_table = pd.crosstab(df['Role'], df['Performance_Category'])
            chi2, p, dof, expected = stats.chi2_contingency(contingency_table)
            
            st.metric("Chi-Square Statistic", f"{chi2:.4f}")
            st.metric("P-value", f"{p:.4f}")
            st.metric("Degrees of Freedom", dof)
            
            if p < 0.05:
                st.success("✅ Significant relationship between Role and Performance")
            else:
                st.info("ℹ️ No significant relationship between Role and Performance")
        except Exception as e:
            st.warning(f"Unable to perform chi-square test: {str(e)}")
    
    with col2:
        st.subheader("📈 T-Test: Capped vs Uncapped Players")
        capped_roi = df[df['Capped'] == 1]['ROI']
        uncapped_roi = df[df['Capped'] == 0]['ROI']
        
        if len(uncapped_roi) > 1 and len(capped_roi) > 1:
            t_stat, p_val = stats.ttest_ind(capped_roi, uncapped_roi)
            st.metric("T-Statistic", f"{t_stat:.4f}")
            st.metric("P-value", f"{p_val:.4f}")
            
            if p_val < 0.05:
                st.success("✅ Significant difference in ROI between groups")
            else:
                st.info("ℹ️ No significant difference in ROI between groups")
        else:
            st.warning("Insufficient data for t-test")

# Visual Analysis
elif page == "📈 Visual Analysis":
    st.header("📈 Visual Analysis")
    st.markdown("Comprehensive visualizations of player performance and budget allocation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Histogram of ROI (with KDE)")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.histplot(df['ROI'], kde=True, ax=ax, bins=30, color='skyblue')
        ax.set_title("Distribution of ROI", fontsize=12, fontweight='bold')
        ax.set_xlabel("ROI Score")
        st.pyplot(fig)
    
    with col2:
        st.subheader("📦 Box Plot: ROI vs Role")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.boxplot(data=df, x='Role', y='ROI', ax=ax, palette='Set2')
        ax.set_title("ROI Distribution by Role", fontsize=12, fontweight='bold')
        st.pyplot(fig)
    
    st.subheader("💰 Scatter Plot: Price vs Performance Score")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.scatterplot(data=df, x='Price', y='Performance_Score', hue='Role', s=100, ax=ax, alpha=0.6)
    ax.set_title("Price vs Performance Score", fontsize=12, fontweight='bold')
    ax.set_xlabel("Price (₹ Cr)")
    ax.set_ylabel("Performance Score")
    st.pyplot(fig)
    
    st.subheader("🏆 Team-wise ROI Box Plot")
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.boxplot(data=df, x='Team', y='ROI', ax=ax, palette='husl')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    ax.set_title("ROI Distribution by Team", fontsize=12, fontweight='bold')
    st.pyplot(fig)
    
    st.subheader("🔝 Top vs Bottom ROI Players")
    top10_roi = df.nlargest(10, 'ROI')['ROI'].values
    bottom10_roi = df.nsmallest(10, 'ROI')['ROI'].values
    comparison_df = pd.DataFrame({
        'Group': ['Top 10'] * len(top10_roi) + ['Bottom 10'] * len(bottom10_roi),
        'ROI': list(top10_roi) + list(bottom10_roi)
    })
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.boxplot(data=comparison_df, x='Group', y='ROI', ax=ax, palette='Set1')
    ax.set_title("Top 10 vs Bottom 10 ROI Players", fontsize=12, fontweight='bold')
    st.pyplot(fig)

# Data Overview
elif page == "📋 Data Overview":
    st.header("📋 Data Overview")
    st.markdown("Summary statistics and data quality checks")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Players", len(df))
    with col2:
        st.metric("Teams", df['Team'].nunique())
    with col3:
        st.metric("Total Budget (₹ Cr)", f"{df['Price'].sum():.1f}")
    with col4:
        st.metric("Avg Player Price (₹ Cr)", f"{df['Price'].mean():.2f}")
    
    st.subheader("📊 Summary Statistics")
    summary_stats = df[['Price', 'ROI', 'Runs', 'Wickets']].describe()
    st.dataframe(summary_stats, use_container_width=True)
    
    st.subheader("👥 Players by Role")
    role_dist = df['Role'].value_counts()
    fig, ax = plt.subplots(figsize=(10, 6))
    role_dist.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title("Player Distribution by Role", fontsize=12, fontweight='bold')
    ax.set_xlabel("Role")
    ax.set_ylabel("Count")
    plt.tight_layout()
    st.pyplot(fig)
    
    st.subheader("🏟️ Players by Team")
    team_dist = df['Team'].value_counts()
    fig, ax = plt.subplots(figsize=(12, 6))
    team_dist.plot(kind='bar', ax=ax, color='lightcoral')
    ax.set_title("Player Count by Team", fontsize=12, fontweight='bold')
    ax.set_xlabel("Team")
    ax.set_ylabel("Count")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)
    
    st.subheader("📋 Full Dataset")
    st.dataframe(df.sort_values('ROI', ascending=False), use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("🏏 IPL Auction 2023 Dashboard\n\nAnalyzing player ROI and team strategies")
