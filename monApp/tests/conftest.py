import os
import pytest
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import text, event
from unittest.mock import patch
from hashlib import sha256
from monApp import app,db
from monApp.models import (
        CATEGORIE, PLAT, CLIENT, COMMANDE, MENU,
        CONTENIR, APPARTENIR_PLATS, APPARTENIR_MENUS, AVIS, DEFINIR_STOCK
    )

@pytest.fixture(scope='session')
def testapp():
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI":'mysql+pymysql://lubin:lubin@servinfo-maria:3306/DBlubin?charset=utf8mb4',
        "WTF_CSRF_ENABLED": False
    })

    class MockDate(date):
        @classmethod
        def today(cls):
            return date(2025, 10, 21)
    
    patcher = patch('monApp.views.date', MockDate)
    patcher.start()

    with app.app_context():
        @event.listens_for(db.engine, "connect")
        def set_mysql_timestamp(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("SET TIMESTAMP = 1761048000")
            cursor.close()

        with db.engine.connect() as connection:
            connection.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            db.metadata.drop_all(bind=connection)
            connection.execute(text("SET FOREIGN_KEY_CHECKS=1"))
            connection.commit()
        db.create_all()
        today = date(2025, 10, 21)
        cats = [
            CATEGORIE(id_categorie=1, nom_categorie='Entrées'),
            CATEGORIE(id_categorie=2, nom_categorie='Plats principaux'),
            CATEGORIE(id_categorie=3, nom_categorie='Accompagnements'),
            CATEGORIE(id_categorie=4, nom_categorie='Desserts'),
            CATEGORIE(id_categorie=5, nom_categorie='Boissons'),
        ]
        db.session.add_all(cats)
        db.session.commit()

        plats = [
            PLAT(id_plat=1, id_categorie=1, nom_plat='Nems au porc', description='Nems croustillants', prix=Decimal('5.50'), disponible=True),
            PLAT(id_plat=2, id_categorie=1, nom_plat='Raviolis vapeur', description='Raviolis poulet', prix=Decimal('6.00'), disponible=True),
            PLAT(id_plat=3, id_categorie=2, nom_plat='Canard laqué', description='Canard mariné et laqué', prix=Decimal('12.00'), disponible=True),
            PLAT(id_plat=4, id_categorie=2, nom_plat='Poulet sauté', description='Poulet au gingembre', prix=Decimal('9.50'), disponible=True),
            PLAT(id_plat=5, id_categorie=3, nom_plat='Riz cantonais', description='Riz sauté', prix=Decimal('4.50'), disponible=True),
            PLAT(id_plat=6, id_categorie=3, nom_plat='Nouilles sautées', description='Nouilles aux légumes', prix=Decimal('4.00'), disponible=True),
            PLAT(id_plat=7, id_categorie=4, nom_plat='Perles de coco', description='Dessert sucré', prix=Decimal('3.00'), disponible=True),
            PLAT(id_plat=8, id_categorie=5, nom_plat='Thé jasmin', description='Thé parfumé', prix=Decimal('1.80'), disponible=True),
            PLAT(id_plat=9, id_categorie=2, nom_plat='Boeuf aux oignons', description='Bœuf tendre', prix=Decimal('10.00'), disponible=True),
        ]
        db.session.add_all(plats)
        db.session.commit()

        stocks = [
            DEFINIR_STOCK(id_plat=1, jour=today, stock=40),
            DEFINIR_STOCK(id_plat=2, jour=today, stock=30),
            DEFINIR_STOCK(id_plat=3, jour=today, stock=15),
            DEFINIR_STOCK(id_plat=4, jour=today, stock=25),
            DEFINIR_STOCK(id_plat=5, jour=today, stock=10),
            DEFINIR_STOCK(id_plat=6, jour=today, stock=20),
            DEFINIR_STOCK(id_plat=7, jour=today, stock=50),
            DEFINIR_STOCK(id_plat=8, jour=today, stock=100),
            DEFINIR_STOCK(id_plat=9, jour=today, stock=18),
        ]
        db.session.add_all(stocks)
        db.session.commit()

        def hash_pwd(pwd):
            m = sha256()
            m.update(pwd.encode())
            return m.hexdigest()

        clients = [
            CLIENT(id_client=1, nom='Dupont', prenom='Alice', telephone='0601020304', mot_de_passe=hash_pwd('password'), banni=False, role='user'),
            CLIENT(id_client=2, nom='Martin', prenom='Bob', telephone='0602030405', mot_de_passe=hash_pwd('password'), banni=False, role='user'),
            CLIENT(id_client=3, nom='Nguyen', prenom='Chau', telephone='0603040506', mot_de_passe=hash_pwd('password'), banni=False, role='user'),
            CLIENT(id_client=4, nom='Zhang', prenom='Wei', telephone='0604050607', mot_de_passe=hash_pwd('password'), banni=False, role='user'),
            CLIENT(id_client=5, nom='Garcia', prenom='Luis', telephone='0605060708', mot_de_passe=hash_pwd('password'), banni=False, role='user'),
            CLIENT(id_client=100, nom='Admin', prenom='System', telephone='admin', mot_de_passe=hash_pwd('admin'), banni=False, role='admin'),
        ]
        db.session.add_all(clients)
        db.session.commit()

        menus = [
            MENU(id_menu=1, nom_menu='Menu Canard', description='Entrée + Canard + Dessert', prix=Decimal('18.00')),
            MENU(id_menu=2, nom_menu='Menu Crevettes', description='Entrée + Crevettes + Riz', prix=Decimal('17.50')),
            MENU(id_menu=3, nom_menu='Menu Végétarien', description='Entrée + Nouilles + Dessert', prix=Decimal('14.00')),
        ]
        db.session.add_all(menus)
        db.session.commit()

        contenir_rows = [
            CONTENIR(id_menu=1, id_plat=1),
            CONTENIR(id_menu=1, id_plat=3),
            CONTENIR(id_menu=1, id_plat=7),
            CONTENIR(id_menu=2, id_plat=2),
            CONTENIR(id_menu=2, id_plat=5),
            CONTENIR(id_menu=2, id_plat=9),
            CONTENIR(id_menu=3, id_plat=2),
            CONTENIR(id_menu=3, id_plat=6),
            CONTENIR(id_menu=3, id_plat=7),
        ]
        db.session.add_all(contenir_rows)
        db.session.commit()

        commandes = [
            COMMANDE(id_commande=1, id_client=1, date_commande=datetime(today.year, today.month, today.day, 12, 0, 0), statut='En commande', montant_total=Decimal('0.00'), sur_place=False, nombre_personnes=1),
            COMMANDE(id_commande=2, id_client=2, date_commande=datetime(today.year, today.month, today.day, 12, 0, 0), statut='En commande', montant_total=Decimal('0.00'), sur_place=True, nombre_personnes=4),
            COMMANDE(id_commande=3, id_client=3, date_commande=datetime(today.year, today.month, today.day, 13, 0, 0), statut='En commande', montant_total=Decimal('0.00'), sur_place=False, nombre_personnes=2),
            COMMANDE(id_commande=4, id_client=4, date_commande=datetime(today.year, today.month, today.day, 13, 0, 0), statut='En commande', montant_total=Decimal('0.00'), sur_place=True, nombre_personnes=2),
        ]
        db.session.add_all(commandes)
        db.session.commit()

        lignes = [
            APPARTENIR_PLATS(id_commande=1, id_plat=1, quantite=2),
            APPARTENIR_PLATS(id_commande=1, id_plat=5, quantite=1),
            APPARTENIR_PLATS(id_commande=2, id_plat=3, quantite=2),
            APPARTENIR_PLATS(id_commande=2, id_plat=1, quantite=4),
            APPARTENIR_PLATS(id_commande=3, id_plat=2, quantite=3),
        ]
        db.session.add_all(lignes)
        db.session.commit()

        menu_lines = [
            APPARTENIR_MENUS(id_commande=4, id_menu=2, quantite=2, id_entree=2, id_plat_choisi=9, id_dessert=5),
            APPARTENIR_MENUS(id_commande=3, id_menu=3, quantite=1, id_entree=2, id_plat_choisi=6, id_dessert=7),
        ]
        db.session.add_all(menu_lines)
        db.session.commit()

        avis = [
            AVIS(id_avis=1, id_client=1, note=5, commentaire='Très bon service'),
            AVIS(id_avis=2, id_client=2, note=4, commentaire='Plats savoureux'),
        ]
        db.session.add_all(avis)
        db.session.commit()
    
    yield app
    patcher.stop()

@pytest.fixture
def client(testapp):
    return testapp.test_client()    


def pytest_sessionfinish(session, exitstatus):
    os.system("flask loaddb monApp/data/data.yml")