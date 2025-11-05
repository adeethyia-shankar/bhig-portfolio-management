# backtester/loaders/fetch_yfinance.py
# =============== BOILERPLATE START ======================

# Basic boilerplate: download sample stock data from Yahoo Finance.
# Provides raw CSV data for the DataLoader to clean next week.

import yfinance as yf
import pandas as pd
from pathlib import Path

# Example tickers (large, liquid names for testing)
tickers = ["AAPL", "MSFT", "META", "BLK", "SHOP", "PYPL"]


# eate data directory if it doesn't exist
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

print("📥 Downloading daily price data from Yahoo Finance...")
data = yf.download(tickers, start="2024-11-03", end="2025-11-03", group_by="ticker")

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
#print(raw_df.head(100))


# =============== BOILERPLATE END ======================

# ==========================================================
# TODO: Implement DataLoader
# ----------------------------------------------------------
# Goal: Take the raw_prices.csv file and output a clean,
# (date, ticker)-indexed DataFrame ready for merging later.
# Steps (for next task):
# 1. Load data/raw_prices.csv into a DataFrame, alter boilerplate to keep the last year of data for each stock
#    read data/raw_prices.csv into dataframe and keep last 365 days per ticker
# 2. Ensure 'date' is YYYY-MM-DD and sort chronologically in reverse order.
#    parse date to yyyy-mm-dd and sort descending by date
#
# 3. Standardize 'ticker' column (uppercase, no spaces).
#    uppercase tickers and strip whitespace
# 4. Remove duplicate (date, ticker) rows.
#    drop duplicate date,ticker rows keeping last occurrence
# 5. Set (date, ticker) as a MultiIndex.
#    set a multiindex on (date, ticker)
# 6. Keep missing values as NaN (forward-fill only if needed).
#    leave missing values as nan; no forward-fill by default
# 7. Ensure numeric columns are proper floats.
#    convert close and volume to floats
# 8. Save clean output as data/clean_prices.csv.
#    write cleaned dataframe to data/clean_prices.csv
# 9. Plot price history for each ticker after cleaning.
#    save a simple line plot per ticker in data/plots
# 10. Check for missing dates or gaps per ticker.
#    detect missing business-day dates per ticker and report
# 11. Compute simple daily returns for one stock of your choice, say AAPL: close.pct_change().
#    compute aapl daily returns and save to csv
# 12. EXTRA: daily returns for apple visualize
#    create histogram and time series plot of aapl daily returns


# implementation of steps 1..12
# 1. read data/raw_prices.csv into dataframe and keep last 365 days per ticker
raw_path = data_dir / "raw_prices.csv"
if raw_path.exists(): # load from csv
    df = pd.read_csv(raw_path)
else:
    try:
        df = raw_df.copy()
    except NameError:
        raise FileNotFoundError(f"{raw_path} not found and no raw_df available")

# 2. parse date to yyyy-mm-dd and sort descending by date
#    parse to datetime, normalize to day, sort desc so index 0 is most recent day
df["date"] = pd.to_datetime(df.get("date"), errors="coerce")
df = df.dropna(subset=["date"]).copy()
df["date"] = df["date"].dt.normalize()
df = df.sort_values("date", ascending=False).copy()
print(df.head(100))

# 3. uppercase tickers and strip whitespace
df["ticker"] = df["ticker"].astype(str).str.upper().str.strip()

# 4. drop duplicate (date, ticker) keeping last occurrence
df = df.drop_duplicates(subset=["date", "ticker"], keep="last").copy()

# 5. set a multiindex on (date, ticker)
df = df.set_index(["date", "ticker"]).sort_index(level=0, ascending=False)

# 6. leave missing values as nan (no forward-fill by default)
#    (intentionally no ffill)

