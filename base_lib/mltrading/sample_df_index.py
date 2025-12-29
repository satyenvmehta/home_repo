import pandas as pd
import numpy as np

# Sample DataFrame for demonstration
data = {
    'Value': [10, 20, 30, 40, 50],
    'Date': ['2024-05-23 00:00:00-04:00', '2024-05-24 00:00:00-04:00', None, '2024-05-26 00:00:00-04:00', '2024-05-27 00:00:00-04:00']
}

df = pd.DataFrame(data)
df.set_index('Date', inplace=True)

# Convert the index to DateTime, coercing errors to NaT (Not a Time)
df.index = pd.to_datetime(df.index, errors='coerce')

# Remove rows where the index is NaT (which means there was an invalid or missing date)
df = df[~df.index.isna()]

# Convert the DateTime index to date format
df.index = df.index.date

# If you want to convert the index to strings in the YYYY-MM-DD format
# df.index = df.index.strftime('%Y-%m-%d')

print(df)
