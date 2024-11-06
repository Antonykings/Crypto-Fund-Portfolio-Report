import pandas as pd
import numpy as np

data = pd.read_csv('data/Popcat.csv', delimiter=';', parse_dates=['timestamp'], index_col='timestamp')
# Calculate daily returns based on the 'close' price
data['Returns'] = data['close'].pct_change()

# 1st row NaN 
data.dropna(inplace=True)

# Calculate daily volatility (standard deviation of daily returns)
daily_volatility = data['Returns'].std()
print("Daily Volatility:", daily_volatility)

# Annualize daily volatility
annualized_volatility = daily_volatility * np.sqrt(365)
print("Annualized Volatility:", annualized_volatility)


