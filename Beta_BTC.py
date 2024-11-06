import pandas as pd


asset_data = pd.read_csv('data/Popcat.csv', delimiter=';', parse_dates=['timestamp'], index_col='timestamp')
btc_data = pd.read_csv('data/BTC.csv', delimiter=';', parse_dates=['timestamp'], index_col='timestamp')


# Calculate daily returns for each Asset
asset_data['Return_Asset'] = asset_data['close'].pct_change()
btc_data['Return_BTC'] = btc_data['close'].pct_change()

# 1st row NaN 
asset_data.dropna(inplace=True)
btc_data.dropna(inplace=True)

# Merge the two datasets on the 'timestamp' index
merged_data = pd.merge(asset_data[['Return_Asset']], btc_data[['Return_BTC']], left_index=True, right_index=True)

# Calculate Covariance between Asset and Bitcoin returns
covariance = merged_data['Return_Asset'].cov(merged_data['Return_BTC'])

# Calculate Variance of Bitcoin returns
variance_btc = merged_data['Return_BTC'].var()

# Calculate Beta
beta = covariance / variance_btc
print("Beta of Asset relative to Bitcoin:", beta)
