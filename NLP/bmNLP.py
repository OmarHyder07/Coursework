import re
import string
from NLP.groqCalls import ebmgroqCall

def pre_process(prompt):
    def hasDigits(s):
        return any(chr.isdigit() for chr in s)
    def extract_units(text):
        # Define regex pattern to extract numbers with their units
        pattern = r"(\d+(?:\.\d+)?)\s*([a-z]+[/^-](?:-?\d+|\w+)?)"# Matches numbers followed by units
        return re.findall(pattern, text)  # Returns list of tuples (value, unit)

    def extract_weights(text):
        pattern = r"(\d+(?:\.d+)?)\s*(kg|g|grams|kilos|kilograms)"
        return re.findall(pattern, text)
    
    prompt += " "
    text = []
    word = ""
    for letter in prompt:
        if letter == " ":
            word = word.translate(str.maketrans('', '', string.punctuation))
            split = []
            if hasDigits(word):
                split = extract_units(word)
                if split == []:
                    split = extract_weights(word)
            if split != []:
                text.append(split[0][0])
                text.append(split[0][1])
            else:
                text.append(word)
            word = ""
        else: word += letter
    if prompt[-1] != " ":
        text.append(word)
    return text

def isNumerical(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def findRoots(index, text):
    massRoots = ["mass", "weighing"]
    speedRoots = ["speed", "velocity"]
    for i in range(index, -1, -1):
        previous_word = text[i-1]
        if not isNumerical(previous_word):
            if previous_word in massRoots:
                return "m"
            elif previous_word in speedRoots:
                return "s"
            elif previous_word == "e":
                return "e"
        else: break
    return None

def extractEntity(index, text):
    namedEntities = ["mass", "arrow", "arrows", "velocity",
                     "speed", "weighing", "gravity"]
    entity = ""
    for i in range(index, -1, -1):
        previous_word = text[i-1]
        if previous_word in namedEntities or isNumerical(previous_word):
            break
        else:
            temp = entity
            entity = previous_word + " "
            entity += temp
    
    return entity + text[index]

# m = pre_process("15 particles of mass 20 arrows showing to indicate velocity")
# arrowWords = ["arrow", "arrows", "vectors", "direction"]

from groq import Groq

def parse_prompt(text):
    sim_data = ebmgroqCall(text)
    if sim_data == False:
        print("error with groq calls, using default values for coefficients of restitution.")
        sim_data = {"pCollision_e": 1, "bound_e": 1}
    # Text must be processed for the following non-LLM (regex etc.) methods
    # But the LLM call requires unprocessed text so that is done first. 
    text = pre_process(text)
    groups = []
    current_group = {"particles": 0, "speed": None, "mass": None, "arrows": False}
    first = True
    for i in range(len(text)): #text is a LIST of words
        word = text[i]
        while True:
            if isNumerical(word):
                # print(word)
                # value-unit pairs 
                next_word = text[i+1] if i + 1 < len(text) else None
                if next_word != None:
                    if re.search("([a-z]+[/^-](?:-?\d+|\w+)?)", next_word):
                        current_group["speed"] = (word, next_word)
                        #print(word, " speed")
                        break
                    elif re.match("kg|g|grams|kilos|kilograms", next_word):
                        current_group["mass"] = (word, next_word)
                        #print(word, " mass")
                        break
                # assignes value-type based on found root word
                rootType = findRoots(i, text)
                if rootType != None:
                    # print("root found with number: ", word)
                    if rootType == "m": 
                        current_group["mass"] = (word, None)
                        #print(word, " rooted mass")
                    elif rootType == "s": 
                        current_group["speed"] = (word, None)
                        #print(word, " rooted speed")
                    break
                # if number not speed or mass: assume particle-count
                # if this is NOT the first particle count, don't make a new group.
                if first != True and rootType != "e":
                    if not (current_group["speed"] == None and current_group["mass"] == None):
                        # This is to make sure a random number hasn't been picked up and just assigned to particle count
                        # e.g. --> "20 particles, with arrows on 10 of them, and 14 more"
                        groups.append(current_group)
                        #print(current_group)
                        current_group = {"particles": 0, "speed": None, "mass": None}
                first = False
                current_group['particles'] = int(word)
                #print(word, " particles")
            break
    
    if current_group not in groups:
        groups.append(current_group)
    
    if len(groups) == 1:
        group = groups[0]
        if group["particles"] == 0:
            group["particles"] = 1
        if group["speed"] == None:
            group["speed"] = (100, None)
        if group["mass"] == None:
            group["mass"] = (30, None)
        groups[0] = group
    else:
        for i in range(0, len(groups)):
            group = groups[i]
            if group["particles"] == 0:
                group["particles"] = 10
            if group["speed"] == None:
                group["speed"] = (100, None)
            if group["mass"] == None:
                group["mass"] = (15, None)
            groups[i] = group


    return [groups, sim_data]




