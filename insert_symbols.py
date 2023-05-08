import datetime
from math import ceil
import sqlite3
import requests
from openbb_terminal.sdk import openbb
import pandas as pd


def top_100_crypto():
    """
    Get a list of 100 cryptos by market cap
    using requests and openbb sdk.
    Returns a pandas df to add to SQLite.
    """
    # Stores the current time, for the created_at record
    now = datetime.datetime.utcnow()

    # Get the list of the 100 cryptos by market cap
    symbolslist = openbb.crypto.ov.coin_list()[:100]

    symbolslist = symbolslist.drop(["id", "rank", "type"], axis=1)

    return symbolslist


def insert_symbols(symbols):
    """
    Insert the crypto symbols into the SQLite database.
    """
    # Connect to the SQLite instance
    con = sqlite3.connect("tick_btcusdt.db")
    cur = con.cursor()
    res = cur.execute("SELECT name FROM sqlite_master")
    # Create the insert strings
    column_str = (
        "name, instrument, ticker, sector, " "currency, created_date, last_updated_date"
    )
    insert_str = ("%s, " * 7)[:-2]
    final_str = "INSERT INTO symbol (%s) VALUES (%s)" % (column_str, insert_str)
    # Using the MySQL connection, carry out
    # an INSERT INTO for every symbol
    cur = con.cursor()
    cur.executemany(final_str, symbols)
    con.commit()


if __name__ == "__main__":
    # print(openbb.crypto.ov.coin_list()[:100])
    symbols = top_100_crypto()
    print(symbols)
    # insert_snp500_symbols(symbols)
    # print("%s symbols were successfully added." % len(symbols))
