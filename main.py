from bin.stats.sharpe import equity_sharpe
from bin.sql.query import get_daily_data
from datetime import datetime as dt


if __name__ == "__main__":
    start_date = dt(2018, 1, 1)
    end_date = dt(2023, 1, 1)

    eth = get_daily_data("eth", start_date, end_date, ["adj_close_price"])

    print(eth)
