import copy
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5 import uic  # ui를 클래스로 바꿔준다.
import pandas as pd
import numpy as np
from konlpy.tag import Okt
from tensorflow.keras.preprocessing.text import *
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from keras.utils import to_categorical
import pickle

# ====================gpu 사용 안하려면========================
import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    # Restrict TensorFlow to only allocate 1GB of memory on the first GPU
    try:
        tf.config.experimental.set_virtual_device_configuration(
            gpus[0],
            [tf.config.experimental.VirtualDeviceConfiguration(memory_limit=1024)])
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Virtual devices must be set before GPUs have been initialized
        print(e)
# ============================================================

form_window = uic.loadUiType('./movie_genre_v2.ui')[0]


class Exam(QMainWindow, form_window):
    def __init__(self):  # 버튼 누르는 함수 처리해 주는 곳
        super().__init__()
        self.setupUi(self)
        self.model = load_model('./models/news_category_classfication_model_0.4605516493320465.h5')
        self.stopwords = pd.read_csv('./crawling/stopwords.csv', index_col=0)
        # 단어를 숫자에 대응
        with open('./models/movie_token2000.pickle', 'rb') as f:
            self.token = pickle.load(f)
        with open('./models/encoder.pickle', 'rb') as f:
            self.encoder = pickle.load(f)
        self.Max = 2000
        self.label = self.encoder.classes_
        self.okt = Okt()
        self.btn_1.clicked.connect(self.str_clear)
        self.btn_2.clicked.connect(self.str_process)
        self.lbl_predict_title = [self.lbl_predict_1, self.lbl_predict_2, self.lbl_predict_3]
        self.action_undo.triggered.connect(self.txt_summary.undo)
        self.action_redo.triggered.connect(self.txt_summary.redo)

    def str_clear(self):
        self.txt_summary.setText('')
        for lbl in self.lbl_predict_title:
            lbl.setText('')

    def str_process(self):
        input_str = self.txt_summary.toPlainText()
        self.str_clear()
        self.txt_summary.setText(input_str)
        print('input str')
        if input_str == '':
            self.lbl_predict_1.setText('내용을 입력하세요')
        else:
            result_str = self.judge_input(input_str)
            for i in range(len(result_str)):
                self.lbl_predict_title[i].setText(result_str[i])

    def judge_input(self, str_temp):
        str_temp = self.okt.morphs(str_temp, stem=True)

        words = []
        for i in range(len(str_temp)):
            if len(str_temp[i]) > 1 and str_temp[i] not in list(self.stopwords['stopword']):
                words.append(str_temp[i])
        str_temp = ' '.join(words)

        tokened_X = self.token.texts_to_sequences([str_temp])
        if self.Max < len(tokened_X): tokened_X = tokened_X[:self.Max]  # 혹시 Max값보다 크면 Max값에 맞춘다.

        X_pad = pad_sequences(tokened_X, self.Max)  # 최대 길이에 맞게 늘려준다.
        pred = self.model.predict(X_pad)
        return self.judge_final(pred)

    def judge_final(self, result_pred):
        result_pred = result_pred[0].tolist()
        list_temp = copy.deepcopy(result_pred)

        list_temp.sort()
        list_temp.reverse()  # 리스트 정렬
        sum_accuracy, coun = 0, 0
        list_genre = []
        for i in list_temp:
            sum_accuracy += i
            coun += 1
            list_genre.append(self.label[result_pred.index(i)] + ' - ' + str(round(i * 100, 2)) + '%')
            if sum_accuracy >= 0.7 or coun == 3: break

        return list_genre


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = Exam()
    mainWindow.show()
    sys.exit(app.exec_())
