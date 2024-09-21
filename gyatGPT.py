# TO RUN:
# ON COMPUTER: flask --app appname run (--debug)
# ON NETWORK: flask run --host=0.0.0.0
# end: ctrl+c in terminal
# change port:
# flask run -p (5001)
from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from NLP.modelGen import guess, load_model
import time
import json
from particleSim.particlesim import *

model = load_model()

#Create instance of flask application
#__name__ tells instance which module is being used
app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
db = SQLAlchemy(app) #Databse 

class Todo(db.Model): 
    id = db.Column(db.Integer, primary_key=True) #Primary key
    content = db.Column(db.String(200), nullable=False)
    prompt = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return "<Task %r>" % self.id
    
# Code below is for initialising db
# with app.app_context():
#     db.create_all()

#.route decorator below, converts function's return value into a HTTP response
#this will be displayed on the web browser;
#'/' passed in value - function responds to web requests for the URL / (main URL)
@app.route('/', methods=["POST", "GET"]) #HTML methods
def index():
    if request.method == "POST":
        task_content = request.form["content"]
        g = guess(task_content, model)
        if g == " BMOTION":
            return redirect('/brownianMotion')
        new_task = Todo(content=g, prompt=task_content)

        try:
            db.session.add(new_task) #adds task to db with class methods
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task"
    else:
        tasks = Todo.query.all()
        return render_template("home.html", tasks=tasks)
    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that task"
    
@app.route('/brownianMotion/')
def BMsim():
    return render_template("brownianMotion.html")

# '/stream' called by javascript in streamtest.html
@app.route('/bMotion')
def stream():
    def particleStream():
        dt = 1/60 
        space_size = 400
        particles = []
        for p in range(40): 
            particles.append(Particle(10, (0,150,0), 1, 1))
        for p in range(100):
            particles.append(Particle(2, (0,0,0), 0.5, 0))
        # ALL STUFF ABOVE WILL EVENTUALLY BE SENT FROM CLIENT
        # (rate, particle number, particle mass, colour etc.)
        while True:
            qtree = generateQuadtree(space_size, particles)
            for p in particles:
                updateParticle(p, dt)
                p.boundaryCheck(space_size) 
            for p in particles:
                checkCollisions(p, qtree, dt)
            
            data = []
            for p in particles:
                p.s.vect.append(p.radius)
                p.s.vect.append(p.isInvisible)
                data.append(p.s.vect)

            yield f"data: {json.dumps(data)}\n\n"
            time.sleep(dt)
    
    return Response(particleStream(), content_type="text/event-stream")

if __name__ == "__main__":
    app.run(debug=True)


# Can put onto a live webserver with heroku
# tut at end of yt video