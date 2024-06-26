# -*- coding: utf-8 -*-
"""LogReg.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Y-vnrZXdLTgSEptHxJV7tFpSXvPMn5Of
"""

from ucimlrepo import fetch_ucirepo

# fetch dataset
rice_cammeo_and_osmancik = fetch_ucirepo(id=545)

# data (as pandas dataframes)
X = rice_cammeo_and_osmancik.data.features
y = rice_cammeo_and_osmancik.data.targets

# metadata
print(rice_cammeo_and_osmancik.metadata)

# variable information
print(rice_cammeo_and_osmancik.variables)

X.head()

y.head()

import pandas as pd

data_rice = pd.concat([X, y], axis=1)

# Display the first few rows of the dataset to understand its structure
data_rice.head(), data_rice.describe(), data_rice.info()

# find the distinct values in the target column
data_rice['Class'].unique()

# Let's normalize the data
for column in data_rice.select_dtypes(include=['number']).columns:  # This ensures only numeric columns are selected (not the target column)
    min_col = data_rice[column].min()
    max_col = data_rice[column].max()

    # Avoid division by zero in case max_col equals min_col
    if max_col != min_col:
        data_rice[column] = (data_rice[column] - min_col) / (max_col - min_col)
    else:
        data_rice[column] = 0  # Assign 0 to all rows if max_col equals min_col

# Replace the Class column with 0 and 1
data_rice['Class'] = data_rice['Class'].replace('Cammeo', 0)
data_rice['Class'] = data_rice['Class'].replace('Osmancik', 1)

data_rice.head()

X = data_rice.drop('Class', axis=1)
y = data_rice['Class']

X.head()

print(X.to_numpy()[1])

def split_data(data_rice):
    # data refreshing
    shuffled_data = data_rice.sample(frac=1, random_state=42).reset_index(drop=True)

    # Define the split size for the training set
    train_size = int(0.8 * len(shuffled_data))  # 80% of data for training, 20% for testing

    # Split the data
    train_data = shuffled_data[:train_size]
    test_data = shuffled_data[train_size:]

    X_train = train_data.drop('Class', axis=1)  # Replace 'target_column' with your actual target column name
    y_train = train_data['Class']

    X_test = test_data.drop('Class', axis=1)
    y_test = test_data['Class']

    return X_train, y_train, X_test, y_test

import numpy as np

def initialize_weights(dim):
    w = np.zeros(dim)  # initialize the weights to zeros
    b = 0.0 # initialize the bias to zero
    return w, b


def sigmoid(z):
    z = np.clip(z, -500, 500)  # Clip z to avoid extreme values that lead to overflow
    return 1 / (1 + np.exp(-z))



# epsilon to avoid division by zero

def logloss(y_true, y_pred, epsilon=1e-8):
    y_pred = np.clip(y_pred, epsilon, 1 - epsilon)  # Clip predictions to avoid log(0)
    return -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))


def gradient_dw(x, y, w, b, alpha, N):  # negative gradient of the log-likelihood function w.r.t w
  '''In this function, we will compute the gradient w.r.to w '''
  dw = x * (y-sigmoid(np.dot(w.T,x)+b)) - ((alpha*w*w)/N)
  return dw


def gradient_db(x, y, w, b):  # negative gradient of the log-likelihood function w.r.t b
  '''In this function, we will compute gradient w.r.to b '''
  db = y-sigmoid(np.dot(w.T,x)+b)
  return db

def test(X, y, w, b):
  y_pred = []
  X = np.array(X)
  for i in range(len(X)):
    z = sigmoid(np.dot(w.T, X[i]) + b)
    y_pred.append(z)
  # turn y into a numpy array

  loss = logloss(y, y_pred)
  return loss

def predict(X, w, b):
  y_pred = []
  for i in range(len(X)):
    if sigmoid(np.dot(w.T, X[i]) + b) > 0.5:
      y_pred.append(1)
    else:
      y_pred.append(0)
  return y_pred

import time

