import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from konlpy.tag import Okt
# pip install konlpy
# https://webnautes.tistory.com/1394
from tensorflow.keras.preprocessing.text import *
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.preprocessing import LabelEncoder
from keras.utils import to_categorical
import pickle

pd.set_option('display.unicode.east_asian_width', True)

df = pd.read_csv('./movie_genre_concat_final.csv')

df.dropna(inplace=True)
print(df.head())
print(df.info())

X = df['summary']
Y = df['genre']

# ============= Y에 대한 onehotencoding ===========================
encoder = LabelEncoder()
labeled_Y = encoder.fit_transform(Y)
label = encoder.classes_  # 엔코더가 갖고 있는 변수
print(labeled_Y[0])
print(label)
with open('./models/encoder.pickle', 'wb') as f:
    pickle.dump(encoder, f)

onehot_Y = to_categorical(labeled_Y)
print(onehot_Y)
# ===============================================================

okt = Okt()
# print(type(X))
# okt_morph_X = okt.morphs(X[1], stem=True)
# print(X[1])
# print(okt_morph_X)

for i in range(len(X)):
    X[i] = okt.morphs(X[i], stem=True)

stopwords = pd.read_csv('./crawling/stopwords.csv', index_col=0)
print(stopwords.head())

# 의미 없는 단어 제거
for j in range(len(X)):
    words = []
    for i in range(len(X[j])):
        if len(X[j][i]) > 1 and X[j][i] not in list(stopwords['stopword']):
            words.append(X[j][i])
    X[j] = ' '.join(words)
print(X)

# 단어를 숫자에 대응
token = Tokenizer()
token.fit_on_texts(X)
tokened_X = token.texts_to_sequences(X)
print(tokened_X[:5])

with open('./models/movie_token.pickle', 'wb') as f:
    pickle.dump(token, f)

wordsize = len(token.word_index) + 1
print(wordsize)
print(token.index_word)

# 가장 긴 문장 기준으로 길이 맞추기
Max = 1000
for i in range(len(tokened_X)):
    if Max < len(tokened_X[i]):
        tokened_X[i] = tokened_X[i][:Max]
print(Max)

X_pad = pad_sequences(tokened_X, Max)
print(X_pad[:10])

X_train, X_test, Y_train, Y_test = train_test_split(X_pad, onehot_Y, test_size=0.1)
print(X_train.shape, Y_train.shape)
print(X_test.shape, Y_test.shape)

xy = X_train, X_test, Y_train, Y_test
np.save('./crawling/movie_data_max_{}_wordsize_{}'.format(Max, wordsize), xy)
