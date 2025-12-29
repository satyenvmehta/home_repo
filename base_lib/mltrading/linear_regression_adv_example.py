import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error


from market.client import getHistoricalDataFor


# Plot the data
# Plot the actual vs predicted values with dates on the x-axis
def plot_data(results):
    # Calculate the mean squared error
    mse = mean_squared_error(results['Actual'], results['Predicted'])
    print(f'Mean Squared Error: {mse}')

    plt.figure(figresultssize=(10, 6))
    plt.plot(['Date'], results['Actual'], label='Actual Prices')
    plt.plot(results['Date'], results['Predicted'], label='Predicted Prices', linestyle='dashed')
    plt.legend()
    plt.xlabel('Date')
    plt.ylabel('Stock Price')
    plt.title('Actual vs Predicted Stock Prices')
    plt.xticks(rotation=45)
    plt.show()
    return

def print_sample_results(results):
    # Display the first/last  few results
    print(results.head())
    print(results.tail())
    return

def create_results_df(dates_test, y_test, y_pred):
    # Create a DataFrame to hold test results and sort by date
    results = pd.DataFrame({'Date': dates_test, 'Actual': y_test, 'Predicted': y_pred})
    results.sort_values('Date', inplace=True)
    return results

def create_model(data):
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

    results = create_results_df(dates_test, y_test, y_pred)
    return results


def predict_next_day():
    pass
    # Predict the next day's stock price
    # return next_day_data[0]

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
    return data

from core.base_container_classes import BaseDict

if __name__ == '__main__':
    tkr_list = ['GOOG' ] # 'GOOG', 'MSFT', 'NFLX', 'ORCL', 'INTC', 'ADBE', 'CSCO', 'IBM', 'QCOM']
    results = getHistoricalDataFor(tkr_list)
    if isinstance(results, BaseDict):
        for key, data in results.items():
            print(f'{key}: {data}')
            # Process the data
            data = process_data(data)
            ##### Make predictions on the test set  #######
            results = create_model(data)
            print_sample_results(results)
            # plot_data(results)



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


def old_process_data(data):
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