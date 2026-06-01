import spacy
import pickle
import os

def callWV(modelName, x):
    nlp = spacy.load("en_core_web_md")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with open(modelName, "rb") as file:
        model = pickle.load(file)
    input_x = [x]
    input_docs = [nlp(text) for text in input_x]
    input_x_word_vectors = [x.vector for x in input_docs]

    return model.predict(input_x_word_vectors)[0]

def findSimType(x):
    return callWV("svm_simulationClassifier", x)

def classifySHM(x):
    return callWV("shmInputClassifier", x)

def classifyBM(x):
    return callWV("bmInputClassifier", x)

def classifyPP(x):
    return callWV("projectionInputClassifier", x)

def classifyMAG(x):
    return callWV("magInputClassifier", x)