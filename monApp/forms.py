from flask_wtf import FlaskForm
from wtforms.fields import StringField, HiddenField, SelectField, PasswordField, IntegerField, DateField
from wtforms.validators import DataRequired, EqualTo, Optional
from monApp import db

class InscriptionForm(FlaskForm):
    id_client = HiddenField('id_client')
    prenom = StringField('Prénom', validators=[DataRequired()])
    nom = StringField('Nom', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    mot_de_passe = PasswordField('Mot de passe', validators=[DataRequired()])
    confirmation_mot_de_passe = PasswordField('Confirmer le mot de passe', validators=[DataRequired()])

class ConnexionForm(FlaskForm):
    telephone = StringField('Téléphone')
    mot_de_passe = PasswordField('Mot de passe')
    next = HiddenField()

    def get_authenticated_client(self):
        from hashlib import sha256
        from .models import CLIENT 
        unClient = db.session.query(CLIENT).filter_by(telephone=self.telephone.data).first()
        if unClient is None:
            return None
        m = sha256()
        m.update(self.mot_de_passe.data.encode())
        passwd = m.hexdigest()
        return unClient if passwd == unClient.mot_de_passe else None

class EditProfileForm(FlaskForm):
    prenom = StringField('Prénom', validators=[DataRequired()])
    nom = StringField('Nom', validators=[DataRequired()])
    telephone = StringField('Téléphone', validators=[DataRequired()])
    current_mot_de_passe = PasswordField('Mot de passe actuel', validators=[Optional()])
    new_mot_de_passe = PasswordField('Nouveau mot de passe', validators=[Optional()])
    confirm_new_mot_de_passe = PasswordField('Confirmer le nouveau mot de passe', validators=[Optional(), EqualTo('new_mot_de_passe', message='Les mots de passe doivent correspondre.')])

class ReservationForm(FlaskForm):
    id_client = HiddenField('id_client')
    date_reservation = DateField('Date de réservation', format='%Y-%m-%d', validators=[DataRequired()])
    id_service = SelectField('Service', coerce=int, validators=[DataRequired()])
    nb_personne = IntegerField('Nombre de personnes', validators=[DataRequired()])
    
    def __init__(self, *args, **kwargs):
        super(ReservationForm, self).__init__(*args, **kwargs)
        from .models import SERVICE
        services = db.session.query(SERVICE).all()
        self.id_service.choices = [(s.id_service, f"{s.heure_debut.strftime('%H:%M')} - {s.heure_fin.strftime('%H:%M')}") for s in services]