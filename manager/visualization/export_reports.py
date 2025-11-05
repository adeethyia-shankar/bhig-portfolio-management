"""
export_reports.py

Provides utilities to generate PDF or HTML reports summarizing monthly portfolio performance.

Author: Adeethyia Shankar
Date: 2025-06-18
"""

import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import os


def generate_pdf_report(figures: list[plt.Figure], filepath: str = "report.pdf"):
    """
    Save a series of matplotlib figures into a single PDF report.

    Parameters
    ----------
    figures : list of plt.Figure
        List of matplotlib figure objects to include in the report.
    filepath : str
        Path to save the PDF file.
    """
    with PdfPages(filepath) as pdf:
        for fig in figures:
            pdf.savefig(fig)
            plt.close(fig)
    print(f"PDF report generated at {filepath}")


def generate_html_report(summary_table: pd.DataFrame, filepath: str = "report.html"):
    """
    Save a summary performance table as an HTML report.

    Parameters
    ----------
    summary_table : pd.DataFrame
        Table containing performance summary.
    filepath : str
        Path to save the HTML file.
    """
    summary_table.to_html(filepath)
    print(f"HTML report saved to {filepath}")