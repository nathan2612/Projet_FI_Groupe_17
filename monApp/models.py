from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from .app import db,login_manager
from sqlalchemy import event, DDL
from flask_login import UserMixin

class CATEGORIE(db.Model):
	__tablename__ = 'categories'
	id_categorie = db.Column(db.Integer, primary_key=True)
	nom_categorie = db.Column(db.String(100))
	image_categorie = db.Column(db.String(255), default='images/default-categorie.jpg')

	plats = db.relationship('PLAT', back_populates='categorie')

	def __repr__(self):
		return f"<Categorie {self.nom_categorie} ({self.id_categorie})>"


class PLAT(db.Model):
	__tablename__ = 'plats'
	id_plat = db.Column(db.Integer, primary_key=True)
	id_categorie = db.Column(db.Integer, db.ForeignKey('categories.id_categorie'))
	nom_plat = db.Column(db.String(150))
	description = db.Column(db.Text)
	longue_description = db.Column(db.Text, nullable=True)
	prix = db.Column(db.Numeric(10, 2))
	disponible = db.Column(db.Boolean, default=True)
	image_url = db.Column(db.String(255), default='default_plat.png')
	vegetarien = db.Column(db.Boolean, default=False)
	vegan = db.Column(db.Boolean, default=False)
	gluten = db.Column(db.Boolean, default=False)
	lactose = db.Column(db.Boolean, default=False)
	fruit_a_coque = db.Column(db.Boolean, default=False)
	crustaces = db.Column(db.Boolean, default=False)

	categorie = db.relationship('CATEGORIE', back_populates='plats')
	stock = db.relationship('DEFINIR_STOCK', back_populates='plat')
	details_commandes = db.relationship('APPARTENIR_PLATS', back_populates='plat')
	contenirs = db.relationship('CONTENIR', back_populates='plat')

	def __repr__(self):
		return f"<Plat {self.nom_plat} ({self.id_plat})>"


class CLIENT(db.Model,UserMixin):
	__tablename__ = 'clients'
	id_client = db.Column(db.Integer, primary_key=True)
	nom = db.Column(db.String(100))
	prenom = db.Column(db.String(100))
	telephone = db.Column(db.String(15), unique=True, )
	mot_de_passe = db.Column(db.String(255))
	banni = db.Column(db.Boolean, default=False)
	# Rôle de l'utilisateur : 'user' (par défaut) ou 'admin'
	role = db.Column(db.String(20), default='user')

	commandes = db.relationship('COMMANDE', back_populates='client')
	avis = db.relationship('AVIS', back_populates='client')
	reservations = db.relationship('RESERVATION', back_populates='client')

	def get_id(self):
		return self.id_client
	def is_admin(self):
		return self.role == 'admin'	

	def __repr__(self):
		return f"<Client {self.nom} {self.prenom} ({self.id_client})>"
	
@login_manager.user_loader
def load_user(telephone):
    return db.session.get(CLIENT,telephone)

class COMMANDE(db.Model):
	__tablename__ = 'commandes'
	id_commande = db.Column(db.Integer, primary_key=True)
	id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'))
	date_commande = db.Column(db.DateTime, nullable=True)
	statut = db.Column(db.String(50), default='En commande')
	montant_total = db.Column(db.Numeric(10, 2),default=0.00)
	nombre_personnes = db.Column(db.Integer)

	__table_args__ = (
		db.CheckConstraint('nombre_personnes <= 12', name='chk_nombre_personnes'),
		db.CheckConstraint("statut IN ('En commande', 'En attente', 'En préparation', 'Prêt','non récupéré','récupéré')", name='chk_statut_valide'),
		db.CheckConstraint("date_commande IS NULL OR (TIME(date_commande) BETWEEN '11:30:00' AND '14:00:00') OR ((TIME(date_commande) BETWEEN '17:00:00' AND '20:00:00'))", name='chk_heure_valide'),
		db.CheckConstraint("date_commande IS NULL OR WEEKDAY(DATE(date_commande)) IN (0, 1, 2, 3, 4)", name='chk_commande_jour_valide'),
	)

	client = db.relationship('CLIENT', back_populates='commandes')
	plats = db.relationship('APPARTENIR_PLATS', back_populates='commande')
	menus = db.relationship('APPARTENIR_MENUS', back_populates='commande')

	def __repr__(self):
		return f"<Commande {self.id_commande} client={self.id_client} statut={self.statut}>"