# 7. convert numeric columns to floats
for col in ["close", "volume"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype(float)

# 8. save cleaned dataframe to data/clean_prices.csv
clean_path = data_dir / "clean_prices.csv"
df_reset = df.reset_index()
# ensure date column is datetime then sort so each ticker block has newest date first
df_reset["date"] = pd.to_datetime(df_reset["date"], errors="coerce")
# sort by ticker asc then date desc so within each ticker the first row is the latest date
df_reset = df_reset.sort_values(["ticker", "date"], ascending=[True, False]).reset_index(drop=True)
# show top rows for aapl to confirm descending orders
print("aapl cleaned head:\n", df_reset[df_reset["ticker"] == "AAPL"].head(5))
df_reset["date"] = df_reset["date"].dt.strftime("%Y-%m-%d")
df_reset.to_csv(clean_path, index=False)
print(f"✅ cleaned data saved to {clean_path}")

# 9. plot price history for each ticker after cleaning
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    plots_dir = data_dir / "plots"
    plots_dir.mkdir(exist_ok=True)

    for ticker in df_reset["ticker"].unique():
        sub = df_reset[df_reset["ticker"] == ticker].sort_values("date")
        if "close" not in sub.columns or sub["close"].dropna().empty:
            # skip if not in sub or no close data
            continue
        plt.figure(figsize=(8, 3))
        plt.plot(pd.to_datetime(sub["date"]), sub["close"], lw=1)
        plt.title(f"{ticker} close")
        plt.xlabel("date")
        plt.ylabel("close")
        plt.tight_layout()
        out = plots_dir / f"{ticker}_close.png"
        plt.savefig(out)
        plt.close()
    print(f"✅ saved price plots to {plots_dir}")
except Exception as e:
    print(f"⚠️ plotting skipped: {e}")

# 10. detect missing business-day dates per ticker and report gaps
gaps = []
for ticker in df_reset["ticker"].unique():
    sub = pd.to_datetime(df_reset.loc[df_reset["ticker"] == ticker, "date"]).dropna().sort_values()
    # sub is the datetimes with na data dropped
    if sub.empty:
        continue
    full = pd.date_range(start=sub.min(), end=sub.max(), freq="B")
    missing = full.difference(sub) # missing is the dates in full but not in sub
    
    if not missing.empty: # iterate through non-empty missing, display them
        print(f"\n{ticker} missing business days ({len(missing)} total):")
        for missing_date in sorted(missing):
            gaps.append({
                "ticker": ticker, 
                "missing_date": missing_date.strftime('%Y-%m-%d'),
            })
            
gaps_df = pd.DataFrame(gaps) # dataframe with the gaps 
gaps_path = data_dir / "gaps_report.csv"
if not gaps_df.empty:
    gaps_df.to_csv(gaps_path, index=False)
    print(f"\n⚠️ gaps detected; report saved to {gaps_path}")
else:
    print("✅ no gaps detected (business days) for available tickers")


# 11. compute daily returns for aapl via close.pct_change()
#    compute aapl daily returns and save to csv
try:
    aapl = df_reset[df_reset["ticker"] == "AAPL"].copy()
    # compute returns on ascending dates (oldest -> newest)
    aapl = aapl.sort_values("date", ascending=True)
    if "close" in aapl.columns and not aapl["close"].dropna().empty:
        # iterate over rows that are not na
        aapl_returns = aapl.set_index(pd.to_datetime(aapl["date"]))["close"].pct_change()
        # compute returns on ascending dates (oldest -> newest)
        aapl_out = data_dir / "aapl_returns.csv"
        # save to csv
        aapl_returns.rename("returns").to_csv(aapl_out, header=True)
        print(f"✅ aapl returns saved to {aapl_out}")
    else:
        print("⚠️ aapl close data not available to compute returns")
except Exception as e:
    print(f"⚠️ computing aapl returns failed: {e}")

# 12. EXTRA: daily returns for apple visualize
#    create histogram and time series plot of aapl daily returns
try:
    import matplotlib.pyplot as plt
    
    if 'aapl_returns' in locals() and not aapl_returns.dropna().empty:
        # create subplots for returns visualization
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # plot 1: time series of daily returns
        returns_clean = aapl_returns.dropna()
        ax1.plot(returns_clean.index, returns_clean.values, lw=0.8, alpha=0.7)
        ax1.axhline(y=0, color='red', linestyle='--', alpha=0.5)
        ax1.set_title("AAPL Daily Returns Over Time")
        ax1.set_xlabel("Date")
        ax1.set_ylabel("Daily Return")
        ax1.grid(True, alpha=0.3)
        
        # plot 2: histogram of daily returns
        ax2.hist(returns_clean.values, bins=50, alpha=0.7, color='blue', edgecolor='black')
        ax2.axvline(x=returns_clean.mean(), color='red', linestyle='--', label=f'Mean: {returns_clean.mean():.4f}')
        ax2.set_title("AAPL Daily Returns Distribution")
        ax2.set_xlabel("Daily Return")
        ax2.set_ylabel("Frequency")
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        returns_plot_path = data_dir / "aapl_returns_visualization.png"
        plt.savefig(returns_plot_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"✅ aapl returns visualization saved to {returns_plot_path}")
        print(f"   returns stats: mean={returns_clean.mean():.4f}, std={returns_clean.std():.4f}")
    else:
        print("⚠️ no aapl returns data available for visualization")
        
except Exception as e:
    print(f"⚠️ aapl returns visualization failed: {e}")
# ==========================================================