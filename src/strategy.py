import pandas as pd

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
