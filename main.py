# TO RUN:
# ON COMPUTER: flask --app appname run (--debug)
# ON NETWORK: flask run --host=0.0.0.0
# end: ctrl+c in terminal
# change port:
# flask run -p (5001)
from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit
from NLP.callWordVectorModel import *
from NLP.bmNLP import parse_prompt
from NLP.groqCalls import *
import time
import os
from SimLogic.particlesim import *
from SimLogic.projectionSim import *
from SimLogic.magSim import *

#Create instance of flask application
#__name__ tells instance which module is being used
app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///prompts.db"
db = SQLAlchemy(app) #Databse 
socketio = SocketIO(app) #Creates instance of socketio, allowing me to use Web Sockets

# Class of objects which are compatible with sqlalchemy
# Each object is a record and each property is a column
class Prompts(db.Model): 
    __tablename__ = "parent_prompts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True) #Primary key
    type = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String(200), nullable=False)

    # Creates relationship between parent prompt and child prompts
    # Properties set so if the parent prompt is delted, all child prompts are too (doens't leave any orphans)
    children = db.relationship('ChildPrompts', backref='parent', cascade="all, delete, delete-orphan")


    def __repr__(self): # Returns string, __repr__ method allows the use of print(prompts object)
        return self.text
    
class ChildPrompts(db.Model):
    __tablename__ = "child_prompts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True) #Primary key
    parent_id = db.Column(db.Integer, db.ForeignKey('parent_prompts.id'), nullable=False) #Foreign key (parent's id)
    text = db.Column(db.String(200), nullable=False)
    
# Code below is for initialising db
os.chdir(os.path.dirname(os.path.abspath(__file__))) # Sets absolute filepath to where main file is located (root of project folder)
with app.app_context():
    db.create_all()

def add_child_prompt(parent_id, prompt):
    child = ChildPrompts(parent_id=parent_id, text=prompt)
    db.session.add(child)
    db.session.commit()

def get_child_prompts():
    parent = Prompts.query.order_by(Prompts.id.desc()).first() #Queries all prompts, and selects the one with the largest id (latest inputted prompt)
    children = [parent.text] #Includes the parent prompt (so the dropdown menu has it as well as child prompts)
    for child in parent.children:
        children.append(child.text)
    return children #Put child prompts into a list for ease of use on frontend

def redirectToNewSim(type, num):
    if num != None: #num used for specific error codes so non-error redirects don't need a num value
        type += "/"+num
    if type in ["BMOTION", "PROJECTION", "SHM", "MAG", f"ERROR/{num}"]:
        emit("disconnect", f"http://localhost:5000/{type}")
    else: #only case if type==Undefined
        emit("disconnect", "http://localhost:5000/")

def addToDB(text, type):
    dbPromptLine = Prompts(type=type, text=text)
    db.session.add(dbPromptLine)
    db.session.commit()

def addChildToDB(text, parent_id):
    dbPromptLine = ChildPrompts(parent_id=parent_id, text=text)
    db.session.add(dbPromptLine)
    db.session.commit()

#.route decorator below, converts function's return value into a HTTP response
#this will be displayed on the web browser;
#'/' passed in value - function responds to web requests for the URL / (main URL)
@app.route('/', methods=["POST", "GET"]) #HTML methods
def index():
    if request.method == "POST": # true when home textarea form is sending the prompt to backend
        prompt = request.form["content"] # Extracts prompt text from POST method 
        type = findSimType(prompt)
        type = type.replace(" ", "") #CSV file has spaces in it for the sake of readability but this needs to be removed for formatting
        new_prompt = Prompts(type=type, text=prompt)
        try:
            db.session.add(new_prompt)
            db.session.commit()
            if type in ["BMOTION", "PROJECTION", "SHM", "MAG"]:
                return redirect(f"/{type}")
            else:
                return redirect("/")
        except:
            return "There was an issue adding your task"
    else: # true when just loading home.html, without sending anything back
        prompts = Prompts.query.all() 
        return render_template("home.html", prompts=prompts)

@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Prompts.query.get_or_404(id) #returns error if no there is no record with this id
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/') #goes back home
    except:
        return "There was a problem deleting that task"
    
