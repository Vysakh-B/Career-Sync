import nltk
import numpy as np
nltk.download('punkt')

from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
# Initialize stemmer
stemmer = PorterStemmer()

# Tokenization function
def tokenize(sentence):
    return word_tokenize(sentence)

# Stemming function
def stem(word):
    return stemmer.stem(word.lower())
def bag_of_words(tokenized_sentence,all_words):
    tokenized_sentence = [stem(w) for w in tokenized_sentence]
    bag = np.zeros(len(all_words),dtype=np.float32)
    for idx, w in enumerate(all_words):
        if w in tokenized_sentence:
            bag[idx]=1.0

    return bag

