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
	prix = db.Column(db.Numeric(10, 2))
	disponible = db.Column(db.Boolean, default=True)
	image_url = db.Column(db.String(255), default='default_plat.png')
	vegetarien = db.Column(db.Boolean, default=False)
	vegan = db.Column(db.Boolean, default=False)
	sans_gluten = db.Column(db.Boolean, default=False)
	sans_lactose = db.Column(db.Boolean, default=False)
	sans_fruit_a_coque = db.Column(db.Boolean, default=False)
	sans_crustaces = db.Column(db.Boolean, default=False)

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
	telephone = db.Column(db.String(15))
	mot_de_passe = db.Column(db.String(255))
	banni = db.Column(db.Boolean, default=False)

	commandes = db.relationship('COMMANDE', back_populates='client')
	avis = db.relationship('AVIS', back_populates='client')

	def get_id(self):
		return self.id_client

	def __repr__(self):
		return f"<Client {self.nom_client} {self.prenom_client} ({self.id_client})>"
	
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
	sur_place = db.Column(db.Boolean, default=False)
	nombre_personnes = db.Column(db.Integer)

	__table_args__ = (
		db.CheckConstraint('nombre_personnes <= 12', name='chk_nombre_personnes'),
		db.CheckConstraint("statut IN ('En commande', 'En préparation', 'Prêt','non récupéré','récupéré')", name='chk_statut_valide'),
		db.CheckConstraint("date_commande IS NULL OR (TIME(date_commande) BETWEEN '11:30:00' AND '14:00:00') OR ((TIME(date_commande) BETWEEN '17:00:00' AND '20:00:00' AND sur_place=0))", name='chk_heure_valide'),
		db.CheckConstraint("date_commande IS NULL OR WEEKDAY(DATE(date_commande)) IN (1, 2, 3, 4, 5)", name='chk_commande_jour_valide'),
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
	prix = db.Column(db.Numeric(10, 2))

	contenir = db.relationship('CONTENIR', back_populates='menu')
	appartenir_menus = db.relationship('APPARTENIR_MENUS', back_populates='menu')

	def __repr__(self):
		return f"<Menu {self.nom_menu} ({self.id_menu})>"


class CONTENIR(db.Model):
	__tablename__ = 'contenir'
	id_menu = db.Column(db.Integer, db.ForeignKey('menu.id_menu'), primary_key=True)
	id_plat = db.Column(db.Integer, db.ForeignKey('plats.id_plat'), primary_key=True)

	menu = db.relationship('MENU', back_populates='contenir')
	plat = db.relationship('PLAT', back_populates='contenirs')

	def __repr__(self):
		return f"<Contenir menu={self.id_menu} plat={self.id_plat}>"


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

	def __repr__(self):
		return f"<AppartenirMenus commande={self.id_commande} menu={self.id_menu} qty={self.quantite}>"


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

@login_manager.user_loader
def load_user(username):
    return db.session.get(CLIENT, username)
	

# DDL trigger creation for MySQL/MariaDB: create trigger after table creation
# * triggers gestion stock plats
trigger_insert_stock_plats = DDL('''
CREATE TRIGGER trg_insert_stock_plats
BEFORE INSERT ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (SELECT statut FROM commandes WHERE id_commande = NEW.id_commande) != 'En commande' THEN
		IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_plat and jour = (select DATE(date_commande) from commandes where id_commande = NEW.id_commande)) - NEW.quantite >= 0 THEN
			UPDATE definir_stock SET stock = stock - NEW.quantite WHERE id_plat = NEW.id_plat and jour = (select DATE(date_commande) from commandes where id_commande = NEW.id_commande);
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour commander le plat';
		END IF;
	END IF;			 
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_insert_stock_plats)

trigger_update_stock_plats = DDL('''
CREATE TRIGGER trg_update_stock_plats
BEFORE UPDATE ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (SELECT statut FROM commandes WHERE id_commande = NEW.id_commande) != 'En commande' THEN
		IF (SELECT stock FROM definir_stock WHERE id_plat = NEW.id_plat and jour = (select DATE(date_commande) from commandes where id_commande = NEW.id_commande)) + OLD.quantite - NEW.quantite >= 0 THEN
			UPDATE definir_stock SET stock = stock + OLD.quantite - NEW.quantite WHERE id_plat = NEW.id_plat and jour = (select DATE(date_commande) from commandes where id_commande = NEW.id_commande);
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour commander le plat';
		END IF;
	END IF;			 
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_update_stock_plats)

trigger_insert_stock_menus = DDL('''
CREATE TRIGGER trg_insert_stock_menus
BEFORE INSERT ON appartenir_menus
FOR EACH ROW
BEGIN
	DECLARE fini INT DEFAULT 0;
	DECLARE plat_id INT;
	DECLARE les_plats CURSOR FOR
		SELECT id_plat FROM contenir WHERE id_menu = NEW.id_menu;

	DECLARE CONTINUE HANDLER FOR NOT FOUND SET fini = 1;

	IF (SELECT statut FROM commandes WHERE id_commande = NEW.id_commande) != 'En commande' THEN
		OPEN les_plats; -- Le curseur doit être ouvert après la condition IF
		WHILE not fini do
			FETCH les_plats INTO plat_id;
			IF not fini THEN
				IF (SELECT stock FROM definir_stock WHERE id_plat = plat_id and jour = (select DATE(date_commande) from commandes where id_commande = NEW.id_commande)) - NEW.quantite >= 0 THEN
					UPDATE definir_stock SET stock = stock - NEW.quantite WHERE id_plat = plat_id and jour = (select DATE(date_commande) from commandes where id_commande = NEW.id_commande);
				ELSE
					SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour commander le menu';
				END IF;
			END IF;
		END WHILE;
		CLOSE les_plats;
	END IF;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_insert_stock_menus)

trigger_update_stock_menus = DDL('''
CREATE TRIGGER trg_update_stock_menus
BEFORE UPDATE ON appartenir_menus
FOR EACH ROW
BEGIN
	DECLARE fini INT DEFAULT 0;
	DECLARE plat_id INT;
	DECLARE les_plats CURSOR FOR
		SELECT id_plat FROM contenir WHERE id_menu = NEW.id_menu;

	DECLARE CONTINUE HANDLER FOR NOT FOUND SET fini = 1;

	IF (SELECT statut FROM commandes WHERE id_commande = NEW.id_commande) != 'En commande' THEN
		OPEN les_plats; -- Le curseur doit être ouvert après la condition IF
		WHILE not fini do
			FETCH les_plats INTO plat_id;
			IF not fini THEN
				IF (SELECT stock FROM definir_stock WHERE id_plat = plat_id and jour = (select DATE(date_commande) from commandes where id_commande = NEW.id_commande)) + OLD.quantite - NEW.quantite >= 0 THEN
					UPDATE definir_stock SET stock = stock + OLD.quantite - NEW.quantite WHERE id_plat = plat_id and jour = (select DATE(date_commande) from commandes where id_commande = NEW.id_commande);
				ELSE
					SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='Stock insuffisant pour commander le menu';
				END IF;
			END IF;
		END WHILE;
		CLOSE les_plats; -- Le curseur doit être fermé avant la fin du bloc IF
	END IF;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_update_stock_menus)

# * triggers gestion commande sur_place
trigger_insert_commande_sur_place = DDL('''
CREATE TRIGGER trg_insert_commande_sur_place
BEFORE INSERT ON commandes
FOR EACH ROW
BEGIN
	if (select sum(nombre_personnes) from commandes where DATE(date_commande) = DATE(NEW.date_commande) and sur_place = 1 and HOUR(date_commande) = HOUR(NEW.date_commande)) + NEW.nombre_personnes > 12 then
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nombre maximum de personnes dépassé';
	end if;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_insert_commande_sur_place)

trigger_update_commande_sur_place = DDL('''
CREATE TRIGGER trg_update_commande_sur_place
BEFORE UPDATE ON commandes
FOR EACH ROW
BEGIN
	if (select sum(nombre_personnes) from commandes where DATE(date_commande) = DATE(NEW.date_commande) and sur_place = 1 and HOUR(date_commande) = HOUR(NEW.date_commande)) + NEW.nombre_personnes > 12 then
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nombre maximum de personnes dépassé';
	end if;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_update_commande_sur_place)

# * triggers calcule montant total plats
trigger_insert_calcule_montant_total_plats = DDL('''
CREATE TRIGGER trg_calcule_montant_total_plats
AFTER INSERT ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (SELECT statut FROM commandes WHERE id_commande = NEW.id_commande) != 'En commande' THEN
		UPDATE commandes
		SET montant_total = montant_total + ((select prix from plats where id_plat = NEW.id_plat) * NEW.quantite)
		WHERE id_commande = NEW.id_commande;
	END IF;
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_insert_calcule_montant_total_plats)

trigger_update_calcule_montant_total_plats = DDL('''
CREATE TRIGGER trg_update_calcule_montant_total_plats
AFTER UPDATE ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (SELECT statut FROM commandes WHERE id_commande = OLD.id_commande) != 'En commande' THEN
		UPDATE commandes
		SET montant_total = montant_total - ((select prix from plats where id_plat = OLD.id_plat) * OLD.quantite) + ((select prix from plats where id_plat = NEW.id_plat) * NEW.quantite)
		WHERE id_commande = NEW.id_commande;
	END IF;
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_update_calcule_montant_total_plats)

trigger_delete_calcule_montant_total_plats = DDL('''
CREATE TRIGGER trg_delete_calcule_montant_total_plats
AFTER DELETE ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (SELECT statut FROM commandes WHERE id_commande = OLD.id_commande) != 'En commande' THEN
		UPDATE commandes
		SET montant_total = montant_total - ((select prix from plats where id_plat = OLD.id_plat) * OLD.quantite)
		WHERE id_commande = OLD.id_commande;
	END IF;
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_delete_calcule_montant_total_plats)

# * triggers calcule montant total menus
trigger_insert_calcule_montant_total_menus = DDL('''
CREATE TRIGGER trg_insert_calcule_montant_total_menus
AFTER INSERT ON appartenir_menus
FOR EACH ROW
BEGIN
	IF (SELECT statut FROM commandes WHERE id_commande = NEW.id_commande) != 'En commande' THEN
		UPDATE commandes
		SET montant_total = montant_total + ((select prix from menu where id_menu = NEW.id_menu) * NEW.quantite)
		WHERE id_commande = NEW.id_commande;
	END IF;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_insert_calcule_montant_total_menus)

trigger_update_calcule_montant_total_menus = DDL('''
CREATE TRIGGER trg_update_calcule_montant_total_menus
AFTER UPDATE ON appartenir_menus
FOR EACH ROW
BEGIN
	IF (SELECT statut FROM commandes WHERE id_commande = OLD.id_commande) != 'En commande' THEN
		UPDATE commandes
		SET montant_total = montant_total - ((select prix from menu where id_menu = OLD.id_menu) * OLD.quantite) + ((select prix from menu where id_menu = NEW.id_menu) * NEW.quantite)
		WHERE id_commande = NEW.id_commande;
	END IF;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_update_calcule_montant_total_menus)

trigger_delete_calcule_montant_total_menus = DDL('''
CREATE TRIGGER trg_delete_calcule_montant_total_menus
AFTER DELETE ON appartenir_menus
FOR EACH ROW
BEGIN
	IF (SELECT statut FROM commandes WHERE id_commande = OLD.id_commande) != 'En commande' THEN
		UPDATE commandes
		SET montant_total = montant_total - ((select prix from menu where id_menu = OLD.id_menu) * OLD.quantite)
		WHERE id_commande = OLD.id_commande;
	END IF;
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