@app.route('/resimulate/<int:id>')
def resimulate(id):
    prompt_to_resimulate = Prompts.query.get_or_404(id)
    PromptCopy = Prompts(type=prompt_to_resimulate.type, text=prompt_to_resimulate.text, children=prompt_to_resimulate.children)
    #copies prompt so when the original is deleted can re-add the copy
    delete(id) 
    # Delete prompt so that it can be stored again (so it's outputted at the end of the table)
    # and all queries for simulation prompts get the last enterred prompt so this makes sure resimulation uses the correct prompt
    try:
        db.session.add(PromptCopy)
        db.session.commit()
        return redirect(f'/{PromptCopy.type}')
    except:
        return "There was a problem resimulating this prompt"

@app.route("/ERROR/<int:id>")
def error(id):
    print(id)
    # error id number is the index value for the error messages list
    errorMessages = ["There is an error calling the GroqCloud LLM.",
                     "The data you have inputted is not mathematically possible for projection."]
    return render_template("errorPage.html", errorMessage=errorMessages[id])

# ================================================================

@app.route("/BMOTION") #renders brownianMotion.html when redirected to /BMOTION
def BMsim():
    return render_template("brownianMotion.html", childPrompts=get_child_prompts())

# script for brownianMotion.html emits a message via websocket to run the stream function
@socketio.on("request_particle_data")
def stream():
    # global variables used so can use self-contained functions to handle data being sent from the front end and use the data here
    global newPrompt
    global window_size
    global confirmNewPrompt
    confirmNewPrompt = False
    global connected

    # Extracts last inputted record from database
    latest_record = Prompts.query.order_by(Prompts.id.desc()).first()
    data = parse_prompt(latest_record.text) #extracts data from prompt
    pdata = data[0] 
    simdata = data[1]
    
    # print(pdata)
    # print(simdata)
    dt = 1/60 
    particles = []

    i = 1
    for group in pdata:#Instantiates particles based on prompt
        for _ in range(int(group["particles"])):
            mass = int(group["mass"][0])
            speed = int(group["speed"][0])
            p = Particle(mass=mass, radius=mass, vel=Vector(speed, i*speed), acc=Vector(0,0), s=Vector(random.randint(0, int(window_size["width"])-50),random.randint(0, int(window_size["height"])-50)), isAir=0)
            i = -i
            particles.append(p)
    for _ in range(200):#Instantiates 200 air particles for simulation
        particles.append(Particle(radius=2, mass=5, acc=Vector(0,0), s=Vector(random.randint(0, int(window_size["width"])-50),random.randint(0, int(window_size["height"])-50)), isAir=1, vel=Vector(250, i*250), isInvisible=0))
        i = -i
    type = None #Used for redirection when websocket (simulation) closed, None so default redirect is to the home page
    arrows = 1 #arrows displayed by default
    while connected:
        qtree = generateQuadtree(window_size, particles)
        data = [] #list of lists containing frame data for each particle
        for p in particles:
            updateParticle(p, dt)
            p.boundaryCheck(window_size, simdata["bound_e"]) 
        for p in particles:
            checkCollisions(p, qtree, dt, simdata["pCollision_e"])
            data.append([p.s.vect[0], p.s.vect[1], p.radius, p.isInvisible, str(int(p.vel.modulus())), p.vel[0], p.vel[1], arrows, p.isAir])
        #above calculates frame data

        emit("particle_data", data) #sends frame data to backend
        
        if confirmNewPrompt:
            type = classifyBM(newPrompt["text"]) 
            type = type.replace(" ", "")
            if type == "OTHER": 
                prompt = newPrompt["text"]
                type = findSimType(prompt)
                type = type.replace(" ", "")
                try:
                    addToDB(prompt, type )
                except:
                    print("Unable to process prompt")
                    type = None #Redirects home if there is an error with db
                connected = False
            else:
                if type == "addAIR":
                    for _ in range(50):
                        particles.append(Particle(radius=2, mass=5, acc=Vector(0,0), s=Vector(random.randint(0, int(window_size["width"])-50),random.randint(0, int(window_size["height"])-50)), isAir=1, vel=Vector(250, i*250), isInvisible=0))
                        i = -i
                elif type == "removeAIR":
                    # if the particles list isn't reversed,
                    # when an item is removed the indexes are changed in the list 
                    # but not on iterated over items, 
                    # and it skips every other item, only halving the air not removing all
                    for p in reversed(particles):
                        if p.isAir == 1:
                            particles.remove(p)
                elif type == "nARROWS": arrows = 0
                elif type == "pARROWS": arrows = 1
                elif type == "addG": #adds gravity
                    for p in particles:
                        p.acc.vect[1] = 98.1
                elif type == "removeG": #removes gravity
                    for p in particles:
                        p.acc.vect[1] = 0
                elif type == "AddSlowMo": dt=1/200
                elif type == "NoSlowMo": dt=1/60
                elif type == "addParticles":
                    data = parse_prompt(newPrompt["text"])
                    pdata = data[0]
                    simdata = data[1]
                    print(pdata)
                    i = 1
                    for group in pdata:
                        for _ in range(int(group["particles"])):
                            mass = int(group["mass"][0])
                            speed = int(group["speed"][0])
                            p = Particle(mass=mass, radius=mass, vel=Vector(speed, i*speed), acc=Vector(0,0), s=Vector(random.randint(0, int(window_size["width"])-50),random.randint(0, int(window_size["height"])-50)), isAir=0)
                            i = -i
                            particles.append(p)
                
                #stores prompts made during simulation as a child prompt of the parent prompt
                add_child_prompt(latest_record.id, newPrompt["text"])
                emit("update_dropdown", newPrompt["text"])
                
            print(type)
            confirmNewPrompt = False 

        time.sleep(1/60) #sets frame-rate
    
    redirectToNewSim(type, num=None)

