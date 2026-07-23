from data_loader import fetch_and_clean_data
from strategy import run_battery_backtest
from report import generate_report


def main():

    cleaned_df = fetch_and_clean_data()

    # interval_hours made explicit: current data source is hourly.
    # If energy_market.db is ever regenerated at a different resolution
    # (e.g. 15-min), this must be updated to match, or energy/revenue
    # calculations will be silently wrong.
    simulated_data = run_battery_backtest(cleaned_df, interval_hours=1.0)

    generate_report(simulated_data)


if __name__ == "__main__":
    main()
