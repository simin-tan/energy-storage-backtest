from data_loader import fetch_and_clean_data
from strategy import run_battery_backtest
from report import generate_report


def main():

    cleaned_df = fetch_and_clean_data()

    simulated_data = run_battery_backtest(
        cleaned_df
    )

    generate_report(
        simulated_data
    )


if __name__ == "__main__":
    main()