def train_sgd(X, y, w, b, alpha, lr, epochs):
    N = len(X)
    X = np.array(X)
    y = np.array(y)  # Ensure y is also a numpy array
    prev_loss = np.inf
    epsilon = 1e-5
    loss = logloss(y, 0, epsilon)
    print(f'Initial Loss: {loss}')
    start_time = time.time()
    losses = []
    for epoch in range(epochs):
        # Shuffle the data
        shuffle_index = np.random.permutation(N)
        X_shuffled, y_shuffled = X[shuffle_index], y[shuffle_index]

        epoch_losses = []  # Collect losses for each instance

        for i in range(N):
            dw = gradient_dw(X_shuffled[i], y_shuffled[i], w, b, alpha, N)
            db = gradient_db(X_shuffled[i], y_shuffled[i], w, b)
            w = w + lr * dw
            b = b + lr * db

            # Predict on the shuffled instance and calculate loss
            y_pred = sigmoid(np.dot(w.T, X_shuffled[i]) + b)
            loss = logloss(y_shuffled[i], y_pred, epsilon)
            # isnan

            epoch_losses.append(loss)

        # Average loss for the epoch
        avg_epoch_loss = np.mean(epoch_losses)
        losses.append(avg_epoch_loss)
        print(f'Epoch: {epoch}, Loss: {avg_epoch_loss}')

        # Early stopping (optional) based on average loss
        if (epoch > 0 and avg_epoch_loss > prev_loss) or np.isnan(avg_epoch_loss): # If the average loss is nan
            print("Stopping early due to increase in average loss.")
            break
        prev_loss = avg_epoch_loss
    end_time = time.time()
    training_time = end_time - start_time
    return w, b, losses, training_time

def train_batch_gd(X, y, w, b, alpha, lr, epochs):
    N = len(X)
    X = np.array(X)
    prev_loss = np.inf

    start_time = time.time()
    losses = []

    for epoch in range(epochs):
        # Calculate the gradient for the whole dataset
        dw = np.mean([gradient_dw(X[i], y[i], w, b, alpha, N) for i in range(N)], axis=0)
        db = np.mean([gradient_db(X[i], y[i], w, b) for i in range(N)])

        # Update weights and bias for the whole dataset
        w = w + lr * dw
        b = b + lr * db

        # Calculate predictions and loss for the entire dataset
        y_pred = sigmoid(np.dot(X, w) + b)
        loss = logloss(y, y_pred)
        losses.append(loss)

        print(f'Epoch: {epoch}, Loss: {loss}')

        # Stop if the loss is not decreasing
        if epoch > 0 and loss >= prev_loss:
            end_time = time.time()
            training_time = end_time - start_time
            print("Stopping early due to increase in loss.")
            break
        prev_loss = loss
    end_time = time.time()
    training_time = end_time - start_time
    return w, b, losses, training_time

shuffled_data = data_rice.sample(frac=1, random_state=42).reset_index(drop=True)

# Define the split size for the training set
train_size = int(0.8 * len(shuffled_data))  # 80% of data for training, 20% for testing

# Split the data
train_data = shuffled_data[:train_size]
test_data = shuffled_data[train_size:]

X_train = train_data.drop('Class', axis=1)  # Replace 'target_column' with your actual target column name
y_train = train_data['Class']

X_test = test_data.drop('Class', axis=1)
y_test = test_data['Class']

print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

"""## logistic regression trained with GD (alpha = 0), no regularization"""

loss_dict = {}
accuracy_dict = {}

X_train.head()

y_train.head()

X_train, y_train, X_test, y_test = split_data(data_rice)

w, b = initialize_weights(X_train.shape[1])

alpha = 0
lr = 1
epochs = 400
w, b, losses, training_time = train_batch_gd(X_train, y_train, w, b, alpha, lr, epochs)

test_loss = test(X_test, y_test, w, b)
print(f'Test loss: {test_loss}')
loss_dict["GD"] = (test_loss)


# test accuracy
y_pred = predict(X_test.to_numpy(), w, b)
test_accuracy = np.mean(y_pred == y_test.to_numpy())
print(f'Accuracy: {test_accuracy}')

# training accuracy
y_pred = predict(X_train.to_numpy(), w, b)
training_accuracy = np.mean(y_pred == y_train.to_numpy())

accuracy_dict["GD"] = (training_accuracy, test_accuracy)

"""## 5-fold cross validation to find the best L2 regularization parameter for the Batch Gradient Descent"""

shuffled_data = data_rice.sample(frac=1, random_state=42).reset_index(drop=True)


def kfold_split(data, k):
    data_split = []
    fold_size = int(len(data) / k)
    for i in range(k):
        fold = data[i * fold_size: (i + 1) * fold_size]
        data_split.append(fold)
    return data_split