# ================================================================

@app.route("/PROJECTION") #renders projection.html when redirected to /PROJECTION
def Project():
    return render_template("projection.html", childPrompts=get_child_prompts())

# script for projection.html emits a message via websocket to run the p_stream function
@socketio.on("request_projection_data")
def p_stream():
    global window_size 
    global connected
    global confirmNewPrompt
    confirmNewPrompt = False
    #gets latest prompt 
    latest_record = Prompts.query.order_by(Prompts.id.desc()).first()
    data = getProjectionData(latest_record, window_size)
    if data == 0 or data == 1: # 0 or 1 error codes (0: LLM API error, 1: mathematical/physics error)
        type = "ERROR"
        num = data
        connected = False
    else:
        num = None
        particle = data[0]
        simData = data[1]
        width = 200
        scalar = simData["pxWidth"] / width #pixel-to-meter ratio so animation canvas represents 200 meters (200 is default, can be changed)
        dt = 1/60 #frame rate
        arrows = 1

    while connected:
        #sends frame data to frontend
        heightInMeters = window_size["height"] / scalar
        emit("projection_data", [particle.s[0], particle.s[1], particle.radius, particle.vel[0], particle.vel[1], arrows, str(float(width)), str(heightInMeters)])
        emit("displayData", ["x: "+str(round(particle.s[0]/scalar,2)), "y: "+str(round(heightInMeters-particle.s[1]/scalar,2)),"vx: "+str(round(particle.vel[0],2)), "vy: "+str(round(particle.vel[1],2)), "ax: "+str(round(particle.acc[0],2)), "ay: "+str(round(particle.acc[1],2))])

        if particle.s.vect[1] > window_size["height"]:  #if particle collides with ground, it goes stationary
            emit("displayData", ["x: "+str(round(particle.s[0]/scalar,2)), "y: 0","vx: 0", "vy: 0", "ax: 0", "ay: 0"])
        else: #update particle position
            particle.updateVelocity(dt)
            particle.updatePosition(dt*scalar)
        if confirmNewPrompt:
            type = classifyPP(newPrompt["text"])
            type = type.replace(" ", "")
            if type == "OTHER": #other simulation type to redirect to
                prompt = newPrompt["text"]
                type = findSimType(prompt)
                type = type.replace(" ", "")
                try:
                    addToDB(prompt, type)
                except:
                    print("Unable to process prompt")
                    type = ""
                connected = False
            else:
                if type == "nARROWS": arrows = 0 #removes displayed arrows
                elif type == "pARROWS": arrows = 1 #adds displayed arrows
                elif type == "AddSlowMo": dt=1/200
                elif type == "NoSlowMo": dt=1/60
                elif type == "PROJECTION": #new particle projection inputted
                    newData = getProjectionData(newPrompt["text"], window_size)
                    particle = newData[0]
                elif type == "changeWidth": #changes width of animation area
                    width = convertUnit("length", "meters", newPrompt["text"])
                    if width == False: print("Error tying to change width")
                    else: width = float(width)
                    #calculating new scalar 
                    temp = scalar
                    newScalar = data[1] / width
                    newScalar = newScalar / temp
                    scalar = newScalar
                    particle.s.vect[0] = particle.s.vect[0] * scalar
                    #y-value (s.vect[1]) has to be calculated this way as HTML canvas coordinates are from the top left corner
                    #so if this isn't done and the scalar is 2, it will double the x-values but halve the y-values
                    particle.s.vect[1] = window_size["height"] - ((window_size["height"] - particle.s.vect[1])*scalar)
                    emit("widthChange", scalar) #sends news scalar to frontend
                
                #stores prompts made during simulation as a child prompt of the parent prompt
                add_child_prompt(latest_record.id, newPrompt["text"])
                emit("update_dropdown", newPrompt["text"])

            print(type)
            confirmNewPrompt = False

        time.sleep(1/60) #sets frame-rate
    
    redirectToNewSim(type, num)

