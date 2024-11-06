import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import glob
import os

# Initialize session state for portfolio if it doesn't exist
if "portfolio" not in st.session_state:
    st.session_state["portfolio"] = {}

# Homepage setup
st.title("Crypto Portfolio Risk Dashboard")
total_portfolio = st.number_input("Total Portfolio Value in USD", value=0)
st.write("Add assets to your portfolio")

# Dropdown to select existing assets
existing_assets = list(st.session_state["portfolio"].items())
asset_options = [f"{asset} (${value})" for asset, value in existing_assets]
selected_asset = st.selectbox("Select Existing Asset (Optional)", [""] + asset_options)

# If an asset is selected from the dropdown, fill in its details
if selected_asset:
    asset_name, asset_value = selected_asset.split(" ($")
    asset_value = float(asset_value.strip(")"))
    st.session_state["selected_asset"] = asset_name
else:
    st.session_state["selected_asset"] = ""

# Input fields for adding or editing assets
asset = st.text_input("Enter Crypto Symbol (e.g., BTC)", value=st.session_state["selected_asset"] or "")
value = st.number_input(f"Enter value of {asset} in USD", min_value=0.0, value=st.session_state["portfolio"].get(asset, 0.0))

# Buttons for adding, editing, and deleting assets
col1, col2, col3 = st.columns([1, 1, 1])

# Function to calculate the current total portfolio value
def calculate_total_portfolio_value(proposed_asset=None, proposed_value=0.0):
    current_value = sum(st.session_state["portfolio"].values())
    if proposed_asset:
        # Check if we're adding a new asset or updating an existing one
        current_value += proposed_value - st.session_state["portfolio"].get(proposed_asset, 0)
    return current_value

# Add Asset button functionality
if col1.button("Add Asset"):
    if asset and value:
        # Check if the new addition would exceed the total portfolio value
        updated_total = calculate_total_portfolio_value(proposed_asset=asset, proposed_value=value)
        if updated_total > total_portfolio:
            st.warning(f"Cannot add {asset} with value ${value}. Total exceeds allowed portfolio limit (${total_portfolio}).")
        else:
            st.session_state["portfolio"][asset] = value  # Commit the new value
            st.success(f"Added {asset} with value ${value}")
    else:
        st.warning("Please enter both a symbol and a value.")

# Edit Asset button functionality
if col2.button("Edit Asset"):
    if asset in st.session_state["portfolio"]:
        # Check if the edit would exceed the total portfolio value
        updated_total = calculate_total_portfolio_value(proposed_asset=asset, proposed_value=value)
        if updated_total > total_portfolio:
            st.warning(f"Cannot update {asset} to value ${value}. Total exceeds allowed portfolio limit (${total_portfolio}).")
        else:
            st.session_state["portfolio"][asset] = value  # Commit the edited value
            st.success(f"Updated {asset} to value ${value}")
    else:
        st.warning(f"Asset {asset} not found in portfolio. Please add it first.")

# Delete Asset button functionality
if col3.button("Delete Asset"):
    if asset in st.session_state["portfolio"]:
        del st.session_state["portfolio"][asset]
        st.success(f"Deleted {asset} from portfolio")
    else:
        st.warning(f"Asset {asset} not found in portfolio.")

# Calculate and display total portfolio summary value
total_portfolio_summary_value = sum(st.session_state["portfolio"].values())

# Display current portfolio from session state
st.write("Portfolio Summary")
st.write(st.session_state["portfolio"])

# Interactive pie chart for portfolio distribution
if st.session_state["portfolio"]:
    portfolio_df = pd.DataFrame(
        list(st.session_state["portfolio"].items()), columns=["Asset", "Value"]
    )
    fig = px.pie(portfolio_df, names="Asset", values="Value", title="Portfolio Distribution")
    st.plotly_chart(fig)

# Dropdown to choose calculation
st.write("Select a calculation to perform on the portfolio:")
calc_option = st.selectbox("Choose Metric", ["Select", "Volatility", "VaR", "Beta", "Maximum Drawdown", "30% Risk Test"])

# Function to load data for each asset
def load_data(symbol):
    filepath = f"data/{symbol}.csv"
    if os.path.exists(filepath):
        return pd.read_csv(filepath, delimiter=";", parse_dates=["timestamp"], index_col="timestamp")
    else:
        st.error(f"Data file for {symbol} not found.")
        return None

