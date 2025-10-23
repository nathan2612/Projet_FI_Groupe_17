from .app import app
from flask import render_template,request
from .app import db

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")
                       
@app.route('/contact/')
def contact():
    return render_template("contact.html")

@app.route('/apropos/')
def propos():
    return render_template("propos.html")



if __name__ == "__main__":
    app.run()