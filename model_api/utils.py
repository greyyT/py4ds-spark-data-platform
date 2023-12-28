import re
import string
import numpy as np
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.text import tokenizer_from_json
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
import yaml
import json

with open('./tokenizer.pkl', 'rb') as tokenizer_file:
    tokenizer = pickle.load(tokenizer_file)

def text_preprocessing(text):
    text_clean = []
    translator = str.maketrans(string.punctuation, ' '*len(string.punctuation))
    clean = re.compile(r'<[^>]+>')
    for i, test in enumerate(text):
        tmp_text = test.lower()
        tmp_text = tmp_text.replace('\n', '')
        tmp_text = clean.sub('', tmp_text)
        tmp_text = tmp_text.translate(translator)
        text_clean.append(tmp_text)

    text_clean = np.array(text_clean)

    text = tokenizer.texts_to_sequences(text_clean)
    text = pad_sequences(text, maxlen=100, truncating='post', padding ='post')
    return text