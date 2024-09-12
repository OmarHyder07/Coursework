# alternative to bag of words
# captures semantic meaning of words 
# by converting them to a vector
# uses neural network that's trained already 

# pip install -U scikit-learn
# python -m spacy download en_core_web_md

# from testing it seems when the model is not too sure which scenario to spec into;
# it just chooses the last scenario in train_y.
# AND when there is a low amount of training data;
# and a test input is redundant, it will define it based on similiar language constructs;
# e.g. the idea of plurality (such, very, lots) will spec into brownian motion.

# LIMITATIONS
# since it averages all word vectors together for a sentance, meaning can be obscured.
# homonyms will have the same word vector

# Model making:
# CSV file which takes in inputted sentances 
# predicts category
# you input which category it actually is

import spacy
from sklearn import svm

class Category:
    P = "PROJECTION"
    BM = "BMOTION"
    SHM = "SHM"
    UN = "UNDEFINED"

nlp = spacy.load("en_core_web_md")
#### MODEL CREATING / LOADING IN TRAINING DATA
#  takes all individual word embeddings and averages them into one vector
def train_model(train_x, train_y):
    print("Generating model...")
    docs = [nlp(text) for text in train_x]
    train_x_word_vectors = [x.vector for x in docs] 
    # A list, containing 1 vector for each sentance

    clf_svm_wv = svm.SVC(kernel="linear")
    return clf_svm_wv.fit(train_x_word_vectors, train_y)
# fits word vectors to train_y data, effectively making model
####

from filewritingtest import load_traindata
def load_model():
    traindata = load_traindata()
    p = train_model(traindata[0], traindata[1])
    print("Model generated")
    return p

def train():
    model = load_model()
    cont = True
    while cont == True:

        print("Test sentance:")
        s = input()

        test_x = [s]
        test_docs = [nlp(text) for text in test_x]
        test_x_word_vectors = [x.vector for x in test_docs]

        print("Is the test sentance:")
        print(model.predict(test_x_word_vectors))
        print("P, BM, SHM, UN?")
        type = input()

        f = open("demofile1.csv", "a")
        match type:
            case "P":
                type = Category.P
            case "BM":
                type = Category.BM
            case "SHM":
                type = Category.SHM
            case "UN":
                type = Category.UN

        f.write("\n" + s +", " + type)
        f.close()

        q=input("continue? (y/n)")
        if q != "y":
            cont = False 
        else:
            retrain = input("retrain model? ")
            if retrain == "y":
                model = load_model()


def guess(x, model):
    test_x = [x]
    test_docs = [nlp(text) for text in test_x]
    test_x_word_vectors = [x.vector for x in test_docs]

    return model.predict(test_x_word_vectors)[0]


