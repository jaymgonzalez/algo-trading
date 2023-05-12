import os
from datetime import datetime as dt
import pprint
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.tsa.stattools as ts
import sqlite3
from matplotlib.dates import date2num


##### TODO: fix xaxis datetime. it starts in the 70's
def plot_price_series(df, ts1, ts2, start_date, end_date):
    """
    Plot both time series on the same line graph for
    the specified date range.
    Parameters
    ----------
    df : 'pd.DataFrame'
    The DataFrame containing prices for each series
    ts1 : 'str'
    The first time series column name
    ts2 : 'str'
    The second time series column name
    start_date : 'datetime'
    The starting date for the plot
    end_date : 'datetime'
    The ending date for the plot
    """
    months = mdates.MonthLocator()  # every month
    fig, ax = plt.subplots()
    ax.plot(df.index, df[ts1], label=ts1)
    ax.plot(df.index, df[ts2], label=ts2)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    ax.set_xlim(start_date, end_date)
    ax.grid(True)
    fig.autofmt_xdate()
    plt.xlabel("Month/Year")
    plt.ylabel("Price ($)")
    plt.title("%s and %s Daily Prices" % (ts1, ts2))
    plt.legend()
    plt.show()


def plot_scatter_series(df, ts1, ts2):
    """
    Plot a scatter plot of both time series for
    via the provided DataFrame.
    Parameters
    ----------
    df : 'pd.DataFrame'
    The DataFrame containing prices for each series
    ts1 : 'str'
    The first time series column name
    ts2 : 'str'
    The second time series column name
    """
    plt.xlabel("%s Price ($)" % ts1)
    plt.ylabel("%s Price ($)" % ts2)
    plt.title("%s and %s Price Scatterplot" % (ts1, ts2))
    plt.scatter(df[ts1], df[ts2])
    plt.show()


def plot_residuals(df, start_date, end_date):
    """
    Plot the residuals of OLS procedure for both
    time series.
    Parameters
    ----------
    df : 'pd.DataFrame'
    The residuals DataFrame
    start_date : 'datetime'
    The starting date of the residuals plot
    end_date : 'datetime'
    The ending date of the residuals plot
    """
    months = mdates.MonthLocator()  # every month
    fig, ax = plt.subplots()
    ax.plot(df.index, df["res"], label="Residuals", c="blue")
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.set_xlim(start_date, end_date)
    ax.grid(True)
    fig.autofmt_xdate()

    plt.xlabel("Month/Year")
    plt.ylabel("Price ($)")
    plt.title("Residual Plot")
    plt.legend()
    plt.plot(df["res"])
    plt.show()


if __name__ == "__main__":
    # Get the path to the database file relative to the current working directory
    db_path = os.path.join(os.getcwd(), "top_100_crypto.db")

    con = sqlite3.connect(db_path)

    # Download the ETH OHLCV data from 1/1/2018 to 1/1/2023
    start_date = dt(2021, 1, 1)
    end_date = dt(2023, 1, 1)

    sql_avax = f"""SELECT dp.price_date, dp.close_price
      FROM symbol AS sym
      INNER JOIN daily_price AS dp
      ON dp.symbol_id = sym.id
      WHERE sym.ticker = 'AVAX'
      AND dp.price_date BETWEEN '{start_date}' AND '{end_date}'
      ORDER BY dp.price_date ASC;"""
    # Create a pandas dataframe from the SQL query
    avax = pd.read_sql_query(sql_avax, con=con, index_col="price_date")

    sql_sol = f"""SELECT dp.price_date, dp.close_price
      FROM symbol AS sym
      INNER JOIN daily_price AS dp
      ON dp.symbol_id = sym.id
      WHERE sym.ticker = 'SOL'
      AND dp.price_date BETWEEN '{start_date}' AND '{end_date}'
      ORDER BY dp.price_date ASC;"""

    sol = pd.read_sql_query(sql_sol, con=con, index_col="price_date")

    # Place them into the Pandas DataFrame format
    df = pd.DataFrame(index=sol.index)
    df["AVAX"] = avax["close_price"]
    df["SOL"] = sol["close_price"]

    # Convert dates to str format to avoid issues when calling the functions
    start_date = str(start_date)
    end_date = str(end_date)

    # Plot the two time series
    plot_price_series(df, "AVAX", "SOL", start_date, end_date)
    # Display a scatter plot of the two time series
    plot_scatter_series(df, "AVAX", "SOL")
    # Calculate optimal hedge ratio "beta" via Statsmodels
    model = sm.OLS(df["SOL"], df["AVAX"])
    res = model.fit()
    beta_hr = res.params[0]
    # Calculate the residuals of the linear combination
    df["res"] = df["SOL"] - beta_hr * df["AVAX"]
    # Plot the residuals
    plot_residuals(df, start_date, end_date)
    # Calculate and output the CADF test on the residuals
    cadf = ts.adfuller(df["res"])
    pprint.pprint(cadf)


# The cointegration technique presumes that 2 assets in the same category will behave similarly giving the possibility of mean reversion between them. The way of calculating this is by using Cointegration ADF.
# As we can see from the result below, we cannot reject the null hypothesis of no cointegration because test statistic is lower than any of the values plus p-value is really high for these pair.

# (-1.8056819883620912,
#  0.37764441538776833,
#  16,
#  714,
#  {'1%': -3.4395418285955563,
#   '10%': -2.5689301318958955,
#   '5%': -2.865596454500293},
#  4487.129387043653)