# ================================================================

@app.route("/SHM") #renders SHM.html when redirected to /SHM
def SHM():
    return render_template("SHM.html", childPrompts=get_child_prompts())

#script for SHM.html emits a message via websocket to run the shm_stream function
@socketio.on("request_SHM_data")
def shm_stream():
    # values to determine if calculations for velocity or acceleration time or energy graphs 
    global isvtGraph
    global isatGraph
    global isenergyGraph
    isvtGraph = 0
    isatGraph = 0
    isenergyGraph = 0

    global window_size 
    global connected
    global confirmNewPrompt
    confirmNewPrompt = False
    latest_record = Prompts.query.order_by(Prompts.id.desc()).first() #gets latest prompt 

    data = shmgroqCall(latest_record)
    if data == False: # if there is an error with LLM API
        type = "ERROR"
        num = 0
        connected = False
    else:
        print(data)
        mass = float(data["mass"])
        k = float(data["k"]) #spring constant
        amplitude = float(data["amplitude"])

        dt = 1/60
        omega = math.sqrt(k/mass) #angular frequency
        t = 0
        v = 0
        x=0
        mOutput = str(mass) + "kg"
        #wether or not to display velocity and acceleration arrows
        displayV = 1
        displayA = 1 
        #values for redirection when simulation closed
        type = None
        num = None

    while connected:
        xOutput = "x = " + str(round(-x, 2)) + "m"
        a = - omega**2 * x #acceleration
        emit("SHM_data", [x,v, a, displayV, displayA, mOutput, xOutput])
        x = amplitude * math.cos(omega*t) #position
        v = -amplitude * omega**2 * math.sin(omega*t) #velocity
        
        t += dt 
        
        if confirmNewPrompt:
            type = classifySHM(newPrompt["text"])
            type = type.replace(" ", "")
            if type == "OTHER":
                prompt = newPrompt["text"]
                type = findSimType(prompt)
                type = type.replace(" ", "")
                try:
                    addToDB(prompt, type)
                except:
                    print("Unable to process prompt")
                    type = ""
                connected = False
            else:
                if type == "removeVel": displayV = 0 #removes velocity arrows
                elif type == "addVel": displayV = 1 #adds velocity arrows
                elif type == "removeAcc": displayA = 0 #removes acceleration arrows
                elif type == "addAcc": displayA = 1 #adds acceleration arrows
                elif type == "changeMass":
                    newMass = convertUnit("mass", "kilograms", newPrompt["text"]) #ensures mass in prompt is in kilograms
                    if newMass == False: print("Error tying to change mass") #if there is an error with LLM API
                    else: 
                        mass = float(newMass)
                        mOutput = str(mass) + "kg"
                elif type == "changeK":
                    newK = convertUnit("spring constant", "Newtons per meter", newPrompt["text"]) #ensures spring constant is in N/m
                    if newK == False: print("Error tying to change spring constant")
                    else: k = float(newK)
                elif type == "changeAmplitude":
                    newAmplitude = convertUnit("length", "meters", newPrompt["text"]) #ensures amplitude is in m
                    if newAmplitude == False: print("Error tying to change amplitude")
                    else: amplitude = float(newAmplitude)
                elif type == "AddSlowMo": dt=1/200
                elif type == "NoSlowMo": dt=1/60
                elif type == "vtGRAPH": emit("vtGraph") #emits message to create a v-t graph
                elif type == "atGRAPH": emit("atGraph") #emits message to create an a-t graph
                elif type == "energyGRAPH": emit("energyGraph")   #emits message to create an energy graph

                #stores prompts made during simulation as a child prompt of the parent prompt
                add_child_prompt(latest_record.id, newPrompt["text"])
                emit("update_dropdown", newPrompt["text"])

            print(type)
            confirmNewPrompt = False

        if isvtGraph == 1 or isatGraph == 1: #calculates data for v-t or a-t graphs
            aOutput = "a = " + str(round(a,2)) + "ms^-2"
            vOutput = "v = " + str(round(v, 2)) + "ms^-1"
            tOutput = "t = " + str(round(t, 2)) + "s"
            emit("displayVTATGraph", [isvtGraph, isatGraph, v, a, tOutput, vOutput, aOutput])
        if isenergyGraph == 1: #calculates data for energy graph
            totalEnergy = 0.5*k*(amplitude**2)
            ke = 0.5 * mass * (omega**2)*((amplitude**2)-(x**2)) 
            pe = 0.5 * k * (x**2)
            emit("displayEnergy", [ke, pe, t, totalEnergy])
        
        time.sleep(1/60) #sets frame rate
    
    redirectToNewSim(type, num)

