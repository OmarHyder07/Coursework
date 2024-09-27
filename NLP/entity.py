import spacy 

def getParticleCount(prompt):
    nlp = spacy.load("en_core_web_md")

    doc = nlp(prompt)
    for token in doc:
        if token.ent_type_ in ["QUANTITY", "CARDINAL"]:
            return int(token.text)
