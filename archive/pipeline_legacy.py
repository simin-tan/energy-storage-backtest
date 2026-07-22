"""
Deprecated.
Replaced by src/main.py.

Kept for reference only.
"""
import sqlite3
import pandas as pd
import plotly.graph_objects as go

def fetch_and_clean_data(db_path="energy_market.db"):
    # 1. Pull data via SQL
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM market_prices", conn)
    conn.close()
    
    print(f"Raw rows fetched from DB: {len(df)}")
    
    # 2. Schema handling & Data Quality checks
    df = df.dropna(subset=['electricity_price_eur_mwh']) # Remove nulls
    
    # Clean text and force conversion to datetime objects
    df['timestamp'] = df['timestamp'].astype(str).str.strip()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # 3. GROUP BY TIMESTAMP to merge duplicate entries by taking the mean price
    # This prevents any downstream "duplicate labels" crashes
    df = df.groupby('timestamp', as_index=True).mean()
    
    # 4. Handle European timezone safely (accounting for standard/daylight savings)
    df = df.tz_localize('Europe/Berlin', ambiguous='NaT', nonexistent='shift_forward')
    df = df.tz_convert('UTC')
    
    print(f"Cleaned rows processed: {len(df)}")
    return df

def run_battery_backtest(df):
    """
    A simple algorithmic trading strategy:
    Buy (Charge) when prices are in the lowest 25% of the week.
    Sell (Discharge) when prices are in the highest 25% of the week.
    """
    # Create a fresh copy to prevent setting-with-copy alerts
    backtest_df = df.copy()
    
    # Define thresholds using pandas quantiles
    low_threshold = backtest_df['electricity_price_eur_mwh'].quantile(0.25)
    high_threshold = backtest_df['electricity_price_eur_mwh'].quantile(0.75)
    
    # Initialize trading decisions using numpy vectorization
    backtest_df['action'] = 'HOLD'
    backtest_df.loc[backtest_df['electricity_price_eur_mwh'] <= low_threshold, 'action'] = 'CHARGE'
    backtest_df.loc[backtest_df['electricity_price_eur_mwh'] >= high_threshold, 'action'] = 'DISCHARGE'
    
    # Financial metrics logic (Assuming a 1 MW battery capacity)
    battery_efficiency = 0.85 # 85% round-trip efficiency factor
    
    # Initialize revenue column
    backtest_df['revenue_eur'] = 0.0
    
    # Extract arrays using .values to completely bypass pandas series reindexing checks
    prices = backtest_df['electricity_price_eur_mwh'].values
    
    # Apply calculations smoothly using the masks
    charge_mask = (backtest_df['action'] == 'CHARGE').values
    discharge_mask = (backtest_df['action'] == 'DISCHARGE').values
    
    backtest_df.loc[charge_mask, 'revenue_eur'] = -prices[charge_mask]
    backtest_df.loc[discharge_mask, 'revenue_eur'] = prices[discharge_mask] * battery_efficiency
    
    total_profit = backtest_df['revenue_eur'].sum()
    print(f"--- Backtest Results ---")
    print(f"Total simulated trading profit: {total_profit:.2f} EUR")
    
    return backtest_df

def generate_report(df):
    # Create an interactive plot showing the market prices
    fig = go.Figure()
    
    # Add the base market electricity price line
    fig.add_trace(go.Scatter(
        x=df.index, 
        y=df['electricity_price_eur_mwh'],
        mode='lines',
        name='Electricity Price (EUR/MWh)',
        line=dict(color='gray', width=1)
    ))
    
    # Highlight Charge points
    charge_events = df[df['action'] == 'CHARGE']
    fig.add_trace(go.Scatter(
        x=charge_events.index, 
        y=charge_events['electricity_price_eur_mwh'],
        mode='markers',
        name='Battery Charging (Buying)',
        marker=dict(color='green', size=7)
    ))
    
    # Highlight Discharge points
    discharge_events = df[df['action'] == 'DISCHARGE']
    fig.add_trace(go.Scatter(
        x=discharge_events.index, 
        y=discharge_events['electricity_price_eur_mwh'],
        mode='markers',
        name='Battery Discharging (Selling)',
        marker=dict(color='red', size=7)
    ))
    
    fig.update_layout(
        title="Automated Battery Storage Asset Backtest Simulation",
        xaxis_title="Timestamp (UTC)",
        yaxis_title="EUR / MWh",
        template="plotly_dark"
    )
    
    # Automatically export it as a clean HTML file
    fig.write_html("battery_performance_report.html")
    print("Interactive HTML report generated successfully!")

# The single execution block that runs everything sequentially
if __name__ == "__main__":
    cleaned_df = fetch_and_clean_data()
    simulated_data = run_battery_backtest(cleaned_df)
    generate_report(simulated_data)