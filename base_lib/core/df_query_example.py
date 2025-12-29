import pandas as pd
from datetime import datetime, timedelta

# Sample data: Replace this with your actual data loading process
data = {
    'symbol': ['AAPL', 'AAPL', 'GOOGL', 'GOOGL', 'MSFT', 'MSFT', 'TSLA', 'TSLA'],
    'date': ['2023-01-01', '2023-06-01', '2023-01-01', '2022-11-01', '2023-01-01', '2022-10-01', '2023-01-01', '2022-08-01'],
}

# Convert to DataFrame
df = pd.DataFrame(data)
df['date'] = pd.to_datetime(df['date'])

# Define the date range (last six months from today)
end_date = datetime.now()
start_date = end_date - timedelta(days=180)

# Filter data within the last six months
recent_trades = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# Identify all symbols
all_symbols = df['symbol'].unique()

# Identify active symbols
active_symbols = recent_trades['symbol'].unique()

# Identify idle symbols
idle_symbols = list(set(all_symbols) - set(active_symbols))

print("Idle symbols:", idle_symbols)
