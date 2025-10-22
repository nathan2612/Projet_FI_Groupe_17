from datetime import date
from monApp.models import (
        CATEGORIE, PLAT, CLIENT, COMMANDE, MENU,
        CONTENIR, APPARTENIR_PLATS, APPARTENIR_MENUS, AVIS, DEFINIR_STOCK
    )
from monApp import db

def test_categorie_init():
    cat = CATEGORIE(id_categorie=1, nom_categorie='Entrées', description='Plats d\'entrée')
    assert cat.id_categorie == 1
    assert cat.nom_categorie == 'Entrées'
    assert cat.description == 'Plats d\'entrée'

def test_plat_init():
    plat = PLAT(id_plat=1, id_categorie=1, nom_plat='Salade César', description='Salade avec poulet, croûtons et parmesan', prix=9.99, disponible=True)
    assert plat.id_plat == 1
    assert plat.id_categorie == 1
    assert plat.nom_plat == 'Salade César'
    assert plat.description == 'Salade avec poulet, croûtons et parmesan'
    assert plat.prix == 9.99
    assert plat.disponible is True

def test_client_init():
    client = CLIENT(id_client=1, nom_client='Doe', prenom_client='John', telephone='0123456789', banni=False)
    assert client.id_client == 1
    assert client.nom_client == 'Doe'
    assert client.prenom_client == 'John'
    assert client.telephone == '0123456789'
    assert client.banni is False
    assert client.get_id() == 1

def test_menu_init():
    menu = MENU(id_menu=1, nom_menu='Menu Déjeuner', description='Entrée + Plat + Dessert', prix=19.99)
    assert menu.id_menu == 1
    assert menu.nom_menu == 'Menu Déjeuner'
    assert menu.description == 'Entrée + Plat + Dessert'
    assert menu.prix == 19.99

def test_avis_init():
    avis = AVIS(id_avis=1, id_client=1, note=5, commentaire='Excellent plat!')
    assert avis.id_avis == 1
    assert avis.id_client == 1
    assert avis.note == 5
    assert avis.commentaire == 'Excellent plat!'

def test_commande_init():
    commande = COMMANDE(id_commande=1, id_client=1, date_commande='2024-01-01', statut='En cours', montant_total=29.99, sur_place=True, nombre_personnes=2)
    assert commande.id_commande == 1
    assert commande.id_client == 1
    assert commande.date_commande == '2024-01-01'
    assert commande.statut == 'En cours'
    assert commande.montant_total == 29.99
    assert commande.sur_place is True
    assert commande.nombre_personnes == 2

def test_contenir_init():
    contenir = CONTENIR(id_menu=1, id_plat=1)
    assert contenir.id_menu == 1
    assert contenir.id_plat == 1

def test_appartenir_plats_init():
    appartenir_plats = APPARTENIR_PLATS(id_commande=1, id_plat=1, quantite=2)
    assert appartenir_plats.id_commande == 1
    assert appartenir_plats.id_plat == 1
    assert appartenir_plats.quantite == 2

def test_appartenir_menus_init():
    appartenir_menus = APPARTENIR_MENUS(id_commande=1, id_menu=1, quantite=1)
    assert appartenir_menus.id_commande == 1
    assert appartenir_menus.id_menu == 1
    assert appartenir_menus.quantite == 1
def test_definir_stock_init():
    definir_stock = DEFINIR_STOCK(id_plat=1, jour=date(2024, 1, 1), stock=50)
    assert definir_stock.id_plat == 1
    assert definir_stock.jour == date(2024, 1, 1)
    assert definir_stock.stock == 50
    assert definir_stock.stock == 50