k = 5
data_folds = kfold_split(shuffled_data, k)

print(data_folds[0].shape)

data_folds[0].head()

# shuffle the data

shuffled_data = data_rice.sample(frac=1, random_state=42).reset_index(drop=True)


def kfold_split(data, k):
    data_split = []
    fold_size = int(len(data) / k)
    for i in range(k):
        fold = data[i * fold_size: (i + 1) * fold_size]
        data_split.append(fold)
    return data_split

k = 5
data_folds = kfold_split(shuffled_data, k)

alpha_values = [0.01, 0.1, 1, 10, 100]

all_loss = []
all_accuracy = []

lr = 1
epochs = 100



for i in range(k):
    # Define the split size for the training set
    train_size = int(0.8 * len(data_folds[i]))  # 80% of data for training, 20% for testing
    # Split the data
    train_data = data_folds[i][:train_size]
    test_data = data_folds[i][train_size:]

    X_train = train_data.drop('Class', axis=1).to_numpy()  # Convert DataFrame to numpy array
    y_train = train_data['Class'].to_numpy()  # Convert Series to numpy array

    X_test = test_data.drop('Class', axis=1).to_numpy()  # Convert DataFrame to numpy array
    y_test = test_data['Class'].to_numpy()  # Convert Series to numpy array

    w, b = initialize_weights(X_train.shape[1])

    alpha = alpha_values[i]

    print(f'Fold {i+1} with alpha: {alpha}')
    print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

    w, b, losses, training_time = train_batch_gd(X_train, y_train, w, b, alpha, lr, epochs)

    test_loss = test(X_test, y_test, w, b)

    all_loss.append(test_loss)

    # test accuracy
    y_pred = predict(X_test, w, b)
    test_accuracy = np.mean(y_pred == y_test)
    all_accuracy.append(test_accuracy)

all_loss

all_accuracy



# we see that accuracy is maximum for alpha = 1 hence we will use this value for our model
# let's check the performance of our model on the entire dataset

X_train, y_train, X_test, y_test = split_data(data_rice)

w, b = initialize_weights(X_train.shape[1])

alpha = 1
lr = 1
epochs = 200

w, b, losses, training_time = train_batch_gd(X_train, y_train, w, b, alpha, lr, epochs)

test_loss = test(X_test, y_test, w, b)
print(f"Test Loss: {test_loss}")
loss_dict["L2-GD"] = test_loss



# test accuracy
y_pred = predict(X_test.to_numpy(), w, b)
test_accuracy = np.mean(y_pred == y_test.to_numpy())
print(f'Accuracy: {test_accuracy}')

# training accuracy
y_pred = predict(X_train.to_numpy(), w, b)
training_accuracy = np.mean(y_pred == y_train.to_numpy())

accuracy_dict["L2-GD"] = (training_accuracy, test_accuracy)

"""### now the thing is for lambda (regularization parameter) 0 learning rate 1 works the best as accuracy, but for lambda 10 learning rate 0.1 works better. Since the accuracy difference is not that big, i will use learning rate 1 for batch gradient descent linear regression not for only consistency but also test loss is less than the lr 0.1."""

accuracy_dict

"""## now it's time for Stochastic Gradient Descent

### i will be using learning rate 0.1 for SGD, since it's faster than BGD and i the step size can get so big.
"""

# initialize the weights
w, b = initialize_weights(X_train.shape[1])

alpha = 0
lr = 0.1
epochs = 200
w, b, losses, training_time = train_sgd(X_train, y_train, w, b, alpha, lr, epochs)

test_loss = test(X_test, y_test, w, b)
print(f'Test loss: {test_loss}')
loss_dict["SGD"] = test_loss

# test accuracy
y_pred = predict(X_test.to_numpy(), w, b)
test_accuracy = np.mean(y_pred == y_test)
print(f'Accuracy: {test_accuracy}')

# training accuracy
y_pred = predict(X_train.to_numpy(), w, b)
training_accuracy = np.mean(y_pred == y_train)

accuracy_dict["SGD"] = (training_accuracy, test_accuracy)

"""## 5-fold with stochastic gradient descent"""

k = 5
data_folds = kfold_split(shuffled_data, k)

alpha_values = [0.01, 0.1, 1, 10, 100]

all_loss = []

all_accuracy = []

lr = 0.1
epochs = 50