class MENU(db.Model):
	__tablename__ = 'menu'
	id_menu = db.Column(db.Integer, primary_key=True)
	nom_menu = db.Column(db.String(150))
	description = db.Column(db.Text)
	image_url = db.Column(db.String(255), default='default_menu.jpg')
	prix = db.Column(db.Numeric(10, 2))

	contenir = db.relationship('CONTENIR', back_populates='menu')
	appartenir_menus = db.relationship('APPARTENIR_MENUS', back_populates='menu')

	def __repr__(self):
		return f"<Menu {self.nom_menu} ({self.id_menu})>"


class CONTENIR(db.Model):
	__tablename__ = 'contenir'
	id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), primary_key=True)
	id_plat = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)
	type_plat = db.Column(db.Integer, nullable=False, default=1)

	__table_args__ = (
		db.CheckConstraint('type_plat IN (0,1,2)', name='chk_type_mauvais'),
	)

	menu = db.relationship('MENU', back_populates='contenir')
	plat = db.relationship('PLAT', back_populates='contenirs')

	def __repr__(self):
		# use the actual column name `type_plat` (0=entrée,1=plat,2=dessert)
		course_name = {0: 'entrée', 1: 'plat', 2: 'dessert'}.get(self.type_plat, str(self.type_plat))
		return f"<Contenir menu={self.id_menu} plat={self.id_plat} type_plat={course_name}>"


class APPARTENIR_PLATS(db.Model):
	__tablename__ = 'appartenir_plats'
	id_commande = db.Column(db.Integer, db.ForeignKey('commandes.id_commande'), primary_key=True)
	id_plat = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)
	quantite = db.Column(db.Integer)

	commande = db.relationship('COMMANDE', back_populates='plats')
	plat = db.relationship('PLAT', back_populates='details_commandes')

	def __repr__(self):
		return f"<AppartenirPlats commande={self.id_commande} plat={self.id_plat} qty={self.quantite}>"


class APPARTENIR_MENUS(db.Model):
	__tablename__ = 'appartenir_menus'
	id_commande = db.Column(db.Integer, db.ForeignKey('commandes.id_commande'), primary_key=True)
	id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), primary_key=True)
	quantite = db.Column(db.Integer)

	commande = db.relationship('COMMANDE', back_populates='menus')
	menu = db.relationship('MENU', back_populates='appartenir_menus')

	id_entree = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)
	id_plat_choisi = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)
	id_dessert = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)

	entree = db.relationship('PLAT', foreign_keys=[id_entree])
	plat_choisi = db.relationship('PLAT', foreign_keys=[id_plat_choisi])
	dessert = db.relationship('PLAT', foreign_keys=[id_dessert])

	def __repr__(self):
		return f"<AppartenirMenus commande={self.id_commande} menu={self.id_menu} qty={self.quantite} entree={self.id_entree} plat={self.id_plat_choisi} dessert={self.id_dessert}>"


class AVIS(db.Model):
	__tablename__ = 'avis'
	id_avis = db.Column(db.Integer, primary_key=True)
	id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'))
	note = db.Column(db.Integer)
	commentaire = db.Column(db.Text)

	client = db.relationship('CLIENT', back_populates='avis')

	def __repr__(self):
		return f"<Avis {self.id_avis} client={self.id_client} note={self.note}>"


