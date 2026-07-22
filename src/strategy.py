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
        
    # Battery parameters
    battery_capacity_mwh = 1.0
    charge_rate_mwh = 1.0
    discharge_rate_mwh = 1.0
    battery_efficiency = 0.85 # 85% round-trip efficiency factor 
    
    # Current battery state
    state_of_charge_mwh = 0.0

    # Initialize simulation output columns
    backtest_df['revenue_eur'] = 0.0
    backtest_df['state_of_charge_mwh'] = 0.0
    
    # Simulate battery operation over time
    for index, row in backtest_df.iterrows():

        action = row['action']
        price = row['electricity_price_eur_mwh']

        # Charge the battery if there is available capacity
        if action == 'CHARGE' and state_of_charge_mwh < battery_capacity_mwh:

            state_of_charge_mwh = min(
                battery_capacity_mwh,
                state_of_charge_mwh + charge_rate_mwh
            )

            backtest_df.at[index, 'revenue_eur'] = -price

        # Discharge the battery if energy is available
        elif action == 'DISCHARGE' and state_of_charge_mwh > 0:

            state_of_charge_mwh = max(
                0,
                state_of_charge_mwh - discharge_rate_mwh
            )

            backtest_df.at[index, 'revenue_eur'] = (
                price * battery_efficiency
            )

        # Record the battery state after this timestep
        backtest_df.at[index, 'state_of_charge_mwh'] = state_of_charge_mwh

    total_profit = backtest_df['revenue_eur'].sum()
    print(f"--- Backtest Results ---")
    print(f"Total simulated trading profit: {total_profit:.2f} EUR")
    print(f"Final battery state of charge: {state_of_charge_mwh:.1f} MWh")
    
    return backtest_df
