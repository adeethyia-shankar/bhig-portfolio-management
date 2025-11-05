"""
parse_pdf.py

Module for parsing the monthly PDFs received from the Brown Investment Office.

Reads a PDF file to extract portfolio and cash position statistics, and then saves to CSV.

Dependencies:
-------------
- pdfplumber

Author: Adeethyia Shankar
Date: 2025-08-17
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path

def parse_asset_detail(pdf_path: str) -> pd.DataFrame:
    """
    Parse the Northern Trust 'Asset Detail by Account' report into a DataFrame.

    Args:
        pdf_path (str): Path to the Asset Detail PDF.

    Returns:
        pd.DataFrame: Parsed table with columns:
            ['Description', 'CUSIP', 'Shares', 'Price', 'Market Value', 'Cost', 'Unrealized Gain/Loss']
    """
    rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            lines = text.split("\n")
            for line in lines:
                # Match lines with stock details: SYMBOL + description + shares + price + market value etc.
                if re.search(r"\sCUSIP\s*:\s*[A-Z0-9]+", line):
                    # Example: ABBOTT LAB COM   CUSIP : 002824100
                    desc_match = re.match(r"(.+?)\s+CUSIP\s*:\s*([A-Z0-9]+)", line)
                    if desc_match:
                        description = desc_match.group(1).strip()
                        cusip = desc_match.group(2).strip()
                        continue
                else:
                    # Try to extract numeric row: e.g. "33.000 133.58 0.00 4,408.14 3,112.50 1,295.64"
                    nums = re.findall(r"-?\d+\.\d+", line.replace(",", ""))
                    if len(nums) >= 5:
                        shares = float(nums[0])
                        price = float(nums[1])
                        market_val = float(nums[3])
                        cost = float(nums[4])
                        unrealized = float(nums[5])
                        rows.append([description, cusip, shares, price, market_val, cost, unrealized])
    return pd.DataFrame(rows, columns=["Description", "CUSIP", "Shares", "Price", "Market Value", "Cost", "Unrealized G/L"])

# TODO: doesn't work
def parse_cash_activity(pdf_path: str) -> pd.DataFrame:
    """
    TODO: DOESN'T WORK
    Parse the Northern Trust 'Cash Activity Detail by Account' report into a structured DataFrame.

    Args:
        pdf_path (str): Path to the Cash Activity PDF.

    Returns:
        pd.DataFrame: DataFrame with clean transaction rows containing:
            ['Entry Date', 'Transaction Narrative/Security Description',
             'Local Receipt/Disbursement', 'USD Balance',
             'Base Receipt/Disbursement', 'Balance']
    """
    all_rows = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract tables from each page
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    all_rows.append(row)

    # Build DataFrame with expected headers
    df = pd.DataFrame(all_rows, columns=[
        "Entry Date",
        "Transaction Narrative/Security Description",
        "Local Receipt/Disbursement",
        "USD Balance",
        "Base Receipt/Disbursement",
        "Balance"
    ])

    # Clean up: drop completely empty rows
    df = df.dropna(how="all")

    # Strip whitespace and normalize
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    return df


def export_to_csv(df: pd.DataFrame, output_path: str):
    """
    Export a DataFrame to CSV.

    Args:
        df (pd.DataFrame): Data to export.
        output_path (str): Path for the CSV file.
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    # Example usage
    asset_df = parse_asset_detail("../../data/brown_investment_office_pdfs/5-2025 Stu Bio Tech NT Asset_Detail_by_Account.pdf")
    cash_df = parse_cash_activity("../../data/brown_investment_office_pdfs/5-2025 Stu Bio Tech NT Cash Activity Detail.pdf")

    export_to_csv(asset_df, "../../data/parsed_csvs/assets.csv")
    export_to_csv(cash_df, "../../data/parsed_csvs/cash_activity.csv")

    print("Parsing complete. Data exported to parsed_csvs/")