# changes global variable so ongoing simulation function can access the message to create an energy graph
@socketio.on("energy_graph_made")
def confirmEnergyGraph():
    global isenergyGraph
    print("energy graph")
    isenergyGraph = 1 

# ================================================================

@app.route("/MAG") #renders mag.html when redirected to /MAG
def mag():
    return render_template("mag.html", childPrompts=get_child_prompts())

#script for mag.html emits a message via websocket to run the mag_stream function
@socketio.on("request_mag_data")
def mag_stream():
    global window_size 
    global connected
    global confirmNewPrompt
    confirmNewPrompt = False
    #gets latest prompt
    latest_record = Prompts.query.order_by(Prompts.id.desc()).first()
    data = maggroqCall(latest_record)
    if data == False: #LLM API error
        type = "ERROR"
        num = 0
        connected = False
    else:
        m, q, B, vx, vy = getMagdata(data)
        x, y = 0, window_size["height"]/2 #inisialises particle position to the left and in the middle of the screen
        
        if data["type"] != "neutron": #since q=0 for neutrons, would create a math error with calculating the Lamor radius
            isNeutron = False
            radius = (m*vx) / (abs(q*B)) 
            print("theoretical radius: ", radius)
            if radius < 1e-4: #sets time slow-down factor based on how big the Lamor radius is (for the sake of animation)
                dt = 1e-13
                initialdt = dt*100
            else:
                dt = 1e-10
                initialdt = dt/10
            visualScale = window_size["height"]/(6*radius) #scalar to make the height of canvas 6*radius of particles motion arc
        else: 
            isNeutron = True
            visualScale = 1
            dt = 1e-11
            initialdt = dt
            radius = 1
            #default simulation values for neutrons

        print("mass: ", m)
        print("q", q)
        print("B", B)
        print("v0", vx)
        emit("displayData", ["mass: " + str(m),  "charge: " + str(q), "B: " + str(B), "v0: " + str(vx)])

        #initialises particle data
        v = Vector(5e11, vy) #This velocity is for the sake of animation, and will be changed later to reflect data in the prompt
        s = Vector(x,y)
        a=Vector(0,0)
        F = Vector(0,0)        
        
        type = None 
        num = None
        alreadyEnteredField = False 
    while connected:
        if s.vect[0] > 1*window_size["width"]/16:
            if alreadyEnteredField == False and isNeutron == False:
                v = Vector(vx, vy) #sets velocity to actual velocity from prompt data
                alreadyEnteredField = True 
            F = Vector(q*v.vect[1]*B, -q*v.vect[0]*B) #calculates magnetic force on particle
            a = F.scalarX(1/m) #calculates acceleration
            v = v.sum(a, dt) #calculates velocity
            s = s.sum(v, dt*visualScale) #calcultes new position
        else: 
            if alreadyEnteredField: s = s.sum(v, dt*visualScale) #ensures particle leaves magnetic field with the same velocity 
            else: s = s.sum(v, initialdt)

        #sends frame-data to frontend to be animated
        #velocity and acceleration normalised (unit vectors) and then multipled by 50 to make them have a length of 50
        #this is necessary for drawing arrows as their true magnitudes will be very, very large and therefore offscreen
        emit("mag_data", [s[0],s[1], B, radius, v.unit().scalarX(50).vect, a.unit().scalarX(50).vect]) 
        time.sleep(1/50) #sets frame rate

        if confirmNewPrompt:
            type = classifyMAG(newPrompt["text"]) #word-vector model for classifying prompts inputted during a magnetic fields simulation
            type = type.replace(" ", "")
            if type == "OTHER":
                prompt = newPrompt["text"]
                type = findSimType(prompt)
                type = type.replace(" ", "")
                try:
                    addToDB(prompt, type )
                except:
                    print("Unable to process prompt")
                    type = ""
                connected = False
            else:
                if type == "newParticle":
                    data = maggroqCall(newPrompt["text"])
                    if data == False:
                        type = "ERROR"
                        num = 0
                        connected = False
                    else:
                        if data["type"] != "neutron":
                            isNeutron = False
                            radius = (m*vx) / (abs(q*B)) 
                            print("theoretical radius: ", radius)
                            if radius < 1e-4: #sets time slow-down factor based on how big the Lamor radius is (for the sake of animation)
                                dt = 1e-13
                                initialdt = dt*100
                            else:
                                dt = 1e-10
                                initialdt = dt/10
                        else: 
                            isNeutron = True
                            visualScale = 1
                            dt = 1e-11
                            initialdt = dt
                            radius = 1
                            #default simulation values for neutrons

                        temp = radius #Used so the height of the animation area is consistent for all particles 
                        #initialises data for new particle
                        m, q, B, vx, vy = getMagdata(data)
                        x, y = 0, window_size["height"]/2
                        v = Vector(5e11, vy)
                        s = Vector(x,y)
                        a=Vector(0,0)
                        alreadyEnteredField = False 

                        print("theoretical radius: ", radius)
                        print("mass: ", m)
                        print("q", q)
                        print("B", B)
                        print("v0", vx)
                        emit("displayData", ["mass: " + str(m),  "charge: " + str(q), "B: " + str(B), "v0: " + str(vx)])
                        radius = temp #Used so the height of the animation area is consistent for all particles 
                elif type == "changeB": #Changes magnetic field strength
                    newB = convertUnit("magnetic field strength", "Tesla", newPrompt["text"]) #ensures units for magnetic field strength are in Tesla
                    if B == False: print("Error tying to change B")
                    else: B = float(newB)
                elif type == "changeType": #Resimulates with the same data from the previous particle but with a different particle-type
                    temp = radius
                    pattern = r"(None|electron|alpha|proton|neutron)" #regular expression for extracting which particle-type to use
                    particleType = re.findall(pattern, newPrompt["text"])
                    m, q = MQforParticle(particleType[0])
                    if particleType[0] != "neutron":
                        radius = (m*vx) / (abs(q*B))
                        print("theoretical radius: ", radius)
                        if radius < 1e-4:
                            dt = 1e-13
                            initialdt = dt*100
                        else:
                            dt = 1e-10
                            initialdt = dt/10
                    x, y = 0, window_size["height"]/2
                    s = Vector(x,y)
                    v = Vector(5e11, vy)
                    a=Vector(0,0)
                    c = False 
                    print("mass: ", m)
                    print("q", q)
                    print("B", B)
                    print("v0", vx)
                    radius = temp
                
                add_child_prompt(latest_record.id, newPrompt["text"])
                emit("update_dropdown", newPrompt["text"])
                
            print(type)
            confirmNewPrompt = False
        
    redirectToNewSim(type, num)

# ================================================================

#Below all handle messages sent from the front end, changing global variables so simulation methods can use those values 
@socketio.on("connect")
def handle_connect():
    global connected 
    connected = True
    print("Connected")

@socketio.on("disconnect")
def handle_disconnect():
    global connected
    connected = False 
    print("Disconnected")

@socketio.on("window_size")
def window_size(data):
    global window_size
    print("window size from front end is: ", data)
    window_size = data

@socketio.on("newPrompt")
def newPrompt(prompt):
    global newPrompt
    newPrompt = prompt
    print(newPrompt)
    emit("confirm")

@socketio.on("confirmNewPrompt")
def confirmNewPrompt():
    global confirmNewPrompt
    confirmNewPrompt = True

@socketio.on("vt_graph_made")
def confirmVTgraph():
    global isvtGraph
    isvtGraph = 1

@socketio.on("at_graph_made")
def confirmATgraph():
    global isatGraph
    isatGraph = 1

# ================================================================

if __name__ == "__main__":
    app.run(debug=True)