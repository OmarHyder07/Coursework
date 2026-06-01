from SimLogic.classes import *
from NLP.groqCalls import maggroqCall

def getMagdata(data):
    if data["type"] != "None":
        m, q = MQforParticle(data["type"])
    else:
        q = float(data["charge"])
        m = float(data["mass"])
    B = float(data["B"]) # mag flux density 
    vx = float(data["v0"]) #v0 is initial velocity into field
    return m, q, B, vx, 0

def MQforParticle(type):
    # assigns masses and charges based on particle type 
    if type == "electron": return 9.11e-31, -1.60e-19
    if type == "proton": return 1.67e-27, 1.60e-19
    if type == "alpha": return 6.64e-27, 3.2e-19
    if type == "neutron": return 1.67e-27, 0