import pandas as pd

data = pd.read_csv('data/Popcat.csv', delimiter=';', parse_dates=['timestamp'], index_col='timestamp')


# Calculate Cumulative Returns
data['Cumulative Return'] = (1 + data['close'].pct_change()).cumprod()

# Calculate the Running Maximum
data['Running Max'] = data['Cumulative Return'].cummax()

# Calculate Drawdown
data['Drawdown'] = (data['Running Max'] - data['Cumulative Return']) / data['Running Max']

# Find Maximum Drawdown
max_drawdown = data['Drawdown'].max()
print("Maximum Drawdown (MDD):", max_drawdown)

drawdown_period = data[data['Drawdown'] == max_drawdown]
print("Drawdown Period:")
print(drawdown_period)
