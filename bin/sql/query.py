from datetime import datetime as dt
import pandas as pd
import sqlite3
import os


def get_daily_data(symbol, start_date, end_date, db, columns):
    db_path = os.path.join(os.getcwd(), db)

    con = sqlite3.connect(db_path)

    # Add 'dp.' prefix to each column name
    prefixed_columns = [f"dp.{column}" for column in columns]

    # Convert the list of prefixed columns to a comma-separated string
    column_names = ", ".join(prefixed_columns)

    sql = f"""SELECT dp.price_date, {column_names}
        FROM symbol AS sym
        INNER JOIN daily_price AS dp
        ON dp.symbol_id = sym.id
        WHERE sym.ticker = '{symbol}'
        AND dp.price_date BETWEEN '{start_date}' AND '{end_date}'
        ORDER BY dp.price_date ASC;"""
    # Create a pandas dataframe from the SQL query
    symbol_data = pd.read_sql_query(sql, con=con, index_col="price_date")

    con.close()

    return symbol_data


print(
    get_daily_data(
        "ETH",
        dt(2018, 1, 1),
        dt(2023, 1, 1),
        "top_100_crypto.db",
        ["adj_close_price", "volume"],
    )
)
