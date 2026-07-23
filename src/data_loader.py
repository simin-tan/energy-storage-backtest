import sqlite3
import pandas as pd

def fetch_and_clean_data(db_path="data/energy_market.db"):
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
    
    # 5. Drop rows made ambiguous by the DST transition (see step 4).
    # ambiguous='NaT' marks the repeated fall-back hour as NaT rather than
    # guessing which offset it belongs to. These rows still have valid
    # prices and would otherwise be silently traded on with an unusable
    # timestamp, so they're removed here.
    n_before = len(df)
    df = df[df.index.notna()]
    n_dropped = n_before - len(df)
    if n_dropped:
        print(f"Dropped {n_dropped} row(s) with ambiguous DST timestamps")

    print(f"Cleaned rows processed: {len(df)}")
    return df
