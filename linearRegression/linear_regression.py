import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn import linear_model


def predict_and_draw_liner_model(path, var_x_name, var_y_name):
    data = pd.read_csv(path, header=None, names=[var_x_name, var_y_name])
    cols = data.shape[1]

    # convert from data frames to numpy matrices
    X = np.matrix(data.iloc[:, 0:cols - 1])
    y = np.matrix(data.iloc[:, cols - 1:cols])

    # Create model + train it
    model = linear_model.LinearRegression()
    model.fit(X, y)

    # Get the model prediction
    f = model.predict(X).flatten()

    # Plot the graph
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.plot(X, f, 'r', label='Prediction')
    ax.scatter(data[var_x_name], data[var_y_name], label='Traning Data')
    ax.legend(loc=2)
    ax.set_xlabel(var_x_name)
    ax.set_ylabel(var_y_name)
    ax.set_title('Predicted {} using {}'.format(var_x_name, var_y_name))


path, var_x_name, var_y_name = "training_set_data_karma_to_score.csv", "karma", "score"
predict_and_draw_liner_model(path, var_x_name, var_y_name)
