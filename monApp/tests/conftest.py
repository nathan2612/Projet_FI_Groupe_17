import os
import pytest
from decimal import Decimal
from datetime import date, datetime
from monApp import app,db
from monApp.models import (
        CATEGORIE, PLAT, CLIENT, COMMANDE, MENU,
        CONTENIR, APPARTENIR_PLATS, APPARTENIR_MENUS, AVIS, DEFINIR_STOCK
    )

@pytest.fixture(scope='session')
def testapp():
    # Use a dedicated test database. You can override with TEST_DATABASE_URL env var.
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI":'mysql+pymysql://joubert:joubert@servinfo-maria:3306/DBjoubert?charset=utf8mb4',
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        # Ensure a clean slate on the target DB once per test session
        db.drop_all()
        db.create_all()
        # --- ORM seed data for tests ---
        # Categories
        cats = [
            CATEGORIE(id_categorie=1, nom_categorie='Entrées', description='Entrées froides et chaudes'),
            CATEGORIE(id_categorie=2, nom_categorie='Plats principaux', description='Plats mijotés et sautés'),
            CATEGORIE(id_categorie=3, nom_categorie='Accompagnements', description='Riz, légumes, sauces'),
            CATEGORIE(id_categorie=4, nom_categorie='Desserts', description='Douceurs et pâtisseries'),
            CATEGORIE(id_categorie=5, nom_categorie='Boissons', description='Boissons chaudes et froides'),
        ]
        db.session.add_all(cats)
        db.session.commit()

        # Plats
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

        # Definir_stock (per-day stock)
        stocks = [
            DEFINIR_STOCK(id_plat=1, jour=date(2025,10,21), stock=40),
            DEFINIR_STOCK(id_plat=2, jour=date(2025,10,21), stock=30),
            DEFINIR_STOCK(id_plat=3, jour=date(2025,10,21), stock=15),
            DEFINIR_STOCK(id_plat=4, jour=date(2025,10,21), stock=25),
            DEFINIR_STOCK(id_plat=5, jour=date(2025,10,21), stock=10),
            DEFINIR_STOCK(id_plat=6, jour=date(2025,10,21), stock=20),
            DEFINIR_STOCK(id_plat=7, jour=date(2025,10,21), stock=50),
            DEFINIR_STOCK(id_plat=8, jour=date(2025,10,21), stock=100),
            DEFINIR_STOCK(id_plat=9, jour=date(2025,10,21), stock=18),
        ]
        db.session.add_all(stocks)
        db.session.commit()

        # Clients
        clients = [
            CLIENT(id_client=1, nom_client='Dupont', prenom_client='Alice', telephone='0601020304', banni=False),
            CLIENT(id_client=2, nom_client='Martin', prenom_client='Bob', telephone='0602030405', banni=False),
            CLIENT(id_client=3, nom_client='Nguyen', prenom_client='Chau', telephone='0603040506', banni=False),
            CLIENT(id_client=4, nom_client='Zhang', prenom_client='Wei', telephone='0604050607', banni=False),
            CLIENT(id_client=5, nom_client='Garcia', prenom_client='Luis', telephone='0605060708', banni=False),
        ]
        db.session.add_all(clients)
        db.session.commit()

        # Menus
        menus = [
            MENU(id_menu=1, nom_menu='Menu Canard', description='Entrée + Canard + Dessert', prix=Decimal('18.00')),
            MENU(id_menu=2, nom_menu='Menu Crevettes', description='Entrée + Crevettes + Riz', prix=Decimal('17.50')),
            MENU(id_menu=3, nom_menu='Menu Végétarien', description='Entrée + Nouilles + Dessert', prix=Decimal('14.00')),
        ]
        db.session.add_all(menus)
        db.session.commit()

        # Contenir (menu compositions)
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

        # Commandes
        commandes = [
            COMMANDE(id_commande=1, id_client=1, date_commande=datetime(2025,10,21,12,00,0), statut='En attente', montant_total=Decimal('0.00'), sur_place=False, nombre_personnes=1),
            COMMANDE(id_commande=2, id_client=2, date_commande=datetime(2025,10,21,12,00,0), statut='En attente', montant_total=Decimal('0.00'), sur_place=True, nombre_personnes=4),
            COMMANDE(id_commande=3, id_client=3, date_commande=datetime(2025,10,21,13,00,0), statut='En attente', montant_total=Decimal('0.00'), sur_place=False, nombre_personnes=2),
            COMMANDE(id_commande=4, id_client=4, date_commande=datetime(2025,10,21,13,00,0), statut='En attente', montant_total=Decimal('0.00'), sur_place=True, nombre_personnes=2),
        ]
        db.session.add_all(commandes)
        db.session.commit()

        # Appartenir_plats (lignes de commande)
        lignes = [
            APPARTENIR_PLATS(id_commande=1, id_plat=1, quantite=2),
            APPARTENIR_PLATS(id_commande=1, id_plat=5, quantite=1),
            APPARTENIR_PLATS(id_commande=2, id_plat=3, quantite=2),
            APPARTENIR_PLATS(id_commande=2, id_plat=1, quantite=4),
            APPARTENIR_PLATS(id_commande=3, id_plat=2, quantite=3),
        ]
        db.session.add_all(lignes)
        db.session.commit()

        # Appartenir_menus
        menu_lines = [
            APPARTENIR_MENUS(id_commande=4, id_menu=2, quantite=2),
            APPARTENIR_MENUS(id_commande=3, id_menu=3, quantite=1),
        ]
        db.session.add_all(menu_lines)
        db.session.commit()

        # Avis
        avis = [
            AVIS(id_avis=1, id_client=1, note=5, commentaire='Très bon service'),
            AVIS(id_avis=2, id_client=2, note=4, commentaire='Plats savoureux'),
        ]
        db.session.add_all(avis)
        db.session.commit()
    yield app

@pytest.fixture
def client(testapp):
    return testapp.test_client()    


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finishes.
    Prints a short summary message (exit status and number of collected tests).
    """
    os.system("flask loaddb monApp/data/data.yml")