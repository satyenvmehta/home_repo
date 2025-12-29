import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


###### Read and create basic input params  #####
# Load the dataset
data = pd.read_csv('historical_stock_prices.csv')

# Ensure the data is sorted by date
data['Date'] = pd.to_datetime(data['Date'])
data.sort_values('Date', inplace=True)

# Create lagged features
data['Lag_1'] = data['Close'].shift(1)
data['Lag_2'] = data['Close'].shift(2)
data['Lag_3'] = data['Close'].shift(3)

# Create a moving average feature
data['MA_5'] = data['Close'].rolling(window=5).mean()

# Shift the 'Close' column to get the next day's closing price
data['Next_Close'] = data['Close'].shift(-1)

# Drop the last row as it will have NaN value for 'Next_Close'
data.dropna(inplace=True)
print(data.head())

###### Select Features and Target  #####
# Selecting relevant features including lagged and moving average features
features = data[['Open', 'High', 'Low', 'Volume', 'Lag_1', 'Lag_2', 'Lag_3', 'MA_5']]
target = data['Next_Close']

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test, dates_train, dates_test = train_test_split(
    features, target, data['Date'], test_size=0.2, random_state=0)


######  Train the Linear Regression Model  ########
# Create the model
model = LinearRegression()
# Train the model
model.fit(X_train, y_train)

##### Make predictions on the test set  #######
y_pred = model.predict(X_test)

# Create a DataFrame to hold test results and sort by date
results = pd.DataFrame({'Date': dates_test, 'Actual': y_test, 'Predicted': y_pred})
results.sort_values('Date', inplace=True)

# Display the first/last  few results
print(results.head())
print(results.tail())

#######  Step 6: Evaluate the Model and Plot the Results   #####
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

###
#         Date      Actual   Predicted
# 5  2020-01-08  104.087486  152.868366
# 14 2020-01-21  189.882522  146.514418
# 16 2020-01-23  158.815767  143.666039
# 19 2020-01-28  113.157600  146.673129
# 25 2020-02-05  174.860601  149.546797
#           Date      Actual   Predicted
# 499 2021-11-30  171.337041  147.915909
# 503 2021-12-06  116.480559  149.951458
# 505 2021-12-08  131.750370  153.462681
# 513 2021-12-20  157.499033  144.225282
# 519 2021-12-28  136.567633  142.400235

#          Date      Actual   Predicted
# 5  2020-01-08  104.087486  152.868366
# 14 2020-01-21  189.882522  146.514418
# 16 2020-01-23  158.815767  143.666039
# 19 2020-01-28  113.157600  146.673129
# 25 2020-02-05  174.860601  149.546797
#           Date      Actual   Predicted
# 499 2021-11-30  171.337041  147.915909
# 503 2021-12-06  116.480559  149.951458
# 505 2021-12-08  131.750370  153.462681
# 513 2021-12-20  157.499033  144.225282
# 519 2021-12-28  136.567633  142.400235
# ###