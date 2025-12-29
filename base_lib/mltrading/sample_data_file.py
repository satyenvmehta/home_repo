import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set the start and end dates
start_date = datetime(2020, 1, 1)
end_date = datetime(2021, 12, 31)

# Generate a range of dates
dates = pd.date_range(start_date, end_date, freq='B')  # 'B' frequency is for business days

# Generate random stock prices and volumes
np.random.seed(0)
data = {
    'Date': dates,
    'Open': np.random.uniform(100, 200, len(dates)),
    'High': np.random.uniform(100, 200, len(dates)),
    'Low': np.random.uniform(100, 200, len(dates)),
    'Close': np.random.uniform(100, 200, len(dates)),
    'Volume': np.random.randint(1000, 10000, len(dates))
}

# Create a DataFrame
df = pd.DataFrame(data)

# Ensure High is always greater than Low, and Open/Close are within this range
df['High'] = df[['Open', 'Close']].max(axis=1) + np.random.uniform(0, 10, len(dates))
df['Low'] = df[['Open', 'Close']].min(axis=1) - np.random.uniform(0, 10, len(dates))

# Date,Open,High,Low,Close,Volume
# 2020-01-01,154.8813503927325,161.0287153580987,134.13677152197292,143.51419865163297,4340

# Save to CSV
df.to_csv('historical_stock_prices_1.csv', index=False)

print("Sample historical_stock_prices_1.csv file created successfully.")
