import pytest
from datetime import datetime, date, timedelta
from sqlalchemy.exc import OperationalError
from monApp import db
from monApp.models import COMMANDE, DEFINIR_STOCK, APPARTENIR_PLATS,MENU,CONTENIR,APPARTENIR_MENUS,CLIENT

def test_trigger_stock_plats(testapp):
    with testapp.app_context():
        today = date(2025, 10, 21)
        stock = db.session.get(DEFINIR_STOCK, (1, today))
        stock_base = stock.stock

        cmd = COMMANDE(id_commande=999, id_client=None, date_commande=datetime(today.year, today.month, today.day, 12, 0, 0), statut='En commande', sur_place=True, nombre_personnes=1)
        db.session.merge(cmd)

        ds = DEFINIR_STOCK(id_plat=1, jour=cmd.date_commande.date(), stock=0)
        db.session.merge(ds)
        db.session.commit()

        ap = APPARTENIR_PLATS(id_commande=999, id_plat=1, quantite=1)
        db.session.add(ap)
        with pytest.raises(OperationalError) as excinfo:
            db.session.commit()
        db.session.rollback()
        assert 'Stock insuffisant' in str(excinfo.value)

        stock.stock = stock_base
        db.session.commit()

def test_trigger_stock_menus(testapp):
    with testapp.app_context():
        menu = MENU(id_menu=999, nom_menu='Menu Test', description='Menu pour test trigger', prix=25.00)
        today = date(2025, 10, 21)
        stock1 = db.session.get(DEFINIR_STOCK, (1, today))
        stock2 = db.session.get(DEFINIR_STOCK, (3, today))
        stock1_base = stock1.stock
        stock2_base = stock2.stock
        menu_plat1 = CONTENIR(id_menu=999, id_plat=1)
        menu_plat3 = CONTENIR(id_menu=999, id_plat=3)
        db.session.add(menu)
        db.session.add(menu_plat1)
        db.session.add(menu_plat3)
        db.session.commit()

        cmd = COMMANDE(id_commande=1000, id_client=None, date_commande=datetime(today.year, today.month, today.day, 13, 0, 0), statut='En commande', sur_place=True, nombre_personnes=1)
        db.session.merge(cmd)

        stock1.stock = 0
        stock2.stock = 0
        db.session.commit()

        am = APPARTENIR_MENUS(id_commande=1000, id_menu=999, quantite=1, id_entree=1, id_plat_choisi=3, id_dessert=None)
        db.session.add(am)
        with pytest.raises(OperationalError) as excinfo:
            db.session.commit()
        db.session.rollback()
        assert 'Stock insuffisant' in str(excinfo.value)

        stock1.stock = stock1_base
        stock2.stock = stock2_base
        db.session.commit()

def test_trigger_commande_sur_place(testapp):
    with testapp.app_context():
        tomorrow = date(2025, 10, 21) + timedelta(days=1)
        cmd1 = COMMANDE(id_commande=1001, id_client=None, date_commande=datetime(tomorrow.year, tomorrow.month, tomorrow.day, 12, 0, 0), statut='En commande', sur_place=True, nombre_personnes=8)
        cmd2 = COMMANDE(id_commande=1002, id_client=None, date_commande=datetime(tomorrow.year, tomorrow.month, tomorrow.day, 13, 0, 0), statut='En commande', sur_place=True, nombre_personnes=8)
        cmd3 = COMMANDE(id_commande=1003, id_client=None, date_commande=datetime(tomorrow.year, tomorrow.month, tomorrow.day, 13, 0, 0), statut='En commande', sur_place=True, nombre_personnes=5)
        db.session.add(cmd1)
        db.session.add(cmd2)
        db.session.add(cmd3)
        db.session.commit()

def test_trigger_calcul_commandes_plats(testapp):
    with testapp.app_context():
        today = date(2025, 10, 21)
        cmd = COMMANDE(id_commande=2000, id_client=None, date_commande=datetime(today.year, today.month, today.day, 12, 0, 0), statut='En commande', sur_place=False, nombre_personnes=1)
        db.session.add(cmd)
        db.session.commit()

        stock1 = db.session.get(DEFINIR_STOCK, (1, today))
        stock2 = db.session.get(DEFINIR_STOCK, (2, today))
        stock1_base = stock1.stock
        stock2_base = stock2.stock
        ap1 = APPARTENIR_PLATS(id_commande=2000, id_plat=1, quantite=2)
        ap2 = APPARTENIR_PLATS(id_commande=2000, id_plat=2, quantite=1)
        db.session.add(ap1)
        db.session.add(ap2)
        db.session.commit()

        commande = db.session.get(COMMANDE, 2000)
        assert commande.montant_total == 17.00

        ap1.quantite = 1
        db.session.commit()
        assert commande.montant_total == 11.50

        db.session.delete(ap1)
        db.session.commit()
        assert commande.montant_total == 6.00

        stock1.stock = stock1_base
        stock2.stock = stock2_base
        db.session.commit()

def test_trigger_calcul_commandes_menus_insert(testapp):
    with testapp.app_context():
        menu = MENU(id_menu=1004, nom_menu='Menu Test', description='Menu pour test trigger', prix=25.00)
        today = date(2025, 10, 21)
        stock1 = db.session.get(DEFINIR_STOCK, (1, today))
        stock2 = db.session.get(DEFINIR_STOCK, (3, today))
        stock1_base = stock1.stock
        stock2_base = stock2.stock
        menu_plat1 = CONTENIR(id_menu=1004, id_plat=1)
        menu_plat3 = CONTENIR(id_menu=1004, id_plat=3)
        db.session.add(menu)
        db.session.add(menu_plat1)
        db.session.add(menu_plat3)
        db.session.commit()

        cmd = COMMANDE(id_commande=2001, id_client=None, date_commande=datetime(today.year, today.month, today.day, 13, 0, 0), statut='En commande', sur_place=False, nombre_personnes=1)
        db.session.add(cmd)
        db.session.commit()

        am = APPARTENIR_MENUS(id_commande=2001, id_menu=1004, quantite=2, id_entree=1, id_plat_choisi=3, id_dessert=7)
        db.session.add(am)
        db.session.commit()
        assert cmd.montant_total == 50.00

        am.quantite = 1
        db.session.commit()
        assert cmd.montant_total == 25.00

        db.session.delete(am)
        db.session.commit()
        assert cmd.montant_total == 0.00

        stock1.stock = stock1_base
        stock2.stock = stock2_base
        db.session.commit()

def test_trigger_client_banni(testapp):
    with testapp.app_context():
        client = db.session.get(CLIENT, 1)
        client.banni = True
        db.session.commit()
        today = date(2025, 10, 21)
        cmd = COMMANDE(id_commande=3000, id_client=1, date_commande=datetime(today.year, today.month, today.day, 12, 0, 0), statut='En commande', sur_place=False, nombre_personnes=1)
        db.session.add(cmd)
        with pytest.raises(OperationalError) as excinfo:
            db.session.commit()
        db.session.rollback()
        assert 'Client banni ne peut pas passer de commande' in str(excinfo.value)

        client.banni = False
        db.session.commit()

def test_trigger_heure_reservation(testapp):
    with testapp.app_context():
        today = date(2025, 10, 21)
        cmd = COMMANDE(id_commande=4000, id_client=None, date_commande=datetime(today.year, today.month, today.day, 19, 0, 0), statut='En commande', sur_place=True, nombre_personnes=2)
        db.session.add(cmd)
        with pytest.raises(OperationalError) as excinfo:
            db.session.commit()
        db.session.rollback()
        assert 'chk_heure_valide' in str(excinfo.value)
