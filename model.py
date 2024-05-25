from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
from sklearn.model_selection import GridSearchCV
import joblib #library to save the model
import preprocessing as pp #This will be the pre-processing part of the project (pre_processing.py)

def load_data():
    
    preprocessor = pp.DataPreprocessor(movies_data_path='tmdb_5000_movies.csv', 
                                       credits_data_path='tmdb_5000_credits.csv', 
                                       reference_year=2024)
    preprocessor.load_data()
    dataset = preprocessor.preprocess()
    return dataset


def split_data(dataset):
   
    X = dataset.iloc[:, :-1].values #all values except last column (budget - popularity - runtime - vote_average - vote_count - age)
    y = dataset.iloc[:, -1].values  #values of last column which is dependent attribute(revenue)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
    return X_train, X_test, y_train, y_test


def evaluate_model(model, X_test, y_test):
   
    y_pred = model.predict(X_test) #Testing part for evaulation (20% of the dataset is seperated for testing)
    mse = mean_squared_error(y_test, y_pred)
    return mse

def tune_hyperparameters(X_train, y_train):
    model = RandomForestRegressor(random_state=0)
    param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10],
        'min_samples_leaf': [1, 2, 4]
    }
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, scoring='neg_mean_squared_error', cv=5, n_jobs=-1, verbose=2)
    grid_search.fit(X_train, y_train)
    print("Best Parameters:", grid_search.best_params_)
    return grid_search.best_estimator_

def predict_random_movies(model, dataset, n=20):
    sample = dataset.sample(n)  # Randomly select n samples
    X_sample = sample.iloc[:, :-1].values
    y_sample_actual = sample.iloc[:, -1].values
    
    y_sample_pred = model.predict(X_sample)
    
    return y_sample_actual, y_sample_pred, sample

if __name__ == "__main__":
    # Load dataset from pre_processing.py
    dataset = load_data()

    # Split dataset
    X_train, X_test, y_train, y_test = split_data(dataset)

    # Train the model (fitting)
    model = tune_hyperparameters(X_train, y_train)
    
    # Save the model to a file
    joblib.dump(model, 'randomforest_model.pkl')
    
    # Evaluating the model with mse
    mse = evaluate_model(model, X_test, y_test)
    print("Mean Squared Error:", mse)

    y_pred = model.predict(X_test)
    
    # Plot predicted vs actual revenue
    plt.figure(figsize=(8, 6))
    plt.scatter(y_test, y_pred, color='blue', alpha=0.5, label='Predicted vs Actual')
    plt.plot([min(y_test), max(y_test)], [min(y_test), max(y_test)], color='red', label='Ideal Fit')  # Diagonal line
    plt.xlabel('Actual Revenue')
    plt.ylabel('Predicted Revenue')
    plt.title('Actual vs Predicted Revenue')
    plt.legend()
    plt.grid(True)
    plt.show()

    y_sample_actual, y_sample_pred, sample = predict_random_movies(model, dataset)
    
    # Display the comparison
    comparison_df = pd.DataFrame({'Actual Revenue': y_sample_actual, 'Predicted Revenue': y_sample_pred}, index=sample.index)

    # Format the numbers with commas
    comparison_df['Actual Revenue'] = comparison_df['Actual Revenue'].apply(lambda x: f"{x:,.0f}")
    comparison_df['Predicted Revenue'] = comparison_df['Predicted Revenue'].apply(lambda x: f"{x:,.0f}")

    print("\nComparison of Actual vs Predicted Revenue for Random 10 Movies:\n")
    print(comparison_df)

    
    # Plot predicted vs actual revenue for random sample
    plt.figure(figsize=(8, 6))
    plt.scatter(y_sample_actual, y_sample_pred, color='green', alpha=0.5, label='Predicted vs Actual (Random Sample)')
    plt.plot([min(y_sample_actual), max(y_sample_actual)], [min(y_sample_actual), max(y_sample_actual)], color='red', label='Ideal Fit')  # Diagonal line
    plt.xlabel('Actual Revenue')
    plt.ylabel('Predicted Revenue')
    plt.title('Actual vs Predicted Revenue (Random Sample)')
    plt.legend()
    plt.grid(True)
    plt.show()