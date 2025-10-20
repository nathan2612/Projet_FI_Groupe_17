from flask_sqlalchemy import SQLAlchemy
from datetime import date, time
from .app import db

# NOTE: Le script SQL fourni utilise parfois des clés primaires composites
# (par exemple PRIMARY KEY (id_plat, id_categorie)). Pour simplifier l'utilisation
# avec SQLAlchemy et les relations (FK), j'ai choisi ici de considérer `id_plat`
# comme clé primaire unique sur la table `Plats` (et conserver id_categorie comme FK).
# Cette décision est une hypothèse raisonnable ; si vous préférez conserver la
# clé composite, dites-le et j'adapterai les modèles.


class Categorie(db.Model):
	__tablename__ = 'categories'
	id_categorie = db.Column(db.Integer, primary_key=True)
	nom_categorie = db.Column(db.String(100))
	description = db.Column(db.Text)

	plats = db.relationship('Plat', back_populates='categorie')

	def __repr__(self):
		return f"<Categorie {self.nom_categorie} ({self.id_categorie})>"


class Plat(db.Model):
	__tablename__ = 'plats'
	id_plat = db.Column(db.Integer, primary_key=True)
	id_categorie = db.Column(db.Integer, db.ForeignKey('categories.id_categorie'))
	nom_plat = db.Column(db.String(150))
	description = db.Column(db.Text)
	prix = db.Column(db.Numeric(10, 2))
	stock = db.Column(db.Integer)
	disponible = db.Column(db.Boolean, default=True)

	categorie = db.relationship('Categorie', back_populates='plats')
	recettes = db.relationship('DefinirStock', back_populates='plat')
	details_commandes = db.relationship('AppartenirPlats', back_populates='plat')
	contenirs = db.relationship('Contenir', back_populates='plat')

	def __repr__(self):
		return f"<Plat {self.nom_plat} ({self.id_plat})>"


class Client(db.Model):
	__tablename__ = 'clients'
	id_client = db.Column(db.Integer, primary_key=True)
	nom_client = db.Column(db.String(100))
	prenom_client = db.Column(db.String(100))
	email = db.Column(db.String(150))
	telephone = db.Column(db.String(15))

	reservations = db.relationship('Reservation', back_populates='client')
	commandes = db.relationship('Commande', back_populates='client')
	avis = db.relationship('Avis', back_populates='client')

	def __repr__(self):
		return f"<Client {self.nom_client} {self.prenom_client} ({self.id_client})>"


class Reservation(db.Model):
	__tablename__ = 'reservation'
	id_reservation = db.Column(db.Integer, primary_key=True)
	id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'))
	date_reservation = db.Column(db.Date)
	heure_reservation = db.Column(db.Time)
	nombre_personnes = db.Column(db.Integer)

	client = db.relationship('Client', back_populates='reservations')

	def __repr__(self):
		return f"<Reservation {self.id_reservation} client={self.id_client} date={self.date_reservation}>"


class Commande(db.Model):
	__tablename__ = 'commandes'
	id_commande = db.Column(db.Integer, primary_key=True)
	id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'))
	date_commande = db.Column(db.Date)
	statut = db.Column(db.String(50), default='En attente')
	montant_total = db.Column(db.Numeric(10, 2))
	sur_place = db.Column(db.Boolean, default=False)

	client = db.relationship('Client', back_populates='commandes')
	plats = db.relationship('AppartenirPlats', back_populates='commande')
	menus = db.relationship('AppartenirMenus', back_populates='commande')

	def __repr__(self):
		return f"<Commande {self.id_commande} client={self.id_client} statut={self.statut}>"


class Menu(db.Model):
	__tablename__ = 'menu'
	id_menu = db.Column(db.Integer, primary_key=True)
	nom_menu = db.Column(db.String(150))
	description = db.Column(db.Text)
	prix = db.Column(db.Numeric(10, 2))

	contenir = db.relationship('Contenir', back_populates='menu')
	appartenir_menus = db.relationship('AppartenirMenus', back_populates='menu')

	def __repr__(self):
		return f"<Menu {self.nom_menu} ({self.id_menu})>"


class Contenir(db.Model):
	__tablename__ = 'contenir'
	id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), primary_key=True)
	id_plat = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)

	menu = db.relationship('Menu', back_populates='contenir')
	plat = db.relationship('Plat', back_populates='contenirs')

	def __repr__(self):
		return f"<Contenir menu={self.id_menu} plat={self.id_plat}>"


class AppartenirPlats(db.Model):
	__tablename__ = 'appartenir_plats'
	id_commande = db.Column(db.Integer, db.ForeignKey('commandes.id_commande'), primary_key=True)
	id_plat = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)
	quantite = db.Column(db.Integer)
	prix_unitaire = db.Column(db.Numeric(10, 2))

	commande = db.relationship('Commande', back_populates='plats')
	plat = db.relationship('Plat', back_populates='details_commandes')

	def __repr__(self):
		return f"<AppartenirPlats commande={self.id_commande} plat={self.id_plat} qty={self.quantite}>"


class AppartenirMenus(db.Model):
	__tablename__ = 'appartenir_menus'
	id_commande = db.Column(db.Integer, db.ForeignKey('commandes.id_commande'), primary_key=True)
	id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), primary_key=True)
	quantite = db.Column(db.Integer)
	prix_unitaire = db.Column(db.Numeric(10, 2))

	commande = db.relationship('Commande', back_populates='menus')
	menu = db.relationship('Menu', back_populates='appartenir_menus')

	def __repr__(self):
		return f"<AppartenirMenus commande={self.id_commande} menu={self.id_menu} qty={self.quantite}>"


class Avis(db.Model):
	__tablename__ = 'avis'
	id_avis = db.Column(db.Integer, primary_key=True)
	id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'))
	note = db.Column(db.Integer)
	commentaire = db.Column(db.Text)

	client = db.relationship('Client', back_populates='avis')

	def __repr__(self):
		return f"<Avis {self.id_avis} client={self.id_client} note={self.note}>"


class DefinirStock(db.Model):
	__tablename__ = 'definir_stock'
	id_plat = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)
	jour = db.Column(db.Date, primary_key=True)
	stock = db.Column(db.Integer)

	plat = db.relationship('Plat', back_populates='recettes')

	def __repr__(self):
		return f"<DefinirStock plat={self.id_plat} jour={self.jour} stock={self.stock}>"

