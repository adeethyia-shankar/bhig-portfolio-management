"""
interactive_tools.py

Provides an interactive dashboard using Streamlit for visualizing
portfolio analytics in a GUI format.

Author: Adeethyia Shankar
Date: 2025-06-18
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def launch_dashboard(data: pd.DataFrame):
    """
    Launch a Streamlit dashboard for exploring portfolio performance.

    Parameters
    ----------
    data : pd.DataFrame
        Portfolio time series data.
    """
    st.title("BHIG Portfolio Dashboard")

    st.sidebar.header("Dashboard Controls")
    columns = st.sidebar.multiselect("Select metrics to display", data.columns.tolist(), default=data.columns.tolist())

    st.line_chart(data[columns])

    if "returns" in data.columns:
        st.subheader("Cumulative Return")
        cumulative_return = (1 + data["returns"]).cumprod()
        st.line_chart(cumulative_return)

    st.write("Data Preview:")
    st.dataframe(data.tail())