from datetime import datetime as dt
import sqlite3
from openbb_terminal.sdk import openbb


TICKER_COUNT = 100  # Change this to 100 to download all tickers

# Obtain a database connection to the SQLite instance
con = sqlite3.connect("top_100_crypto.db")


def obtain_list_of_db_tickers():
    """
    Obtains a list of the ticker symbols in the database.
    """
    cur = con.cursor()
    cur.execute("SELECT id, ticker FROM symbol")
    con.commit()
    data = cur.fetchall()

    return [(d[0], d[1]) for d in data]


def get_daily_historic_data(ticker):
    """
    Use the generated call to query OpenBB
    and return a df of price data
    for a particular ticker.
    """

    try:
        data = openbb.crypto.load(ticker, "2015-01-01")
    except Exception as e:
        print("Could not download data for %s ticker " "(%s)...skipping." % (ticker, e))
        return []
    else:
        return data


def insert_daily_data_into_db(data_vendor_id, symbol_id, daily_data):
    """
    Takes a df of daily data and adds it to the
    SQLite database. Appends the vendor ID and symbol ID to the data.
    """
    now = dt.utcnow()

    for data in daily_data.itertuples():
        print(data)
        # Amend the data to include the vendor ID and symbol ID
        con.execute(
            "INSERT INTO daily_price (data_vendor_id, symbol_id, price_date, created_date, last_updated_date, open_price, high_price, low_price, close_price, adj_close_price, volume) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                data_vendor_id,
                symbol_id,
                data.Index.to_pydatetime(),
                now,
                now,
                data.Open,
                data.High,
                data.Low,
                data.Close,
                data._5,  # adj close
                data.Volume,
            ),
        )

    con.commit()


if __name__ == "__main__":
    # Get tickers from DB
    tickers = obtain_list_of_db_tickers()[:TICKER_COUNT]

    # Loop over the tickers and insert the daily historical
    # data into the database
    lentickers = len(tickers)
    for i, t in enumerate(tickers):
        print("Adding data for %s: %s out of %s" % (t[1], i + 1, lentickers))
        data = get_daily_historic_data(t[1])
        insert_daily_data_into_db("1", t[0], data)
    print("Successfully added pricing data to DB.")
    con.close()