class DEFINIR_STOCK(db.Model):
	__tablename__ = 'definir_stock'
	id_plat = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)
	jour = db.Column(db.Date, primary_key=True)
	stock = db.Column(db.Integer)

	plat = db.relationship('PLAT', back_populates='stock')

	def __repr__(self):
		return f"<DefinirStock plat={self.id_plat} jour={self.jour} stock={self.stock}>"
	
class RESERVATION(db.Model):
	__tablename__ = 'reservation'
	id_reservation = db.Column(db.Integer, primary_key = True)
	date_reservation = db.Column(db.Date)
	id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'))
	id_service = db.Column(db.Integer, db.ForeignKey('service.id_service'))
	nb_personne = db.Column(db.Integer)

	client = db.relationship('CLIENT', back_populates='reservations')
	service = db.relationship('SERVICE', back_populates='reservations')

	def __repr__(self):
		return f"<Reservation {self.id_reservation} client={self.id_client} service={self.id_service} nb_personne={self.nb_personne}>"


class SERVICE(db.Model):
	__tablename__ = 'service'
	id_service = db.Column(db.Integer,primary_key=True)
	heure_debut = db.Column(db.Time)
	heure_fin = db.Column(db.Time)
	actif = db.Column(db.Boolean)

	reservations = db.relationship('RESERVATION', back_populates='service')

	def __repr__(self):
		return f"<Service {self.id_service} debut={self.heure_debut} fin={self.heure_fin}>"


class SALLE(db.Model):
	__tablename__ = 'salle'
	id_parametre = db.Column(db.Integer, primary_key=True)
	cle = db.Column(db.String(100), unique=True)
	valeur = db.Column(db.Integer)

	def __repr__(self):
		return f"<Parametre {self.cle}={self.valeur}>"

trigger_insert_reservation = DDL('''
CREATE TRIGGER trg_insert_reservation
BEFORE INSERT ON reservation
FOR EACH ROW
BEGIN
    DECLARE capacite_max INT;
    DECLARE total_reserve INT;

    SELECT valeur INTO capacite_max FROM salle WHERE cle = 'capacite';
    
    SELECT COALESCE(SUM(nb_personne), 0) INTO total_reserve FROM reservation WHERE id_service = NEW.id_service AND date_reservation = NEW.date_reservation;

    IF total_reserve + NEW.nb_personne > capacite_max THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Capacité du restaurant dépassée pour ce service';
    END IF;
END;''')

event.listen(RESERVATION.__table__, 'after_create', trigger_insert_reservation)

trigger_update_reservation = DDL('''
CREATE TRIGGER trg_update_reservation
BEFORE UPDATE ON reservation
FOR EACH ROW
BEGIN
    DECLARE capacite_max INT;
    DECLARE total_reserve INT;
    
    SELECT valeur INTO capacite_max FROM salle WHERE cle = 'capacite';
    
    SELECT COALESCE(SUM(nb_personne), 0) INTO total_reserve FROM reservation WHERE id_service = NEW.id_service AND date_reservation = NEW.date_reservation AND id_reservation != NEW.id_reservation;
    
    IF total_reserve + NEW.nb_personne > capacite_max THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Capacité du restaurant dépassée pour ce service';
    END IF;
END;''')

event.listen(RESERVATION.__table__, 'after_create', trigger_update_reservation)

# * triggers gestion stock plats
trigger_insert_stock_plats = DDL('''
CREATE TRIGGER trg_insert_stock_plats
BEFORE INSERT ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_plat and jour = CURDATE()) - NEW.quantite >= 0 THEN
		UPDATE definir_stock SET stock = stock - NEW.quantite WHERE id_plat = NEW.id_plat and jour = CURDATE();
	ELSE
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour commander le plat';
	END IF;		 
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_insert_stock_plats)

trigger_update_stock_plats = DDL('''
CREATE TRIGGER trg_update_stock_plats
BEFORE UPDATE ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_plat and jour = CURDATE()) + OLD.quantite - NEW.quantite >= 0 THEN
		UPDATE definir_stock SET stock = stock + OLD.quantite - NEW.quantite WHERE id_plat = NEW.id_plat and jour = CURDATE();
	ELSE
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour commander le plat';
	END IF;		 
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_update_stock_plats)

