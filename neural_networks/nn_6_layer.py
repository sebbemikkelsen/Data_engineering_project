# Neural Network using 6 layers
# Uses 6 features for now
# R2 score of ~0.48

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import Dense
import tensorflow as tf
import tensorflow_addons as tfa
import tensorflow.keras.regularizers as regularizers
from tensorflow import keras
from sklearn.metrics import r2_score

def build_and_compile_six_layer_model(features):
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=(features,)),
        tf.keras.layers.Dense(18, activation='relu'),
        tf.keras.layers.Dense(36, activation='relu'),
        tf.keras.layers.Dense(72, activation='relu'),
        tf.keras.layers.Dense(144, activation='relu'),
        tf.keras.layers.Dense(72, activation='relu'),
        tf.keras.layers.Dense(36, activation='relu'),
        tf.keras.layers.Dense(18, activation='relu'),
        tf.keras.layers.Dense(1)
    ])
    model.compile(
        loss=tf.keras.losses.MeanSquaredError(),
        optimizer=tf.keras.optimizers.Adam(),
        metrics=[tfa.metrics.RSquare()])
    return model


def main():
    # LOAD DATA AND PROPROCESSING
    df = pd.read_csv('top_repos.csv')

    # Drop all entrys with nan
    df = df.dropna(axis=0)

    # Split dataset
    y = df['Stargazers']
    X = df.drop('Stargazers', axis=1)
    X = X.drop('Name', axis=1)
    
    if 'Language' in X.columns:
        category_mapping = {category: index for index, category in enumerate(
            X['Language'].unique())}

        X['Language'] = X['Language'].map(category_mapping)

    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)




    # NORMALIZING THE DATA
    scaler = MinMaxScaler()
    scaler.fit(X_train)

    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)



    # MODEL CREATION

    def r2_metric(y_true, y_pred):
        return r2_score(y_true, y_pred)

    # Model - Layers
    model = keras.Sequential([
        keras.layers.Dense(18, activation='relu', input_shape=(X_train.shape[1],), kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=0.01)),
        keras.layers.Dense(36, activation='relu', kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=0.01)),
        keras.layers.Dense(72, activation='relu', kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=0.01)),
        keras.layers.Dense(36, activation='relu', kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=0.01)),
        keras.layers.Dense(9, activation='relu', kernel_regularizer=regularizers.l1_l2(l1=0.01, l2=0.01)),
        keras.layers.Dense(1)
    ])

    # Training
    model.compile(optimizer='adam', loss='mean_squared_error')
    model.fit(X_train, y_train, epochs=500, batch_size=32)

    # Evaluation
    y_pred = model.predict(X_test)
    r2 = r2_metric(y_test, y_pred)
    print("R2 Score:", r2)

if __name__ == '__main__':
    main()