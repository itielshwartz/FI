import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
%matplotlib osx
path = "training_set_data.csv"
data = pd.read_csv(path, header=None, names=['hour','score'])
data.insert(0, 'Ones', 1)
cols = data.shape[1]
X = data.iloc[:,0:cols-1]
y = data.iloc[:,cols-1:cols]
# convert from data frames to numpy matrices
X = np.matrix(X.values)
y = np.matrix(y.values)
model = linear_model.LinearRegression()
model.fit(X, y)
x = np.array(X[:, 1].A1)
f = model.predict(X).flatten()
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(x, f, 'r', label='Prediction')
ax.scatter(data.hour, data.score, label='Traning Data')
ax.legend(loc=2)
ax.set_xlabel('userKarma')
ax.set_ylabel('score')
ax.set_title('Predicted score vs. userKarma')