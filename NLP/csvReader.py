#f = open("demofile1.txt", "a") #"a" is append
#for i in range(0,2):
#    s = input(str(i) + ": ")
#    f.write(s+"\n") #"\n" writes to new line
#f.close()

#f = open("demofile1.txt", "r") #"r" is read
#print(f.read()) #entire file
#f.close()

import csv

def load_traindata():
    print("Loading training data...")
    train_x = []
    train_y = []
    with open(r"C:\Users\beast\Desktop\coursework\NLP\trainingData.csv") as file:
        csv_reader = csv.reader(file, delimiter=",")
        for row in csv_reader:
            train_x.append(row[0])
            train_y.append(row[1])
    return [train_x, train_y]

print(load_traindata())