from flask_wtf import FlaskForm
from wtforms import StringField, HiddenField, SelectField
from wtforms.validators import DataRequired
from monApp import db

class InscriptionForm(FlaskForm):
    id_client = HiddenField('id_client')
    prenom = StringField('Prénom', validators=[DataRequired()])
    nom = StringField('Nom', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    mot_de_passe = StringField('Mot de passe', validators=[DataRequired()])
    confirmation_mot_de_passe = StringField('Confirmer le mot de passe', validators=[DataRequired()])

class ConnexionForm(FlaskForm):
    telephone = StringField('Téléphone', validators=[DataRequired()])
    mot_de_passe = StringField('Mot de passe', validators=[DataRequired()])