# Load data for all assets in the portfolio
portfolio_data = {}
for symbol in st.session_state["portfolio"].keys():
    data = load_data(symbol)
    if data is not None:
        portfolio_data[symbol] = data

# Volatility Calculation
if calc_option == "Volatility":
    st.subheader("Volatility")
    volatility_data = []
    for symbol, data in portfolio_data.items():
        data['Return'] = data['close'].pct_change()
        daily_volatility = data['Return'].std()
        annualized_volatility = daily_volatility * np.sqrt(365)
        volatility_data.append({"Asset": symbol, "Daily Volatility": daily_volatility, "Annualized Volatility": annualized_volatility})

    st.table(pd.DataFrame(volatility_data))

# VaR Calculation
elif calc_option == "VaR":
    st.subheader("Value at Risk (VaR)")
    z_score = 1.645  # for 95% confidence level
    var_data = []

    for symbol, data in portfolio_data.items():
        data['Return'] = data['close'].pct_change()
        daily_volatility = data['Return'].std()
        mean_return = data['Return'].mean()
        daily_var_95 = mean_return - (z_score * daily_volatility)
        daily_var_95_usd = daily_var_95 * st.session_state["portfolio"][symbol]
        var_data.append({"Asset": symbol, "Daily VaR (USD)": daily_var_95_usd})

    st.table(pd.DataFrame(var_data))

# Beta Calculation
elif calc_option == "Beta":
    st.subheader("Beta relative to Bitcoin")
    btc_data = load_data("BTC")
    if btc_data is not None:
        btc_data['Return_BTC'] = btc_data['close'].pct_change()
        beta_data = []
        for symbol, data in portfolio_data.items():
            data['Return_Asset'] = data['close'].pct_change()
            merged_data = pd.merge(data[['Return_Asset']], btc_data[['Return_BTC']], left_index=True, right_index=True)
            covariance = merged_data['Return_Asset'].cov(merged_data['Return_BTC'])
            variance_btc = merged_data['Return_BTC'].var()
            beta = covariance / variance_btc
            beta_data.append({"Asset": symbol, "Beta": beta})
        
        st.table(pd.DataFrame(beta_data))

# Maximum Drawdown Calculation
elif calc_option == "Maximum Drawdown":
    st.subheader("Maximum Drawdown")
    drawdown_data = []
    for symbol, data in portfolio_data.items():
        data['Cumulative Return'] = (1 + data['close'].pct_change()).cumprod()
        data['Running Max'] = data['Cumulative Return'].cummax()
        data['Drawdown'] = (data['Running Max'] - data['Cumulative Return']) / data['Running Max']
        max_drawdown = data['Drawdown'].max()
        drawdown_data.append({"Asset": symbol, "Max Drawdown": max_drawdown})
    
    st.table(pd.DataFrame(drawdown_data))

# 30% Risk Test Simulation
elif calc_option == "30% Risk Test":
    st.subheader("30% Risk Test Simulation")
    btc_drop_percentage = 0.3  # 30% drop for BTC
    current_values = st.session_state["portfolio"]
    returns = pd.DataFrame({symbol: data['close'].pct_change() for symbol, data in portfolio_data.items()}).dropna()
    correlation_with_btc = returns.corr().get("BTC", pd.Series())

    portfolio_impact = []
    for asset, current_value in current_values.items():
        correlation = correlation_with_btc.get(asset, 0)
        estimated_drop_percentage = correlation * btc_drop_percentage * 100
        stress_value = current_value * (1 - estimated_drop_percentage / 100)
        loss = current_value - stress_value
        portfolio_impact.append({"Asset": asset, "Current Value (USD)": current_value, "Estimated Drop (%)": estimated_drop_percentage, "Stress Value (USD)": stress_value, "Loss (USD)": loss})

    total_initial_value = sum(current_values.values())
    total_stress_value = sum([item["Stress Value (USD)"] for item in portfolio_impact])
    total_loss = total_initial_value - total_stress_value

    st.table(pd.DataFrame(portfolio_impact))
    st.write(f"Total Portfolio Value Before Stress Test: ${total_initial_value}")
    st.write(f"Total Portfolio Value After Stress Test: ${total_stress_value}")
    st.write(f"Total Loss in Portfolio: ${total_loss}")
