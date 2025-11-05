# backtester/loaders/fetch_yfinance.py
# =============== BOILERPLATE START ======================

# Basic boilerplate: download sample stock data from Yahoo Finance.
# Provides raw CSV data for the DataLoader to clean next week.

import yfinance as yf
import pandas as pd
from pathlib import Path

# Example tickers (large, liquid names for testing)
tickers = ["AAPL", "MSFT", "GOOG", "AMZN", "META"]

# Create data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

print("📥 Downloading daily price data from Yahoo Finance...")
data = yf.download(tickers, start="2024-12-30", end="2025-01-01", group_by="ticker")

# Flatten structure into a single tidy DataFrame
frames = []
for t in tickers:
    df = data[t].reset_index()
    df.columns = [c.lower().strip() for c in df.columns]

    # rename adj close -> close if available
    if "adj close" in df.columns:
        df = df.rename(columns={"adj close": "close"})

    df["ticker"] = t
    frames.append(df[["date", "ticker", "close", "volume"]])

# Combine all tickers into one DataFrame
raw_df = pd.concat(frames, ignore_index=True)

# Save output CSV
output_path = data_dir / "raw_prices.csv"
raw_df.to_csv(output_path, index=False)

print(f"✅ Saved raw Yahoo Finance data to {output_path}")
print(raw_df.head(100))


# =============== BOILERPLATE END ======================



# ==========================================================
# TODO: Implement DataLoader
# ----------------------------------------------------------
# Goal: Take the raw_prices.csv file and output a clean,
# (date, ticker)-indexed DataFrame ready for merging later.
#
# Steps (for next task):
# 1. Load data/raw_prices.csv into a DataFrame, alter boilerplate to keep the last year of data for each stock
# 2. Ensure 'date' is YYYY-MM-DD and sort chronologically in reverse order.
# 3. Standardize 'ticker' column (uppercase, no spaces).
# 4. Remove duplicate (date, ticker) rows.
# 5. Set (date, ticker) as a MultiIndex.
# 6. Keep missing values as NaN (forward-fill only if needed).
# 7. Ensure numeric columns are proper floats.
# 8. Save clean output as data/clean_prices.csv.
# 9. Plot price history for each ticker after cleaning.
# 10. Check for missing dates or gaps per ticker.
# 11. Compute simple daily returns for one stock of your choice, say AAPL: close.pct_change().
# ==========================================================