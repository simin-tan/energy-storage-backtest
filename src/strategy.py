import pandas as pd

def run_battery_backtest(df, interval_hours=1.0):
    """
    A simple algorithmic trading strategy:
    Buy (Charge) when prices are in the lowest 25% of the input data.
    Sell (Discharge) when prices are in the highest 25% of the input data.
    
    Note: thresholds are computed over the entire `df` passed in. 
    This matches a single week of input but would need revisiting 
    for multi-week datasets.

    Args:
        df: DataFrame with an 'electricity_price_eur_mwh' column, one row
            per time step.
        interval_hours: Length of each row's time step, in hours
            (e.g. 1.0 for hourly data, 0.25 for 15-min data). Must match
            the actual granularity of df, or the energy/power conversion
            will be silently wrong.

    Returns:
        A copy of df with added 'action', 'revenue_eur',
        'energy_traded_mwh', and 'state_of_charge_mwh' columns.
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
    max_charge_power_mw = 1.0
    max_discharge_power_mw = 1.0

    # Apply round-trip efficiency as separate charging and discharging losses
    round_trip_efficiency = 0.85
    charge_efficiency = round_trip_efficiency ** 0.5 
    discharge_efficiency = round_trip_efficiency ** 0.5
    
    # Current battery state
    state_of_charge_mwh = 0.0

    # Initialize simulation output columns
    backtest_df['revenue_eur'] = 0.0
    backtest_df['energy_traded_mwh'] = 0.0
    backtest_df['state_of_charge_mwh'] = 0.0
    
    # Simulate battery operation over time
    for index, row in backtest_df.iterrows():
        
        action = row['action']
        price = row['electricity_price_eur_mwh']

        # Charge the battery if there is available capacity
        if action == 'CHARGE' and state_of_charge_mwh < battery_capacity_mwh:

            headroom_mwh = battery_capacity_mwh - state_of_charge_mwh

            energy_from_grid_mwh = min(
                max_charge_power_mw * interval_hours,
                headroom_mwh / charge_efficiency
            )
            
            state_of_charge_mwh += energy_from_grid_mwh * charge_efficiency

            backtest_df.at[index, 'revenue_eur'] = -price * energy_from_grid_mwh
            backtest_df.at[index, 'energy_traded_mwh'] = energy_from_grid_mwh

        # Discharge the battery if energy is available
        elif action == 'DISCHARGE' and state_of_charge_mwh > 0:

            energy_from_battery_mwh = min(
                max_discharge_power_mw * interval_hours,
                state_of_charge_mwh
            )

            state_of_charge_mwh -= energy_from_battery_mwh
            energy_to_grid_mwh = energy_from_battery_mwh * discharge_efficiency

            backtest_df.at[index, 'revenue_eur'] = price * energy_to_grid_mwh 
            backtest_df.at[index, 'energy_traded_mwh'] = energy_from_battery_mwh

        # Record the battery state after this timestep
        backtest_df.at[index, 'state_of_charge_mwh'] = state_of_charge_mwh

    total_profit = backtest_df['revenue_eur'].sum()
    print("--- Backtest Results ---")
    print(f"Total simulated trading profit: {total_profit:.2f} EUR")
    print(f"Final battery state of charge: {state_of_charge_mwh:.1f} MWh")
    
    return backtest_df