trigger_delete_stock_plats = DDL('''
CREATE TRIGGER trg_delete_stock_plats
BEFORE DELETE ON appartenir_plats
FOR EACH ROW
BEGIN
	UPDATE definir_stock SET stock = stock + OLD.quantite WHERE id_plat = OLD.id_plat and jour = CURDATE();
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_delete_stock_plats)

trigger_insert_stock_menus = DDL('''
CREATE TRIGGER trg_insert_stock_menus
BEFORE INSERT ON appartenir_menus
FOR EACH ROW
BEGIN
	-- entree
	IF NEW.id_entree IS NOT NULL THEN
		IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_entree AND jour = CURDATE()) - NEW.quantite >= 0 THEN
			UPDATE definir_stock SET stock = stock - NEW.quantite WHERE id_plat = NEW.id_entree AND jour = CURDATE();
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour l''entrée du menu';
		END IF;
	END IF;						 
	-- plat
	IF NEW.id_plat_choisi IS NOT NULL THEN
		IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_plat_choisi AND jour = CURDATE()) - NEW.quantite >= 0 THEN
			UPDATE definir_stock SET stock = stock - NEW.quantite WHERE id_plat = NEW.id_plat_choisi AND jour = CURDATE();
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour le plat du menu';
		END IF;
	END IF;					 
	-- dessert
	IF NEW.id_dessert IS NOT NULL THEN
		IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_dessert AND jour = CURDATE()) - NEW.quantite >= 0 THEN
			UPDATE definir_stock SET stock = stock - NEW.quantite WHERE id_plat = NEW.id_dessert AND jour = CURDATE();
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour le dessert du menu';
		END IF;
	END IF;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_insert_stock_menus)

trigger_update_stock_menus = DDL('''
CREATE TRIGGER trg_update_stock_menus
BEFORE UPDATE ON appartenir_menus
FOR EACH ROW
BEGIN
		-- entree
		IF OLD.id_entree IS NOT NULL THEN
			IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_entree AND jour = CURDATE()) + OLD.quantite - NEW.quantite >= 0 THEN
				UPDATE definir_stock SET stock = stock + OLD.quantite - NEW.quantite WHERE id_plat = NEW.id_entree AND jour = CURDATE();
			ELSE
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour l''entrée du menu';
			END IF;
		END IF;
		-- plat
		IF OLD.id_plat_choisi IS NOT NULL THEN
			IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_plat_choisi AND jour = CURDATE()) + OLD.quantite - NEW.quantite >= 0 THEN
				UPDATE definir_stock SET stock = stock + OLD.quantite - NEW.quantite WHERE id_plat = NEW.id_plat_choisi AND jour = CURDATE();
			ELSE
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour le plat du menu';
			END IF;
		END IF;
		-- dessert
		IF OLD.id_dessert IS NOT NULL THEN
			IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_dessert AND jour = CURDATE()) + OLD.quantite - NEW.quantite >= 0 THEN
				UPDATE definir_stock SET stock = stock + OLD.quantite - NEW.quantite WHERE id_plat = NEW.id_dessert AND jour = CURDATE();
			ELSE
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour le dessert du menu';
			END IF;
		END IF;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_update_stock_menus)

trigger_delete_stock_menus = DDL('''
CREATE TRIGGER trg_delete_stock_menus
BEFORE DELETE ON appartenir_menus
FOR EACH ROW
BEGIN
		-- entree
		IF OLD.id_entree IS NOT NULL THEN
			UPDATE definir_stock SET stock = stock + OLD.quantite WHERE id_plat = OLD.id_entree AND jour = CURDATE();
		END IF;
		-- plat
		IF OLD.id_plat_choisi IS NOT NULL THEN
			UPDATE definir_stock SET stock = stock + OLD.quantite WHERE id_plat = OLD.id_plat_choisi AND jour = CURDATE();
		END IF;
		-- dessert
		IF OLD.id_dessert IS NOT NULL THEN
			UPDATE definir_stock SET stock = stock + OLD.quantite WHERE id_plat = OLD.id_dessert AND jour = CURDATE();
		END IF;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_delete_stock_menus)

