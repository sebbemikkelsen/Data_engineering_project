from celery import Celery

from numpy import loadtxt
import numpy as np
import pandas as pd
import tensorflow as tf
import tensorflow_addons as tfa
from sklearn.preprocessing import StandardScaler

model_file = 'model'
data_file = './top_repos.csv'

def load_data():
    df = pd.read_csv(data_file)
    y = df['Stargazers']
    X = df.drop('Stargazers', axis=1)

    scaler = StandardScaler()
    scaler.fit(X)
    X = scaler.transform(X)

    y = y.to_numpy()

    return X, y

def load_model():
    # load json and create model
    model = tf.keras.saving.load_model(model_file)
    #print("Loaded model from disk")
    return model

# Celery configuration
CELERY_BROKER_URL = 'amqp://rabbitmq:rabbitmq@rabbit:5672/'
CELERY_RESULT_BACKEND = 'rpc://'
# Initialize Celery
celery = Celery('workerA', broker=CELERY_BROKER_URL,
                backend=CELERY_RESULT_BACKEND)


@celery.task()
def add_nums(a, b):
   return a + b

@celery.task
def get_predictions():
    results = {}
    X, y = load_data()
    loaded_model = load_model()
    predictions = np.round(loaded_model.predict(X)).flatten().astype(np.int32)
    results['y'] = y.tolist()
    results['predicted'] = predictions.tolist()
    #print ('results[y]:', results['y'])
    # for i in range(len(results['y'])):
    #print('%s => %d (expected %d)' % (X[i].tolist(), predictions[i], y[i]))
    # results['predicted'].append(predictions[i].tolist()[0])
    # print('results:', results)

    return results

@celery.task
def get_accuracy():
    X, y = load_data()
    loaded_model = load_model()
    loaded_model.compile(loss='mse', optimizer='adam',
                         metrics=[tfa.metrics.RSquare()])
    score = loaded_model.evaluate(X, y, verbose=0)
    #print("%s: %.2f%%" % (loaded_model.metrics_names[1], score[1]*100))
    return score[1]
