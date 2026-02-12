from flask import Flask
app=Flask(__name__)

app.config.from_object('config')

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()
db.init_app(app)

from flask_login import LoginManager
login_manager = LoginManager(app)

login_manager.login_view = "connexion"
