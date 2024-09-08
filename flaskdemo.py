# TO RUN:
# ON COMPUTER: flask --app appname run (--debug)
# ON NETWORK: flask run --host=0.0.0.0
# end: ctrl+c in terminal
# change port:
# flask run -p (5001)
from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from wordvectorstest import guess, load_model

model = load_model()

#Create instance of flask application
#__name__ tells instance which module is being used
app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///test.db"
db = SQLAlchemy(app) #Databse 

class Todo(db.Model): 
    id = db.Column(db.Integer, primary_key=True) #Primary key
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return "<Task %r>" % self.id
    
#with app.app_context():
#    db.create_all()

#.route decorator below, converts function's return value into a HTTP response
#this will be displayed on the web browser;
#'/' passed in value - function responds to web requests for the URL / (main URL)
@app.route('/', methods=["POST", "GET"]) #HTML methods
def index():
    if request.method == "POST":
        task_content = request.form["content"]
        new_task = Todo(content=guess(task_content, model))

        try:
            db.session.add(new_task) #adds task to db with class methods
            db.session.commit()
            return redirect('/')
        except:
            return "There was an issue adding your task"
    else:
        tasks = Todo.query.all()
        return render_template("index.html", tasks=tasks)
    
@app.route('/delete/<int:id>')
def delete(id):
    task_to_delete = Todo.query.get_or_404(id)
    try:
        db.session.delete(task_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that task"
    
@app.route('/update/<int:id>', methods = ["GET", "POST"])
def update(id):
    task = Todo.query.get_or_404(id)

    if request.method == "POST":
        task.content = request.form["content"]

        try:
            db.session.commit()
            return redirect('/')
        except:
            "There was a problem updating that task"
    else:
        return render_template("update.html", task=task)
    
@app.route('/rectangle/')
def rectangle():
    return render_template("test.html")

if __name__ == "__main__":
    app.run(debug=True)


# Can put onto a live webserver with heroku
# tut at end of yt video