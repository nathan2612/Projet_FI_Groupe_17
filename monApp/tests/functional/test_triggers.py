import pytest
from datetime import datetime,date
from sqlalchemy.exc import OperationalError
from monApp import db
from monApp.models import COMMANDE, DEFINIR_STOCK, APPARTENIR_PLATS,MENU,CONTENIR,APPARTENIR_MENUS,CLIENT

# Remarque : j'utilise app.app_context() via la fixture testapp déjà existante
def test_trigger_stock_plats(testapp):
    with testapp.app_context():
        stock = db.session.get(DEFINIR_STOCK, (1, date(2025,10,21)))
        stock_base = stock.stock

        # Prépare état propre (create_all/drop_all est fait par la fixture testapp dans ton conftest.py)
        # Create a commande for that date and mark sur_place True
        cmd = COMMANDE(id_commande=999, id_client=None, date_commande=datetime(2025,10,21,12,00,0), statut='En commande', sur_place=True, nombre_personnes=1)
        db.session.merge(cmd)

        # definir_stock with stock 1 (success case)
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
        stock1 = db.session.get(DEFINIR_STOCK, (1, date(2025,10,21)))
        stock2 = db.session.get(DEFINIR_STOCK, (3, date(2025,10,21)))
        stock1_base = stock1.stock
        stock2_base = stock2.stock
        menu_plat1 = CONTENIR(id_menu=999, id_plat=1)
        menu_plat3 = CONTENIR(id_menu=999, id_plat=3)
        db.session.add(menu)
        db.session.add(menu_plat1)
        db.session.add(menu_plat3)
        db.session.commit()

        cmd = COMMANDE(id_commande=1000, id_client=None, date_commande=datetime(2025,10,21,13,00,0), statut='En commande', sur_place=True, nombre_personnes=1)
        db.session.merge(cmd)

        stock1.stock = 0
        stock2.stock = 0
        db.session.commit()

        am = APPARTENIR_MENUS(id_commande=1000, id_menu=999, quantite=1)
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
        cmd1 = COMMANDE(id_commande=1001, id_client=None, date_commande=datetime(2025,10,22,12,00,0), statut='En commande', sur_place=True, nombre_personnes=8)
        cmd2 = COMMANDE(id_commande=1002, id_client=None, date_commande=datetime(2025,10,22,13,00,0), statut='En commande', sur_place=True, nombre_personnes=8)
        cmd3 = COMMANDE(id_commande=1003, id_client=None, date_commande=datetime(2025,10,22,13,00,0), statut='En commande', sur_place=True, nombre_personnes=5)
        db.session.add(cmd1)
        db.session.add(cmd2)
        db.session.add(cmd3)
        with pytest.raises(OperationalError) as excinfo:
            db.session.commit()
        db.session.rollback()
        assert 'Nombre maximum de personnes dépassé' in str(excinfo.value)

def test_trigger_calcul_commandes_plats(testapp):
    with testapp.app_context():
        cmd = COMMANDE(id_commande=2000, id_client=None, date_commande=datetime(2025,10,21,12,00,0), statut='En commande', sur_place=False, nombre_personnes=1)
        db.session.add(cmd)
        db.session.commit()

        stock1 = db.session.get(DEFINIR_STOCK, (1, date(2025,10,21)))
        stock2 = db.session.get(DEFINIR_STOCK, (2, date(2025,10,21)))
        stock1_base = stock1.stock
        stock2_base = stock2.stock
        ap1 = APPARTENIR_PLATS(id_commande=2000, id_plat=1, quantite=2)  # Prix plat 1 = 5.50
        ap2 = APPARTENIR_PLATS(id_commande=2000, id_plat=2, quantite=1)  # Prix plat 2 = 6.00
        db.session.add(ap1)
        db.session.add(ap2)
        db.session.commit()

        commande = db.session.get(COMMANDE, 2000)
        assert commande.montant_total == 17.00  # 2*5.50 + 1*6.00 = 17.00

        ap1.quantite = 1
        db.session.commit()
        assert commande.montant_total == 11.50  # 1*5.50 + 1*6.00 = 11.50

        db.session.delete(ap1)
        db.session.commit()
        assert commande.montant_total == 6.00

        stock1.stock = stock1_base
        stock2.stock = stock2_base
        db.session.commit()

def test_trigger_calcul_commandes_menus_insert(testapp):
    with testapp.app_context():
        menu = MENU(id_menu=1004, nom_menu='Menu Test', description='Menu pour test trigger', prix=25.00)
        stock1 = db.session.get(DEFINIR_STOCK, (1, date(2025,10,21)))
        stock2 = db.session.get(DEFINIR_STOCK, (3, date(2025,10,21)))
        stock1_base = stock1.stock
        stock2_base = stock2.stock
        menu_plat1 = CONTENIR(id_menu=1004, id_plat=1)
        menu_plat3 = CONTENIR(id_menu=1004, id_plat=3)
        db.session.add(menu)
        db.session.add(menu_plat1)
        db.session.add(menu_plat3)
        db.session.commit()

        cmd = COMMANDE(id_commande=2001, id_client=None, date_commande=datetime(2025,10,21,13,00,0), statut='En commande', sur_place=False, nombre_personnes=1)
        db.session.add(cmd)
        db.session.commit()

        am = APPARTENIR_MENUS(id_commande=2001, id_menu=1004, quantite=2)  # Prix menu = 25.00
        db.session.add(am)
        db.session.commit()
        assert cmd.montant_total == 50.00  # 2*25.00 = 50.00

        am.quantite = 1
        db.session.commit()
        assert cmd.montant_total == 25.00  # 1*25.00 = 25.00

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
        cmd = COMMANDE(id_commande=3000, id_client=1, date_commande=datetime(2025,10,23,12,00,0), statut='En commande', sur_place=False, nombre_personnes=1)
        db.session.add(cmd)
        with pytest.raises(OperationalError) as excinfo:
            db.session.commit()
        db.session.rollback()
        assert 'Client banni ne peut pas passer de commande' in str(excinfo.value)

        client.banni = False
        db.session.commit()

def test_trigger_heure_reservation(testapp):
    with testapp.app_context():
        cmd = COMMANDE(id_commande=4000, id_client=None, date_commande=datetime(2025,10,24,19,00,0), statut='En commande', sur_place=True, nombre_personnes=2)
        db.session.add(cmd)
        with pytest.raises(OperationalError) as excinfo:
            db.session.commit()
        db.session.rollback()
        assert 'chk_heure_valide' in str(excinfo.value)
