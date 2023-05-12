from datetime import datetime as dt
import sqlite3
from numpy import array, cumsum, log, polyfit, sqrt, std, subtract
from numpy.random import randn
import pandas as pd

con = sqlite3.connect("top_100_crypto.db")


def hurst(time_series):
    """
    Calculates the Hurst Exponent of the time series vector ts.
    Parameters
    ----------
    ts : 'np.ndarray'
    Time series array of prices
    Returns
    -------
    'float'
    The Hurst Exponent of the time series
    """
    # Create the range of lag values
    lags = range(2, 100)
    # Calculate the array of the variances of the lagged differences
    tau = [sqrt(std(subtract(time_series[lag:], time_series[:-lag]))) for lag in lags]
    # Use a linear fit to estimate the Hurst Exponent
    poly = polyfit(log(lags), log(tau), 1)
    # Return the Hurst exponent from the polyfit output
    return poly[0] * 2.0


if __name__ == "__main__":
    # Create a Gometric Brownian Motion, Mean-Reverting and Trending Series
    gbm = log(cumsum(randn(100000)) + 1000)
    mr = log(randn(100000) + 1000)
    tr = log(cumsum(randn(100000) + 1) + 1000)
    # Download the ETH OHLCV data from 1/1/2018 to 1/1/2023
    start_date = dt(2018, 1, 1)
    end_date = dt(2023, 1, 1)
    sql = f"""SELECT dp.price_date, dp.adj_close_price
      FROM symbol AS sym
      INNER JOIN daily_price AS dp
      ON dp.symbol_id = sym.id
      WHERE sym.ticker = 'ETH'
      AND dp.price_date BETWEEN '{start_date}' AND '{end_date}'
      ORDER BY dp.price_date ASC;"""
    # Create a pandas dataframe from the SQL query
    eth = pd.read_sql_query(sql, con=con, index_col="price_date")
    # Output the Hurst Exponent for each of the above series
    # and the price of ETH (the Adjusted Close price)
    print("Hurst(GBM): %0.2f" % hurst(gbm))
    print("Hurst(MR): %0.2f" % hurst(mr))
    print("Hurst(TR): %0.2f" % hurst(tr))
    # Calculate the Hurst exponent for the ETH adjusted closing prices
    print("Hurst(ETH): %0.2f" % hurst(array(eth["adj_close_price"].tolist())))

# The goal of the Hurst Exponent is to find wheather the scalar value is mean reverting, randomly walking or trending
# Hurst(GBM): 0.50
# Hurst(MR): 0.00
# Hurst(TR): 0.96
# Hurst(ETH): 0.49
