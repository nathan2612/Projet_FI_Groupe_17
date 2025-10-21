from flask_sqlalchemy import SQLAlchemy
from datetime import date, time
from .app import db
from sqlalchemy import event, DDL

class CATEGORIE(db.Model):
	__tablename__ = 'categories'
	id_categorie = db.Column(db.Integer, primary_key=True)
	nom_categorie = db.Column(db.String(100))
	description = db.Column(db.Text)

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
	stock_reservation = db.Column(db.Integer)
	stock_directe = db.Column(db.Integer)
	disponible = db.Column(db.Boolean, default=True)

	categorie = db.relationship('CATEGORIE', back_populates='plats')
	recettes = db.relationship('DEFINIR_STOCK', back_populates='plat')
	details_commandes = db.relationship('APPARTENIR_PLATS', back_populates='plat')
	contenirs = db.relationship('CONTENIR', back_populates='plat')

	def __repr__(self):
		return f"<Plat {self.nom_plat} ({self.id_plat})>"


class CLIENT(db.Model):
	__tablename__ = 'clients'
	id_client = db.Column(db.Integer, primary_key=True)
	nom_client = db.Column(db.String(100))
	prenom_client = db.Column(db.String(100))
	telephone = db.Column(db.String(15))
	banni = db.Column(db.Boolean, default=False)

	commandes = db.relationship('COMMANDE', back_populates='client')
	avis = db.relationship('AVIS', back_populates='client')

	def __repr__(self):
		return f"<Client {self.nom_client} {self.prenom_client} ({self.id_client})>"

class COMMANDE(db.Model):
	__tablename__ = 'commandes'
	id_commande = db.Column(db.Integer, primary_key=True)
	id_client = db.Column(db.Integer, db.ForeignKey('clients.id_client'))
	date_commande = db.Column(db.Date)
	statut = db.Column(db.String(50), default='En attente')
	montant_total = db.Column(db.Numeric(10, 2),default=0.00)
	sur_place = db.Column(db.Boolean, default=False)
	nombre_personnes = db.Column(db.Integer)

	__table_args__ = (
		db.CheckConstraint('nombre_personnes <= 12', name='chk_nombre_personnes'),
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

	plat = db.relationship('PLAT', back_populates='recettes')

	def __repr__(self):
		return f"<DefinirStock plat={self.id_plat} jour={self.jour} stock={self.stock}>"
	

# DDL trigger creation for MySQL/MariaDB: create trigger after table creation
trigger_insert_stock_plats = DDL('''
CREATE TRIGGER trg_insert_stock_plats
BEFORE INSERT ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (select sur_place from commandes where id_commande = NEW.id_commande) THEN
		IF (SELECT stock_reservation FROM plats WHERE id_plat = NEW.id_plat) - NEW.quantite >= 0 THEN
			UPDATE plats SET stock_reservation = stock_reservation - NEW.quantite WHERE id_plat = NEW.id_plat;
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour le plat';
		END IF;
	ELSE
		IF (SELECT stock_directe FROM plats WHERE id_plat = NEW.id_plat) - NEW.quantite >= 0 THEN
			UPDATE plats SET stock_directe = stock_directe - NEW.quantite WHERE id_plat = NEW.id_plat;
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour le plat';
		END IF;
	END IF;
END;''')

event.listen(APPARTENIR_PLATS.__table__, 'after_create', trigger_insert_stock_plats)

trigger_update_stock_plats = DDL('''
CREATE TRIGGER trg_update_stock_plats
BEFORE UPDATE ON appartenir_plats
FOR EACH ROW
BEGIN
	IF (select sur_place from commandes where id_commande = NEW.id_commande) THEN
		IF (SELECT stock_reservation FROM plats WHERE id_plat = NEW.id_plat) - NEW.quantite >= 0 THEN
			UPDATE plats SET stock_reservation = stock_reservation - NEW.quantite WHERE id_plat = NEW.id_plat;
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour le plat';
		END IF;
	ELSE
		IF (SELECT stock_directe FROM plats WHERE id_plat = NEW.id_plat) - NEW.quantite >= 0 THEN
			UPDATE plats SET stock_directe = stock_directe - NEW.quantite WHERE id_plat = NEW.id_plat;
		ELSE
			SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour le plat';
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

	OPEN les_plats;
	read_loop: LOOP
		FETCH les_plats INTO plat_id;
		IF fini = 1 THEN
			LEAVE read_loop;
		END IF;
		IF (select sur_place from commandes where id_commande = NEW.id_commande) THEN
			IF (SELECT stock_reservation FROM plats WHERE id_plat = plat_id) - NEW.quantite >= 0 THEN
				UPDATE plats SET stock_reservation = stock_reservation - NEW.quantite WHERE id_plat = plat_id;
			ELSE
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour le plat';
			END IF;
		ELSE
			IF (SELECT stock_directe FROM plats WHERE id_plat = plat_id) - NEW.quantite >= 0 THEN
				UPDATE plats SET stock_directe = stock_directe - NEW.quantite WHERE id_plat = plat_id;
			ELSE
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour le plat';
			END IF;
		END IF;
	END LOOP;
	CLOSE les_plats;
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

	OPEN les_plats;
	read_loop: LOOP
		FETCH les_plats INTO plat_id;
		IF fini = 1 THEN
			LEAVE read_loop;
		END IF;
		IF (select sur_place from commandes where id_commande = NEW.id_commande) THEN
			IF (SELECT stock_reservation FROM plats WHERE id_plat = plat_id) - NEW.quantite >= 0 THEN
				UPDATE plats SET stock_reservation = stock_reservation - NEW.quantite WHERE id_plat = plat_id;
			ELSE
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour le plat';
			END IF;
		ELSE
			IF (SELECT stock_directe FROM plats WHERE id_plat = plat_id) - NEW.quantite >= 0 THEN
				UPDATE plats SET stock_directe = stock_directe - NEW.quantite WHERE id_plat = plat_id;
			ELSE
				SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Stock insuffisant pour le plat';
			END IF;
		END IF;
	END LOOP;
	CLOSE les_plats;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_update_stock_menus)

trigger_insert_commande = DDL('''
CREATE TRIGGER trg_insert_commande
BEFORE INSERT ON commandes
FOR EACH ROW
BEGIN
	if (select sum(nombre_personnes) from commandes where date_commande = NEW.date_commande and sur_place = 1) + NEW.nombre_personnes > 12 then
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nombre maximum de personnes dépassé';
	end if;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_insert_commande)

trigger_update_commande = DDL('''
CREATE TRIGGER trg_update_commande
BEFORE UPDATE ON commandes
FOR EACH ROW
BEGIN
	if (select sum(nombre_personnes) from commandes where date_commande = NEW.date_commande and sur_place = 1) + NEW.nombre_personnes > 12 then
		SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Nombre maximum de personnes dépassé';
	end if;
END;''')

event.listen(APPARTENIR_MENUS.__table__, 'after_create', trigger_update_commande)

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