for i in range(k):
    # Define the split size for the training set
    train_size = int(0.8 * len(data_folds[i]))  # 80% of data for training, 20% for testing

    # Split the data
    train_data = data_folds[i][:train_size]
    test_data = data_folds[i][train_size:]

    X_train = train_data.drop('Class', axis=1).to_numpy()  # Replace 'target_column' with your actual target column name
    y_train = train_data['Class'].to_numpy()  # Convert Series to numpy array

    X_test = test_data.drop('Class', axis=1).to_numpy()
    y_test = test_data['Class'].to_numpy()

    w, b = initialize_weights(X_train.shape[1])

    alpha = alpha_values[i]


    w, b, losses, training_time = train_sgd(X_train, y_train, w, b, alpha, lr, epochs)

    test_loss = test(X_test, y_test, w, b)

    all_loss.append(test_loss)

    y_pred = predict(X_test, w, b)
    acc = np.mean(y_pred == y_test)
    all_accuracy.append(acc)

all_loss

all_accuracy

"""### the best accuracy comes from lambda 0.1, the loss diverges for lambda >= 1. also i tested the learning rates here and the 0.1 is the best for not diverging."""

# data refreshing
shuffled_data = data_rice.sample(frac=1, random_state=42).reset_index(drop=True)

# Define the split size for the training set
train_size = int(0.8 * len(shuffled_data))  # 80% of data for training, 20% for testing

# Split the data
train_data = shuffled_data[:train_size]
test_data = shuffled_data[train_size:]

X_train = train_data.drop('Class', axis=1)  # Replace 'target_column' with your actual target column name
y_train = train_data['Class']

X_test = test_data.drop('Class', axis=1)
y_test = test_data['Class']

# initialize the weights
w, b = initialize_weights(X_train.shape[1])

alpha = 0.1
lr = 0.1
epochs = 200
w, b, losses, training_time = train_sgd(X_train, y_train, w, b, alpha, lr, epochs)

test_loss = test(X_test, y_test, w, b)
print(f'Test loss: {test_loss}')
loss_dict["L2-SGD"] = test_loss

# test accuracy
y_pred = predict(X_test.to_numpy(), w, b)
test_accuracy = np.mean(y_pred == y_test.to_numpy())
print(f'Accuracy: {test_accuracy}')

# training accuracy
y_pred = predict(X_train.to_numpy(), w, b)
training_accuracy = np.mean(y_pred == y_train.to_numpy())

accuracy_dict["L2-SGD"] = (training_accuracy, test_accuracy)

accuracy_dict

"""## Now let's compare the times"""

import matplotlib.pyplot as plt

w, b = initialize_weights(X_train.shape[1])

alpha = 1
lr = 1
epochs = 400

# Train using GD
w_gd, b_gd, losses_gd, time_gd = train_batch_gd(X_train, y_train, w, b, alpha, lr, epochs)

accuracy_gd = np.mean(predict(X_test.to_numpy(), w_gd, b_gd) == y_test.to_numpy())

alpha = 0.1
lr = 0.01
# Train using SGD
w_sgd, b_sgd, losses_sgd, time_sgd = train_sgd(X_train, y_train, w, b, alpha, lr, epochs)

accuracy_sgd = np.mean(predict(X_test.to_numpy(), w_sgd, b_sgd) == y_test.to_numpy())

# Plot the loss values
plt.plot(losses_gd, label='GD')
plt.plot(losses_sgd, label='SGD')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Print the training times
print(f'Training time for GD: {time_gd} seconds')
print(f'Training time for SGD: {time_sgd} seconds')

# Print the accuracies
print(f'Accuracy for GD: {accuracy_gd}')
print(f'Accuracy for SGD: {accuracy_sgd}')

"""# SGD is dramatically faster than BGD and final accuracy is better than BGD"""

# Now we will test different learning rates for the SGD model

lr_values = [0.01, 0.1, 1, 10, 100]
all_losses = []
all_accuracies = []

for lr in lr_values:
    w, b = initialize_weights(X_train.shape[1])
    alpha = 0.1
    epochs = 200
    w, b, losses, training_time = train_sgd(X_train, y_train, w, b, alpha, lr, epochs)
    test_loss = test(X_test, y_test, w, b)
    all_losses.append(test_loss)
    y_pred = predict(X_test.to_numpy(), w, b)
    test_accuracy = np.mean(y_pred == y_test.to_numpy())
    all_accuracies.append(test_accuracy)