trigger_insert_calcule_montant_total_plats = DDL('''
CREATE TRIGGER trg_calcule_montant_total_plats
AFTER INSERT ON appartenir_plats
FOR EACH ROW
BEGIN
	UPDATE commandes
	SET montant_total = montant_total + ((select prix from plats where id_plat = NEW.id_plat) * NEW.quantite)
	WHERE id_commande = NEW.id_commande;
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_insert_calcule_montant_total_plats)

trigger_update_calcule_montant_total_plats = DDL('''
CREATE TRIGGER trg_update_calcule_montant_total_plats
AFTER UPDATE ON appartenir_plats
FOR EACH ROW
BEGIN
	UPDATE commandes
	SET montant_total = montant_total - ((select prix from plats where id_plat = OLD.id_plat) * OLD.quantite) + ((select prix from plats where id_plat = NEW.id_plat) * NEW.quantite)
	WHERE id_commande = NEW.id_commande;
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_update_calcule_montant_total_plats)

trigger_delete_calcule_montant_total_plats = DDL('''
CREATE TRIGGER trg_delete_calcule_montant_total_plats
AFTER DELETE ON appartenir_plats
FOR EACH ROW
BEGIN
	UPDATE commandes
	SET montant_total = montant_total - ((select prix from plats where id_plat = OLD.id_plat) * OLD.quantite)
	WHERE id_commande = OLD.id_commande;
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_delete_calcule_montant_total_plats)

# * triggers calcule montant total menus
trigger_insert_calcule_montant_total_menus = DDL('''
CREATE TRIGGER trg_insert_calcule_montant_total_menus
AFTER INSERT ON appartenir_menus
FOR EACH ROW
BEGIN
	UPDATE commandes
	SET montant_total = montant_total + ((select prix from menu where id_menu = NEW.id_menu) * NEW.quantite)
	WHERE id_commande = NEW.id_commande;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_insert_calcule_montant_total_menus)

trigger_update_calcule_montant_total_menus = DDL('''
CREATE TRIGGER trg_update_calcule_montant_total_menus
AFTER UPDATE ON appartenir_menus
FOR EACH ROW
BEGIN
	UPDATE commandes
	SET montant_total = montant_total - ((select prix from menu where id_menu = OLD.id_menu) * OLD.quantite) + ((select prix from menu where id_menu = NEW.id_menu) * NEW.quantite)
	WHERE id_commande = NEW.id_commande;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_update_calcule_montant_total_menus)

trigger_delete_calcule_montant_total_menus = DDL('''
CREATE TRIGGER trg_delete_calcule_montant_total_menus
AFTER DELETE ON appartenir_menus
FOR EACH ROW
BEGIN
	UPDATE commandes
	SET montant_total = montant_total - ((select prix from menu where id_menu = OLD.id_menu) * OLD.quantite)
	WHERE id_commande = OLD.id_commande;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_delete_calcule_montant_total_menus)

# * trigger bannir client
trigger_banni = DDL('''
CREATE TRIGGER trg_update_banni
BEFORE INSERT ON commandes
FOR EACH ROW
BEGIN
	if (select banni from clients where id_client = NEW.id_client) then
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Client banni ne peut pas passer de commande';
	end if;
END;''')

event.listen(COMMANDE.__table__, 'after_create', trigger_banni)