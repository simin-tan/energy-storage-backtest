"""
Generates a local SQLite database with mock hourly electricity price data,
used as the input for pipeline.py.

Deliberately injects one duplicate timestamp and one missing (null) price
value, so pipeline.py's cleaning logic has something real to handle.
"""

import sqlite3
import numpy as np
import pandas as pd


def create_mock_database(db_path="energy_market.db"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS market_prices (
            timestamp TEXT,
            electricity_price_eur_mwh REAL
        )
    ''')

    # Generate 7 days of hourly mock data (168 hours)
    np.random.seed(42)
    timestamps = pd.date_range(start="2026-03-25", periods=168, freq="h") \
        .strftime('%Y-%m-%d %H:%M:%S').tolist()
    prices = np.random.normal(loc=50, scale=20, size=168).tolist()  # avg 50 EUR/MWh

    # Inject a duplicate timestamp and a null price to exercise the cleaning logic
    timestamps.append(timestamps[-1])
    prices.append(prices[-1])
    timestamps.insert(10, timestamps[10])
    prices.insert(10, None)

    cursor.executemany(
        "INSERT INTO market_prices VALUES (?, ?)",
        zip(timestamps, prices)
    )
    conn.commit()
    conn.close()
    print(f"Mock database created at {db_path}")


if __name__ == "__main__":
    create_mock_database()
