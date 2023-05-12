from datetime import datetime as dt, timedelta as td

# from dotenv import load_dotenv

import os
import numpy as np
import pandas as pd
import sqlite3
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.discriminant_analysis import (
    LinearDiscriminantAnalysis as LDA,
    QuadraticDiscriminantAnalysis as QDA,
)
from sklearn.metrics import confusion_matrix
from sklearn.svm import LinearSVC, SVC

# from alpha_vantage.timeseries import TimeSeries


# from openbb_terminal.sdk import openbb as obb

# av_key = os.environ.get("ALPHA_VANTAGE_KEY")


def create_lagged_series(symbol, start_date, end_date, lags=5):
    """
    This creates a Pandas DataFrame that stores the
    percentage returns of the adjusted closing value of
    a stock obtained from AlphaVantage, along with a
    number of lagged returns from the prior trading days
    (lags defaults to 5 days). Trading volume, as well as
    the Direction from the previous day, are also included.
    Parameters
    ----------
    av : 'AlphaVantage'
    The AlphaVantage API instance used to obtain pricing
    symbol : 'str'
    The ticker symbol to obtain from AlphaVantage
    start_date : 'datetime'
    The starting date of the series to obtain
    end_date : 'datetime'
    The ending date of the the series to obtain
    lags : 'int', optional
    The number of days to 'lag' the series by
    Returns
    -------
    'pd.DataFrame'
    Contains the Adjusted Closing Price returns and lags
    """
    adj_start_date = start_date - td(days=365)
    # Obtain stock pricing from AlphaVantage
    sql = f"""SELECT dp.price_date, dp.adj_close_price, dp.volume
      FROM symbol AS sym
      INNER JOIN daily_price AS dp
      ON dp.symbol_id = sym.id
      WHERE sym.ticker = '{symbol}'
      AND dp.price_date BETWEEN '{adj_start_date}' AND '{end_date}'
      ORDER BY dp.price_date ASC;"""
    # Create a pandas dataframe from the SQL query
    ts = pd.read_sql_query(sql, con=con, index_col="price_date")

    # Create the new lagged DataFrame
    tslag = pd.DataFrame(index=ts.index)
    tslag["Today"] = ts["adj_close_price"]
    tslag["Volume"] = ts["volume"]
    # Create the shifted lag series of prior trading period close values
    for i in range(0, lags):
        tslag["Lag%s" % str(i + 1)] = ts["adj_close_price"].shift(i + 1)
    # Create the returns DataFrame
    tsret = pd.DataFrame(index=tslag.index)
    tsret["Volume"] = tslag["Volume"]
    tsret["Today"] = tslag["Today"].pct_change() * 100.0
    # If any of the values of percentage returns equal zero, set them to
    # a small number (stops issues with QDA model in scikit-learn)
    tsret.loc[tsret["Today"].abs() < 0.0001, ["Today"]] = 0.0001
    # Create the lagged percentage returns columns
    for i in range(0, lags):
        tsret["Lag%s" % str(i + 1)] = tslag["Lag%s" % str(i + 1)].pct_change() * 100.0
    # Create the "Direction" column (+1 or -1) indicating an up/down day
    tsret["Direction"] = np.sign(tsret["Today"])
    tsret = tsret[pd.to_datetime(tsret.index) >= pd.to_datetime(start_date)]

    return tsret


if __name__ == "__main__":
    # Get the path to the database file relative to the current working directory
    db_path = os.path.join(os.getcwd(), "top_100_crypto.db")

    con = sqlite3.connect(db_path)

    # Download the S&P500 ETF time series
    start_date = dt(2016, 1, 10)
    end_date = dt(2017, 12, 31)

    # Create a lagged series of the S&P500 US stock market index ETF
    snpret = create_lagged_series("BTC", start_date, end_date)

    # Use the prior two days of returns as predictor
    # values, with direction as the response
    X = snpret[["Lag1", "Lag2"]]
    y = snpret["Direction"]
    # The test data is split into two parts: Before and after 1st Jan 2017.
    start_test = dt(2017, 1, 1)
    # Create training and test sets
    X_train = X[pd.to_datetime(X.index) < start_test]
    X_test = X[pd.to_datetime(X.index) >= start_test]
    y_train = y[pd.to_datetime(y.index) < start_test]
    y_test = y[pd.to_datetime(y.index) >= start_test]
    # Create the (parametrised) models
    print("Hit Rates/Confusion Matrices:\n")
    models = [
        ("LR", LogisticRegression(solver="liblinear")),
        ("LDA", LDA(solver="svd")),
        ("QDA", QDA()),
        ("LSVC", LinearSVC(max_iter=10000)),
        (
            "RSVM",
            SVC(
                C=1000000.0,
                cache_size=200,
                class_weight=None,
                coef0=0.0,
                degree=3,
                gamma=0.0001,
                kernel="rbf",
                max_iter=-1,
                probability=False,
                random_state=None,
                shrinking=True,
                tol=0.001,
                verbose=False,
            ),
        ),
        (
            "RF",
            RandomForestClassifier(
                n_estimators=1000,
                criterion="gini",
                max_depth=None,
                min_samples_split=2,
                min_samples_leaf=1,
                max_features="sqrt",
                bootstrap=True,
                oob_score=False,
                n_jobs=1,
                random_state=None,
                verbose=0,
            ),
        ),
    ]
    # Iterate through the models
    for m in models:
        # Train each of the models on the training set
        m[1].fit(X_train, y_train)
        # Make an array of predictions on the test set
        pred = m[1].predict(X_test)
        # Output the hit-rate and the confusion matrix for each model
        print("%s:\n%0.3f" % (m[0], m[1].score(X_test, y_test)))
        print("%s\n" % confusion_matrix(pred, y_test))
