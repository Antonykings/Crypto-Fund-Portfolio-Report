import pandas as pd
import numpy as np

data = pd.read_csv('data/POPCAT.csv', delimiter=';', parse_dates=['timestamp'], index_col='timestamp')
# Calculate daily returns based on the 'close' price
data['Returns'] = data['close'].pct_change()

# 1st row NaN 
data.dropna(inplace=True)

# Calculate daily volatility (standard deviation of daily returns)
daily_volatility = data['Returns'].std()
print("Daily Volatility:", daily_volatility)

# Calculate Daily VaR

z_score = 1.645 # Z-score for 95% confidence level

# Mean return of daily returns
mean_return = data['Returns'].mean()

# Daily VaR at 95% confidence level (percentage)
daily_var_95 = mean_return - (z_score * daily_volatility)
print("Daily VaR at 95% Confidence Level (in % terms):", daily_var_95*100)

weekly_var_95 = daily_var_95 * np.sqrt(7)
print("Weekly VaR at 95% Confidence Level (in % terms):", weekly_var_95*100)

monthly_var_95 = daily_var_95 * np.sqrt(30)
print("Monthly VaR at 95% Confidence Level (in % terms):", monthly_var_95*100)
