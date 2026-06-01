import math
from SimLogic.classes import Vector
import re
from SimLogic.classes import *
from text.Projectioncall import *

def isNumerical(s):
    #Used to determine if a value is "None" or an actual number
    pattern = r"(\d+(?:\.d+)?)"
    s = re.search(pattern, s)
    if s != None:
        s = s[0]
    try:
        float(s)
        return True
    except ValueError:
        return False
    except TypeError:
        return False

def getVelocities(data, bound_size):
    #Determines which equations to use based on which values have been inputted
    output = {"v": None, "h": None, "va": -9.81, "ha": 0, "startH": 0, "scalar": 1}
    if isNumerical(data["speed"]) and isNumerical(data["theta"]): # speed and angle to horizontal given
        print("u and theta")
        output["v"] = float(data["speed"]) * math.sin(math.radians(float(data["theta"])))
        output["h"] = float(data["speed"]) * math.cos(math.radians(float(data["theta"])))
    elif isNumerical(data["v"]["u"]) and isNumerical(data["h"]["u"]): #vertical and horizontal components given
        output["v"] = float(data["v"]["u"])
        output["h"] = float(data["h"]["u"])
    elif isNumerical(data["v"]["u"]) and isNumerical(data["theta"]): #vertical component and angle given
        output["v"] = data["v"]["u"]
        output["h"] = data["v"]["u"] / math.tan(math.radians(float(data["theta"])))
    elif isNumerical(data["h"]["u"]) and isNumerical(data["theta"]): #horizontal component and angle given
        output["h"] = data["h"]["u"]
        output["v"] = data["h"]["u"] * math.tan(math.radians(float(data["theta"])))
    elif isNumerical(data["theta"]) and isNumerical(data["v"]["maxS"]): #angle and max height given
        print("theta and max height")
        # This will always assume the max height reached is total maximum above h=0. so if it starts at h=10m and reaches a max height of h=25m, it has travelled 15m up.
        if data["startH"] != "None": 
            maxHeight = data["v"]["maxS"] - data["startH"]
        else:
            maxHeight = data["v"]["maxS"]
        u = math.sqrt((2*data["v"]["a"]*maxHeight)/((math.sin(math.radians(data["theta"])))**2))
        output["v"] = u * math.sin(math.radians(data["theta"]))
        output["h"] = u * math.cos(math.radians(data["theta"]))
    elif isNumerical(data["speed"]) and isNumerical(data["v"]["maxS"]): #speed and max height given
        print("max height and speed")
        try:
            theta = math.asin(math.sqrt(abs((-2*float(data["v"]["a"])*float(data["v"]["maxS"]))/(float(data["speed"]))**2)))
            data["theta"] = theta
        except:
            return False
        output["v"] = float(data["speed"]) * math.sin(theta)
        output["h"] = float(data["speed"]) * math.cos(theta)

    output["va"] = float(data["v"]["a"])   
    if data["h"]["a"] == "None": ha = 0
    else: ha = data["h"]["a"]
    output["ha"] = float(ha)
    if data["startH"] != "None": output["startH"] = float(data["startH"])

    #### CHANGE SIGNS OF THINGS...
    #### if we assume any positive values are upwards and to the right:
    if output["va"] < 0:
        output["va"] *= -1
    if output["h"] < 0:
        output["h"] *= -1
    
    velocity = Vector(output["h"], -output["v"])
    acceleration = Vector(output["ha"], output["va"])

    #### Find amount to scale the velocity and acceleration by to make sure the motion fits the boundary
    #### NEED TO WORK SIGNS OUT BEFORE THIS POINT!!
    if isNumerical(data["v"]["maxS"]):
        maxHeight = float(data["v"]["maxS"])
    else:
        maxHeight = ((output["v"])**2)/(2*output["va"])
    if isNumerical(data["h"]["maxS"]):
        range = float(data["h"]["maxS"])
    else:
        print("calculating range")
        # timeToMaxHeight = (-output["v"] + math.sqrt(((output["v"])**2)+2*output["va"]*maxHeight)) / output["va"]
        timeToMaxHeight = (output["v"]) / output["va"]
        timeOfFlight = timeToMaxHeight * 2
        range = output["h"] * timeOfFlight + 0.5 * output["ha"] * (timeOfFlight**2)


    print("range: ", range)
    print("max height: ", maxHeight)
    
    print("velocity: ", velocity)
    print("acc: ", acceleration)

    return {"velocity": velocity, "acceleration": acceleration, "startH": output["startH"], "pxWidth": bound_size["width"]}

def getProjectionData(prompt, window_size):
    data = ppgroqCall(prompt) #calls groq LLM 
    if data == False:
        return 0
    print("window size: ", window_size)
    data = getVelocities(data, window_size)
    if data == False:
        return 1
                                     
    # instantiates particle object and sets it's properties based on prompt
    particle = Particle(20, (0,0,0), 2, 0, 0)
    particle.s = Vector(data["startH"] + particle.radius, window_size["height"] - particle.radius)
    particle.vel = data["velocity"]
    particle.acc = data["acceleration"]
    particle.radius = 5
    print("vertical height: ", window_size["height"])
    print("horizontal width: ", window_size["width"])
    print("starting particle position: ", particle.s)
    print("starting velocity: ", particle.vel)
    print("starting acceleration: ", particle.acc)

    return [particle, data]