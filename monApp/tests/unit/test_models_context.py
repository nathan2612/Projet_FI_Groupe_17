from datetime import date
from monApp.models import (
        CATEGORIE, PLAT, CLIENT, COMMANDE, MENU,
        CONTENIR, APPARTENIR_PLATS, APPARTENIR_MENUS, AVIS, DEFINIR_STOCK
    )
from monApp import db

def test_client_repr(testapp): #testapp est la fixture définie dans conftest.py
    with testapp.app_context():
        client = db.session.get(CLIENT, 1)
        assert repr(client) == "<Client Dupont Alice (1)>"

def test_plat_repr(testapp):
    with testapp.app_context():
        plat = db.session.get(PLAT, 1)
        assert repr(plat) == "<Plat Nems au porc (1)>"

def test_commande_repr(testapp):
    with testapp.app_context():
        commande = db.session.get(COMMANDE, 1)
        assert repr(commande) == "<Commande 1 client=1 statut=En attente>"

def test_menu_repr(testapp):
    with testapp.app_context():
        menu = db.session.get(MENU, 1)
        assert repr(menu) == "<Menu Menu Canard (1)>"

def test_avis_repr(testapp):
    with testapp.app_context():
        avis = db.session.get(AVIS, 1)
        assert repr(avis) == "<Avis 1 client=1 note=5>"

def test_contenir_repr(testapp):
    with testapp.app_context():
        contenir = db.session.get(CONTENIR, (1, 1))
        assert repr(contenir) == "<Contenir menu=1 plat=1>"

def test_appartenir_plats_repr(testapp):
    with testapp.app_context():
        appartenir_plats = db.session.get(APPARTENIR_PLATS, (1, 1))
        assert repr(appartenir_plats) == "<AppartenirPlats commande=1 plat=1 qty=2>"

def test_appartenir_menus_repr(testapp):
    with testapp.app_context():
        appartenir_menus = db.session.get(APPARTENIR_MENUS, (4, 2))
        assert repr(appartenir_menus) == "<AppartenirMenus commande=4 menu=2 qty=2>"

def test_definir_stock_repr(testapp):
    with testapp.app_context():
        definir_stock = db.session.get(DEFINIR_STOCK, (1, date(2025,10,21)))
        assert repr(definir_stock) == "<DefinirStock plat=1 jour=2025-10-21 stock=34>"

def test_categorie_repr(testapp):
    with testapp.app_context():
        categorie = db.session.get(CATEGORIE, 1)
        assert repr(categorie) == "<Categorie Entrées (1)>"