from bin.stats.sharpe import equity_sharpe
from bin.sql.query import get_daily_data
from bin.stats.var import var_cov_var
from datetime import datetime as dt
import numpy as np


if __name__ == "__main__":
    start_date = dt(2018, 1, 1)
    end_date = dt(2023, 1, 1)

    eth = get_daily_data("eth", start_date, end_date, ["adj_close_price"])
    # SHARPE RATIO
    # sr = equity_sharpe(eth)
    # print(sr)

    # VALUE AT RISK
    P = 1e6  # 1,000,000 USD
    c = 0.99  # 99% confidence interval
    eth["rets"] = eth["adj_close_price"].pct_change()

    mu = np.mean(eth["rets"])
    sigma = np.std(eth["rets"])
    var = var_cov_var(P, c, mu, sigma)
    print("Value-at-Risk: $%0.2f" % var)
