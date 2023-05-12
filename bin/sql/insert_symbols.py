import datetime
import sqlite3
from openbb_terminal.sdk import openbb


def top_100_crypto():
    """
    Get a list of 100 cryptos by market cap
    using requests and openbb sdk.
    Returns a pandas df to add to SQLite.
    """

    # Get the list of the 100 cryptos by market cap
    symbolslist = openbb.crypto.ov.coin_list()[:100]

    symbolslist = symbolslist.drop(["id", "rank", "type"], axis=1)

    return symbolslist


def insert_symbols(symbols):
    """
    Insert the crypto symbols into the SQLite database.
    """

    # Stores the current time, for the created_at record
    now = datetime.datetime.utcnow()

    # Connect to the SQLite instance
    con = sqlite3.connect("top_100_crypto.db")

    # Loop through the DataFrame and insert each row into the symbol table
    for i, row in symbols.iterrows():
        name = row["name"]
        ticker = row["symbol"]
        con.execute(
            "INSERT INTO symbol (name, ticker, sector, currency, instrument,created_date, last_updated_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (name, ticker, "crypto", "USD", "spot", now, now),
        )

    con.commit()
    con.close()


if __name__ == "__main__":
    symbols = top_100_crypto()
    insert_symbols(symbols)
    print("%s symbols were successfully added." % len(symbols))
