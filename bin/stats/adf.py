from datetime import datetime as dt
import pprint
import statsmodels.tsa.stattools as ts
import sqlite3
import pandas as pd
import os


# Obtain a database connection to the SQLite instance

# Get the path to the database file relative to the current working directory
db_path = os.path.join(os.getcwd(), "top_100_crypto.db")

con = sqlite3.connect(db_path)


if __name__ == "__main__":
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
    # Output the results of the Augmented Dickey-Fuller test for Amazon
    # with a lag order value of 1
    pprint.pprint(ts.adfuller(eth["adj_close_price"].tolist(), 1))

# This can be used to check mean reversion strategies. If price series possesses mean reversion then the next price level will be proportional to the current price level.
#
#
# Since the calculated value for the T-Statistic is greater than any of the critical values a 1, 5 and 10 % the null hypothesis cannot be rejected and it's unlikely mean-reverting.
#
# (-1.3414883066676289, T-Statistic
#  0.6099842221600674, p-value
#  1,
#  1825,
#  {'1%': -3.4339382310452033,
#   '10%': -2.56761380228936,
#   '5%': -2.863125003847544},
#  21162.411536790685)
