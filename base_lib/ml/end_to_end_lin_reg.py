import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

# Download the data from UCI Machine Learning Repository (optional)
# You can also replace this with your own data loading logic

url = "https://archive.ics.uci.edu/ml/machine-learning-databases/housing/housing.csv"

filen = 'G:\My Drive\Work\ML\housing.csv'
data = pd.read_csv(filen)

# Define features (independent variables)
features = ['longitude', 'latitude', 'housing_median_age', 'total_rooms', 'total_bedrooms', 'population', 'households', 'median_income']


# longitude	latitude	housing_median_age	total_rooms	total_bedrooms	population	households	median_income	median_house_value	ocean_proximity

# Define target variable (dependent variable)
target = 'median_house_value'

X = data[features]  # Features DataFrame
y = data[target]     # Target Series

value_counts = y.value_counts()
categories_to_keep = value_counts[value_counts > 1].index  # Select categories with more than 1 data point

# Filter data to keep rows with categories in categories_to_keep
data_filtered = data[data[y.name].isin(categories_to_keep)]
y_filtered = data_filtered[y.name]  # Update target variable after filtering

sss = StratifiedShuffleSplit(n_splits=10, test_size=0.2, random_state=42)

mse_scores = []
# for a, b in sss.split(X, y_filtered):
#     pass

X_filtered = X.iloc[y_filtered.index]

for train_index, test_index in sss.split(X_filtered, y_filtered):
    X_train, X_test = X_filtered.iloc[train_index], X_filtered.iloc[test_index]
    y_train, y_test = y_filtered.iloc[train_index], y_filtered.iloc[test_index]

    # Create and train the Linear Regression model
    model = LinearRegression()

    data_train = pd.concat([X_train, y_train], axis=1)  # Combine features and target
    data_train = data_train.dropna()  # Drop rows with NaN in any column

    # Separate features and target variable again (after filtering)
    X_train = data_train.iloc[:, :-1]  # All columns except the last (target)
    y_train = data_train.iloc[:, -1]  # Last column (target)

    model.fit(X_train, y_train)

    test_train = pd.concat([X_test, y_test], axis=1)
    test_train = test_train.dropna()
    X_test = test_train.iloc[:, :-1]
    y_test = test_train.iloc[:, -1]

    # Make predictions on the testing data
    y_pred = model.predict(X_test)

    # Calculate mean squared error
    mse = mean_squared_error(y_test, y_pred)
    mse_scores.append(mse)

print(f"Mean Squared Errors (across {len(mse_scores)} folds): {mse_scores}")