all_losses

all_accuracies

"""## let's plot 0.01 and 0.1 learning rates for SGD"""

import matplotlib.pyplot as plt

X_train, y_train, X_test, y_test = split_data(data_rice)

w, b = initialize_weights(X_train.shape[1])

alpha = 0.1
lr = 0.01
epochs = 200

# Train using GD
w_sgd_01, b_sgd_01, losses_sgd_01, time_sgd_01 = train_sgd(X_train, y_train, w, b, alpha, lr, epochs)

accuracy_sgd_01 = np.mean(predict(X_test.to_numpy(), w_sgd_01, b_sgd_01) == y_test.to_numpy())

alpha = 0.1
lr = 0.1
# Train using SGD
w_sgd, b_sgd, losses_sgd, time_sgd = train_sgd(X_train, y_train, w, b, alpha, lr, epochs)

accuracy_sgd = np.mean(predict(X_test.to_numpy(), w_sgd, b_sgd) == y_test.to_numpy())

# Plot the loss values
plt.plot(losses_sgd_01, label='SGD-lr=0.01')
plt.plot(losses_sgd, label='SGD-lr=0.1')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.show()

# Print the training times
print(f'Training time for SGD-lr=0.01: {time_sgd_01} seconds')
print(f'Training time for SGD-lr=0.1: {time_sgd} seconds')

# Print the accuracies
print(f'Accuracy for SGD-lr=0.01: {accuracy_sgd_01}')
print(f'Accuracy for SGD-lr=0.1: {accuracy_sgd}')

from ucimlrepo import fetch_ucirepo

# fetch dataset
breast_cancer_wisconsin_diagnostic = fetch_ucirepo(id=17)

# data (as pandas dataframes)
X = breast_cancer_wisconsin_diagnostic.data.features
y = breast_cancer_wisconsin_diagnostic.data.targets

# metadata
print(breast_cancer_wisconsin_diagnostic.metadata)

# variable information
print(breast_cancer_wisconsin_diagnostic.variables)

data_cancer = pd.concat([X, y], axis=1)

# Display the first few rows of the dataset to understand its structure
data_cancer.head()

data_cancer["Diagnosis"].unique()

# Let's normalize the data
for column in data_cancer.select_dtypes(include=['number']).columns:  # This ensures only numeric columns are selected (not the target column)
    min_col = data_cancer[column].min()
    max_col = data_cancer[column].max()

    # Avoid division by zero in case max_col equals min_col
    if max_col != min_col:
        data_cancer[column] = (data_cancer[column] - min_col) / (max_col - min_col)
    else:
        data_cancer[column] = 0  # Assign 0 to all rows if max_col equals min_col

# Replace the Diagnosis column with 0 and 1

data_cancer['Diagnosis'] = data_cancer['Diagnosis'].replace('M', 0)
data_cancer['Diagnosis'] = data_cancer['Diagnosis'].replace('B', 1)

data_cancer.head()

# Split the data into features and target

X = data_cancer.drop('Diagnosis', axis=1)
y = data_cancer['Diagnosis']

# Shuffle the data
shuffled_data = data_cancer.sample(frac=1, random_state=42).reset_index(drop=True)

# Define the split size for the training set
train_size = int(0.8 * len(shuffled_data))  # 80% of data for training, 20% for testing

# Split the data

train_data = shuffled_data[:train_size]

test_data = shuffled_data[train_size:]

X_train = train_data.drop('Diagnosis', axis=1)  # Replace 'target_column' with your actual target column name
y_train = train_data['Diagnosis']

X_test = test_data.drop('Diagnosis', axis=1)
y_test = test_data['Diagnosis']

print(X_train.shape, y_train.shape, X_test.shape, y_test.shape)

# train the stochastic linear regression model

w, b = initialize_weights(X_train.shape[1])

alpha = 0.1

lr = 0.1

epochs = 200

w, b, losses, training_time = train_sgd(X_train, y_train, w, b, alpha, lr, epochs)

test_loss = test(X_test, y_test, w, b)

print(f'Test loss: {test_loss}')

# test accuracy

y_pred = predict(X_test.to_numpy(), w, b)

test_accuracy = np.mean(y_pred == y_test.to_numpy())

print(f'Accuracy: {test_accuracy}')

