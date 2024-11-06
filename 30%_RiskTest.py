import pandas as pd
import glob  
import os

# Ensure that each file is named as 'BTC.csv', 'ETH.csv' 
file_path = 'data/*.csv'
all_files = glob.glob(file_path)

# Initialize an empty dictionar
data_dict = {}

for file in all_files:
    asset_name = os.path.basename(file).split('.')[0]  # Use file name as asset name
    df = pd.read_csv(file, delimiter=';', parse_dates=['timestamp'], index_col='timestamp')
    data_dict[asset_name] = df['close']  # Store closing price only

# Combine all assets into a single DataFrame on the timestamp
combined_data = pd.DataFrame(data_dict)

# Calculate Daily Returns
returns = combined_data.pct_change().dropna()  # Daily returns for each asset
print("Daily Returns:\n", returns.head())

# Calculate Correlation with Bitcoin
correlation_with_btc = returns.corr()['BTC']  # Correlation of each asset with BTC
print("Correlation with Bitcoin:\n", correlation_with_btc)

# Define BTC Stress Scenario and Calculate Impact
btc_drop_percentage = 0.3  # 30% drop for BTC

# Calculate the estimated drop for each asset based on correlation
portfolio_impact = pd.DataFrame({
    'Asset': correlation_with_btc.index,
    'Correlation with BTC': correlation_with_btc,
    'Estimated Drop (%)': correlation_with_btc * btc_drop_percentage * 100  
})

current_values = {
    'BTC': 250000,
    'ETH': 250000,
    'INJ': 150000,
    'SOL': 150000,
    'JUP': 50000,
    'POPCAT':16666,
    'BONK':16666,
    'DOGE':16666,
    'USDC': 100000,  # Stablecoin unaffected
    # Add remaining assets 
}

# Map the current values to the portfolio impact DataFrame
portfolio_impact['Current Value (USD)'] = portfolio_impact['Asset'].map(current_values)

# Calculate post-stress value and loss for each asset
portfolio_impact.loc[portfolio_impact['Asset'] == 'USDC', 'Estimated Drop (%)'] = 0 # No drop for USDC
portfolio_impact['Stress Value (USD)'] = portfolio_impact['Current Value (USD)'] * (1 - portfolio_impact['Estimated Drop (%)'] / 100)
portfolio_impact['Loss (USD)'] = portfolio_impact['Current Value (USD)'] - portfolio_impact['Stress Value (USD)']

# Calculate total portfolio values
total_initial_value = sum(current_values.values())
total_stress_value = portfolio_impact['Stress Value (USD)'].sum()
total_loss = total_initial_value - total_stress_value


print("\nPortfolio Impact under Stress Scenario:")
print(portfolio_impact[['Asset', 'Current Value (USD)', 'Estimated Drop (%)', 'Stress Value (USD)', 'Loss (USD)']])
print("\nTotal Portfolio Value Before Stress Test:", total_initial_value)
print("Total Portfolio Value After Stress Test:", total_stress_value)
print("Total Loss in Portfolio:", total_loss)
