from flask import Flask
app=Flask(__name__)

# Config options - Make sure you created a 'config.py' file.
app.config.from_object('config')
# To get one variable, tape app.config['MY_VARIABLE']

# Create database connection object
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

#from flask_login import LoginManager
#login_manager = LoginManager(app)

#login_manager.login_view = "login"