# sharpe.py
import numpy as np
import pandas as pd


def annualised_sharpe(returns, N=360):
    """
    Calculate the annualised Sharpe ratio of a returns stream
    based on a number of trading periods, N. N defaults to 252,
    which then assumes a stream of daily returns.
    The function assumes that the returns are the excess of
    those compared to a benchmark.
    """
    return np.sqrt(N) * returns.mean() / returns.std()


def equity_sharpe(ticker):
    """
    Calculates the annualised Sharpe ratio based on the daily
    returns of an equity ticker symbol listed in the DB.
    """
    # Use the percentage change method to easily calculate daily returns
    ticker["daily_ret"] = ticker["adj_close_price"].pct_change()
    # Assume an average annual risk-free rate over the period of 5%
    ticker["excess_daily_ret"] = ticker["daily_ret"] - 0.05 / 360
    # Return the annualised Sharpe ratio based on the excess daily returns
    return annualised_sharpe(ticker["excess_daily_ret"])


def market_neutral_sharpe(ticker, benchmark):
    """
    Calculates the annualised Sharpe ratio of a market
    neutral long/short strategy inolving the long of 'ticker'
    with a corresponding short of the 'benchmark'.
    """
    # Calculate the percentage returns on each of the time series
    ticker["daily_ret"] = ticker["adj_close_price"].pct_change()
    benchmark["daily_ret"] = benchmark["adj_close_price"].pct_change()
    # Create a new DataFrame to store the strategy information
    # The net returns are (long - short)/2, since there is twice
    # the trading capital for this strategy
    strat = pd.DataFrame(index=ticker.index)
    strat["net_ret"] = (ticker["daily_ret"] - benchmark["daily_ret"]) / 2.0
    # Return the annualised Sharpe ratio for this strategy
    return annualised_sharpe(strat["net_ret"])


# if __name__ == "__main__":
#     start_date = dt(2018, 1, 1)
#     end_date = dt(2023, 1, 1)

#     eth = get_daily_data("eth", start_date, end_date, ["adj_close_price"])

#     # eth_sr = equity_sharpe(eth)


# print("AlphaBet Sharpe Ratio: %s" % equity_sharpe(eth))

# # print("AlphaBet Market Neutral Sharpe Ratio: %s" % market_neutral_sharpe(goog, spy))
