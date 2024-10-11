import spacy 

def getParticleCount(prompt):
    nlp = spacy.load("en_core_web_md")

    doc = nlp(prompt)
    for token in doc:
        if token.ent_type_ in ["QUANTITY", "CARDINAL"]:
            return int(token.text)

import re

pattern = r'''
    (\d+) # no. particles
    \s+ # white space
    particles # "particles"
    (?:\s+(?:of|with|moving)?)? 
    # for refference above pattern means it's fully optional
    # and within that is either "of", "with" or "moving"
    \s+
    (?:a\s+)? 
    (?:speed\s+)? 
    (?:of\s+)? 
    # the reason to have words like speed here,
    # is so they will not be flagged as the adjective.
    (
    \w+ # one or more letters (word: quick, slow, etc.)
    |
    # (?:\.d+) allows a decimal
    \d+[a-z]+[/^]?[-]?(?:\d+|\w+)?
    )
    '''


units = r"\d+[a-z]+[/^]?[-]?(?:\d+|\w+)?"

def getData(prompt):
    p = r"(\d+\s+particle(?:s)?)\s+(?:\D+)*(\d+[a-z]+[/^]?[-]?(?:\d+|\w+)?|\w+)"
    match = re.findall(p, prompt)
    if match:
        print("matched")
        m = [d for d in match]
        data = []
        for d in m:
           print(d.group())
           data.append([int(re.search("\d+", d[0])), int(re.search("\d+", d[1]))])
        return m
    return None
    
#print(getData("and 18 particles of 8kmhs")) #and 2 particles of 6kmh
