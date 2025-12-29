import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


from market.client import getHistoricalDataFor

def plot_data(data):
    # Plot the data
    plt.figure(figsize=(10, 6))
    plt.plot(data)
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title('Historical Stock Prices')
    plt.show()
    return

def predict_next_day(model, last_day_data, features):
    # Predict the next day's stock price
    return next_day_data[0]


def plot_the_graph(results, sort_by):
    # Plot the actual vs predicted values with dates on the x-axis
    plt.figure(figsize=(10, 6))
    plt.plot(results[sort_by], results['Actual'], label='Actual Prices')
    plt.plot(results[sort_by], results['Predicted'], label='Predicted Prices', linestyle='dashed')
    plt.legend()
    plt.xlabel(sort_by)
    plt.ylabel('Stock Price')
    plt.title('Actual vs Predicted Stock Prices')
    plt.xticks(rotation=45)
    plt.show()
    return

def linear_reg_model_prediction(model, features, target, data):
    print("Starting linear_reg_model_prediction ...")
    # Split the data into training and testing sets
    print('features: ', features.shape)
    print('target: ', target.shape)
    # features = features.values.reshape(-1, 1)
    # X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=0)

    # Splitting the data into training and testing sets
    X_train, X_test, y_train, y_test, dates_train, dates_test = train_test_split(
        features, target, data.index, test_size=0.2, random_state=0)

    # Train the model
    model.fit(X_train, y_train)

    # Make predictions on the test set
    y_pred = model.predict(X_test)
    # Display the first few predictions
    print(y_pred[:5])

    sort_by = 'Date1'
    # Create a DataFrame to hold test results and sort by date
    results = pd.DataFrame({sort_by: dates_test, 'Actual': y_test, 'Predicted': y_pred})

    results.sort_values(sort_by, inplace=True)

    print(results.head())
    print(results.tail())
    # Calculate the mean squared error
    mse = mean_squared_error(y_test, y_pred)
    print(f'Mean Squared Error: {mse}')
    # old_graph(y_test, y_pred)
    plot_the_graph(results, sort_by)
    return


def old_graph(y_test, y_pred):
    # Plot the actual vs predicted values
    plt.figure(figsize=(10, 6))
    plt.plot(y_test.values, label='Actual Prices')
    plt.plot(y_pred, label='Predicted Prices', linestyle='dashed')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title('Actual vs Predicted Stock Prices')
    plt.show()
    return


def convert_index_col2_date(df):
    index_col_name = df.index.name
    df.index = pd.to_datetime(df.index)
    # Convert the DateTime index to date format
    df.index = df.index.date
    df.index.name = index_col_name
    df = df[~df.index.isna()]
    # df.index = df.index.strftime('%Y-%m-%d')
    return df

def process_data(data):

    # Convert the date column to datetime
    # data.set_index('Date', inplace=True)

    data.index = pd.to_datetime(data.index)

    data = convert_index_col2_date(data)

    data.sort_values('Date', inplace=True)

    # Shift the 'Close' column to get the next day's closing price
    # data['Next_Close'] = data['Close'].shift(-1)

    # Drop any rows with missing values
    data.dropna(inplace=True)

    # Display the first few rows
    print(data.head())

    # Create features and target
    features = data[['Open', 'High', 'Low', 'Volume']]
    target = data['Close']
    # target = data['Next_Close']

    return features, target

from core.base_container_classes import BaseDict

if __name__ == '__main__':
    tkr_list = ['GOOG' ] # 'GOOG', 'MSFT', 'NFLX', 'ORCL', 'INTC', 'ADBE', 'CSCO', 'IBM', 'QCOM']
    results = getHistoricalDataFor(tkr_list)
    if isinstance(results, BaseDict):
        for key, data in results.items():
            print(f'{key}: {data}')
            # Process the data
            features, target = process_data(data)
            # Plot the data
            # plot_data(target)
            # Create the model
            model = LinearRegression()
            # Train the model
            linear_reg_model_prediction(model, features, target, data)

#
# # Process the data
# features, target = process_data(data)
# # Splitting the data into training and testing sets
# X_train, X_test, y_train, y_test = train_test_split(features, target, test_size=0.2, random_state=0)
# # Create the model
# model = LinearRegression()
# # Train the model
# model.fit(X_train, y_train)
#
# # Make predictions on the test set
# y_pred = model.predict(X_test)
#
# # Display the first few predictions
# print(y_pred[:5])
#
# # Calculate the mean squared error
# mse = mean_squared_error(y_test, y_pred)
# print(f'Mean Squared Error: {mse}')
#
# # Plot the actual vs predicted values
# plt.figure(figsize=(10, 6))
# plt.plot(y_test.values, label='Actual Prices')
# plt.plot(y_pred, label='Predicted Prices', linestyle='dashed')
# plt.legend()
# plt.xlabel('Date')
# plt.ylabel('Stock Price')
# plt.title('Actual vs Predicted Stock Prices')
# plt.show()
