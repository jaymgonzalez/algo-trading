import pandas as pd
import sqlite3

if __name__ == "__main__":
    con = sqlite3.connect("top_100_crypto.db")

    # Select all of the historic BTC adjusted close data
    sql = """SELECT dp.price_date, dp.adj_close_price
      FROM symbol AS sym
      INNER JOIN daily_price AS dp
      ON dp.symbol_id = sym.id
      WHERE sym.ticker = 'BTC'
      ORDER BY dp.price_date ASC;"""
    # Create a pandas dataframe from the SQL query
    goog = pd.read_sql_query(sql, con=con, index_col="price_date")
    # Output the dataframe tail
    print(goog.tail())
