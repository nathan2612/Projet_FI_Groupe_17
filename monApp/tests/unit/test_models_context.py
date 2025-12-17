from datetime import date
from monApp.models import (
        CATEGORIE, PLAT, CLIENT, COMMANDE, MENU,
        CONTENIR, APPARTENIR_PLATS, APPARTENIR_MENUS, AVIS, DEFINIR_STOCK
    )
from monApp import db

def test_client_repr(testapp):
    client = CLIENT(id_client=1, nom='Dupont', prenom='Alice')
    assert repr(client) == "<Client Dupont Alice (1)>"

def test_plat_repr(testapp):
    plat = PLAT(id_plat=1, nom_plat='Nems au porc')
    assert repr(plat) == "<Plat Nems au porc (1)>"

def test_commande_repr(testapp):
    commande = COMMANDE(id_commande=1, id_client=1, statut='En commande')
    assert repr(commande) == "<Commande 1 client=1 statut=En commande>"

def test_menu_repr(testapp):
    menu = MENU(id_menu=1, nom_menu='Menu Canard')
    assert repr(menu) == "<Menu Menu Canard (1)>"

def test_avis_repr(testapp):
    avis = AVIS(id_avis=1, id_client=1, note=5)
    assert repr(avis) == "<Avis 1 client=1 note=5>"

def test_contenir_repr(testapp):
    contenir = CONTENIR(id_menu=1, id_plat=1, type_plat=1)
    assert repr(contenir) == "<Contenir menu=1 plat=1 type_plat=plat>"

def test_appartenir_plats_repr(testapp):
    appartenir_plats = APPARTENIR_PLATS(id_commande=1, id_plat=1, quantite=2)
    assert repr(appartenir_plats) == "<AppartenirPlats commande=1 plat=1 qty=2>"

def test_appartenir_menus_repr(testapp):
    appartenir_menus = APPARTENIR_MENUS(id_commande=4, id_menu=2, quantite=2, id_entree=2, id_plat_choisi=9, id_dessert=5)
    assert repr(appartenir_menus) == "<AppartenirMenus commande=4 menu=2 qty=2 entree=2 plat=9 dessert=5>"

def test_definir_stock_repr(testapp):
    today = date(2025, 10, 21)
    definir_stock = DEFINIR_STOCK(id_plat=1, jour=today, stock=34)
    assert repr(definir_stock) == f"<DefinirStock plat=1 jour={today} stock=34>"

def test_categorie_repr(testapp):
    categorie = CATEGORIE(id_categorie=1, nom_categorie='Entrées')
    assert repr(categorie) == "<Categorie Entrées (1)>"