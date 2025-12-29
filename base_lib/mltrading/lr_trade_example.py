import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Load the dataset
data = pd.read_csv('historical_stock_prices.csv')

# Ensure the data is sorted by date
data['Date'] = pd.to_datetime(data['Date'])
data.sort_values('Date', inplace=True)

# Shift the 'Close' column to get the next day's closing price
data['Next_Close'] = data['Close'].shift(-1)

# Drop the last row as it will have NaN value for 'Next_Close'
data.dropna(inplace=True)

# Selecting relevant features
features = data[['Open', 'High', 'Low', 'Volume']]
target = data['Next_Close']

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test, dates_train, dates_test = train_test_split(
    features, target, data['Date'], test_size=0.2, random_state=0)

# Create the model
model = LinearRegression()

# Train the model
model.fit(X_train, y_train)

# Make predictions on the test set
y_pred = model.predict(X_test)

# Create a DataFrame to hold test results and sort by date
results = pd.DataFrame({'Date': dates_test, 'Actual': y_test, 'Predicted': y_pred})
results.sort_values('Date', inplace=True)

# Display the first few results
print(results.head())

# Calculate the mean squared error
mse = mean_squared_error(results['Actual'], results['Predicted'])
print(f'Mean Squared Error: {mse}')

# Plot the actual vs predicted values with dates on the x-axis
plt.figure(figsize=(10, 6))
plt.plot(results['Date'], results['Actual'], label='Actual Prices')
plt.plot(results['Date'], results['Predicted'], label='Predicted Prices', linestyle='dashed')
plt.legend()
plt.xlabel('Date')
plt.ylabel('Stock Price')
plt.title('Actual vs Predicted Stock Prices')
plt.xticks(rotation=45)
plt.show()
