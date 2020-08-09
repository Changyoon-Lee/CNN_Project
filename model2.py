

# Commented out IPython magic to ensure Python compatibility.
# %matplotlib inline
import matplotlib.pyplot as plt
import re
from konlpy.tag import Okt
import numpy as np

import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

import functions as fc

from gensim.models import Word2Vec
ko_model= Word2Vec.load('/content/drive/My Drive/ CNN_project/word2vec_movie.model') # word2vec 모델 로드

# train, test 데이터 불러오기
import pickle
import pandas as pd

test = pd.read_pickle("/content/drive/My Drive/ CNN_project/token_test_data.pkl")
train = pd.read_pickle("/content/drive/My Drive/ CNN_project/token_train_data.pkl")

training_sentences, training_labels = train['tokens'], train['labels']
testing_sentences, testing_labels = test['tokens'], test['labels']

vocab_size = 20000
embedding_dim = 200
max_length = 30
truct_type = 'post'
padding_type = 'post'
oov_tok = '<OOV>'

import functions as fc
training_padded = fc.token_padded(training_sentences)
testing_padded = fc.token_padded(testing_sentences)

# making embedding matrix
tokenizer = Tokenizer(num_words=vocab_size, oov_token=oov_tok)
size = len(tokenizer.word_index) + 1
embedding_matrix = np.zeros((size, embedding_dim))

for word, idx in tokenizer.word_index.items():
    embedding_vector = ko_model[word] if word in ko_model else None
    if embedding_vector is not None:
        embedding_matrix[idx] = embedding_vector

embedding_dim = 200
filter_sizes = (3, 4, 5)
num_filters = 100
dropout = 0.5
hidden_dims = 100

batch_size = 50
num_epochs = 10
min_word_count = 1
context = 10

conv_blocks =[]

input_shape = (30)
model_input = tf.keras.layers.Input(shape=input_shape)
z = model_input
for sz in filter_sizes:
    embedding = tf.keras.layers.Embedding(vocab_size, embedding_dim, input_length=max_length,
                                         weights = [embedding_matrix], trainable = False)(z)
    conv = tf.keras.layers.Conv1D(filters=num_filters,
                         kernel_size=sz,
                         padding="valid",
                         activation="relu",
                         strides=1)(embedding)
    conv = tf.keras.layers.GlobalAveragePooling1D()(conv)
    conv = tf.keras.layers.Flatten()(conv)
    conv_blocks.append(conv)
z = tf.keras.layers.Concatenate()(conv_blocks) if len(conv_blocks) > 1 else conv_blocks[0]

z = tf.keras.layers.Dense(hidden_dims, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(0.003), bias_regularizer=tf.keras.regularizers.l2(0.003))(z)
z = tf.keras.layers.Dropout(dropout)(z)
model_output = tf.keras.layers.Dense(1, activation="sigmoid")(z)
model = tf.keras.Model(model_input, model_output)
model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])


import os #폴더 생성
from tensorflow import keras

checkpoint_dir = './ckpt2'
if not os.path.exists(checkpoint_dir):
    os.makedirs(checkpoint_dir)
callbacks = [
    keras.callbacks.EarlyStopping(monitor='val_accuracy', patience=0),   
    keras.callbacks.ModelCheckpoint(
        filepath=checkpoint_dir + '/ckpt2-loss={loss:.3f}',
        save_freq=500)
]
history = model.fit(training_padded, training_labels, epochs=10, callbacks=callbacks, batch_size = batch_size, validation_data=(testing_padded, testing_labels))

plot_graphs(history, 'accuracy',name='model2_accuracy')
plot_graphs(history, 'loss',name='model2_loss')
