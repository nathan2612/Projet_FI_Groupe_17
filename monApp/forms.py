from flask_wtf import FlaskForm
from wtforms.fields import StringField, HiddenField, SelectField, PasswordField, BooleanField, DecimalField, TextAreaField, SubmitField, SelectMultipleField
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


class PlatForm(FlaskForm):
    id_plat = HiddenField('id_plat')
    nom_plat = StringField('Nom du plat', validators=[DataRequired()])
    id_categorie = SelectField('Catégorie', coerce=int, validators=[Optional()])
    description = StringField('Description', validators=[Optional()])
    longue_description = TextAreaField('Description longue', validators=[Optional()])
    prix = StringField('Prix', validators=[DataRequired()])
    disponible = SelectField('Disponible', choices=[('1', 'Oui'), ('0', 'Non')], validators=[Optional()])
    image_url = StringField('URL de l\'image', validators=[Optional()])
    vegetarien = BooleanField('Végétarien')
    vegan = BooleanField('Vegan')
    gluten = BooleanField('Contient du gluten')
    lactose = BooleanField('Contient du lactose')
    fruit_a_coque = BooleanField('Contient fruits à coque')
    crustaces = BooleanField('Contient crustacés')
    submit = SubmitField('Enregistrer')
    
    def validate_prix(self, field):
        """Validation personnalisée pour vérifier que le prix est un nombre valide."""
        try:
            prix_float = float(field.data.replace(',', '.'))
            if prix_float < 0:
                raise ValueError("Le prix ne peut pas être négatif.")
        except (ValueError, AttributeError):
            raise ValueError('Le prix doit être un nombre valide (ex: 12.50 ou 12,50).')


class MenuForm(FlaskForm):
    id_menu = HiddenField('id_menu')
    nom_menu = StringField('Nom du menu', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    prix = StringField('Prix', validators=[DataRequired()])
    image_url = StringField('URL de l\'image', validators=[Optional()])
    entrees = SelectMultipleField('Entrées', coerce=int, validators=[Optional()])
    plats = SelectMultipleField('Plats principaux', coerce=int, validators=[Optional()])
    desserts = SelectMultipleField('Desserts', coerce=int, validators=[Optional()])
    submit = SubmitField('Enregistrer')
    
    def validate_prix(self, field):
        """Validation personnalisée pour vérifier que le prix est un nombre valide."""
        try:
            prix_float = float(field.data.replace(',', '.'))
            if prix_float < 0:
                raise ValueError("Le prix ne peut pas être négatif.")
        except (ValueError, AttributeError):
            raise ValueError('Le prix doit être un nombre valide (ex: 12.50 ou 12,50).')
    
    def validate(self):
        """Validation personnalisée pour s'assurer qu'au moins un élément de chaque type est sélectionné."""
        if not super(MenuForm, self).validate():
            return False
        
        valid = True
        
        # Vérifier qu'au moins une entrée est sélectionnée
        if not self.entrees.data or len(self.entrees.data) < 1:
            self.entrees.errors.append('Au moins une entrée est requise pour créer un menu.')
            valid = False
        
        # Vérifier qu'au moins un plat principal est sélectionné
        if not self.plats.data or len(self.plats.data) < 1:
            self.plats.errors.append('Au moins un plat principal est requis pour créer un menu.')
            valid = False
        
        # Vérifier qu'au moins un dessert est sélectionné
        if not self.desserts.data or len(self.desserts.data) < 1:
            self.desserts.errors.append('Au moins un dessert est requis pour créer un menu.')
            valid = False
        
        # Vérifier qu'un même plat n'est pas sélectionné dans plusieurs catégories
        if self.entrees.data and self.plats.data and self.desserts.data:
            all_selected = set(self.entrees.data) | set(self.plats.data) | set(self.desserts.data)
            total_selections = len(self.entrees.data) + len(self.plats.data) + len(self.desserts.data)
            
            if len(all_selected) < total_selections:
                error_msg = 'Un même plat ne peut pas être sélectionné dans plusieurs catégories (entrée, plat principal, dessert).'
                if not any(error_msg in e for e in self.entrees.errors):
                    self.entrees.errors.append(error_msg)
                if not any(error_msg in e for e in self.plats.errors):
                    self.plats.errors.append(error_msg)
                if not any(error_msg in e for e in self.desserts.errors):
                    self.desserts.errors.append(error_msg)
                valid = False
        
        return valid