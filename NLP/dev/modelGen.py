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

#pickle.dump(clf_svm_wv.fit(train_x_word_vectors, train_y), file)

import spacy
from sklearn import svm
import pickle
import csv
import os    
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class Category:
    P = "PROJECTION"
    BM = "BMOTION"
    SHM = "SHM"
    UN = "UNDEFINED"

filename = "svm_simulationClassifier"
nlp = spacy.load("en_core_web_md")
#### MODEL CREATING / LOADING IN TRAINING DATA
def build_model():
    print("Loading training data...")
    train_x = []
    train_y = []
    trainingData = input("Which set of data to train with? (include filetype) ")
    with open(trainingData.replace("\\", "/"), 'r') as file:
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            train_x.append(row[0])
            train_y.append(row[1])
    print("Generating model...")
    docs = [nlp(text) for text in train_x]
    train_x_word_vectors = [x.vector for x in docs]  
    # A list, containing 1 vector for each sentance
    clf_svm_wv = svm.SVC(kernel="linear") #fits word vectors to support vector machine
    filename = input("Save model as: ")
    with open(filename, "wb") as file:
        pickle.dump(clf_svm_wv.fit(train_x_word_vectors, train_y), file)
    print("model generated, stored as:", filename)
# fits word vectors to train_y data, effectively making model
####
