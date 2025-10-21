import pytest
from datetime import datetime,date
from sqlalchemy.exc import OperationalError
from monApp import db
from monApp.models import COMMANDE, DEFINIR_STOCK, APPARTENIR_PLATS,PLAT

# Remarque : j'utilise app.app_context() via la fixture testapp déjà existante
def test_trigger_decrement_and_failure(testapp):
    with testapp.app_context():
        stock = db.session.get(DEFINIR_STOCK, (1, date(2025,10,21)))
        stock_base = stock.stock

        # Prépare état propre (create_all/drop_all est fait par la fixture testapp dans ton conftest.py)
        # Create a commande for that date and mark sur_place True
        cmd = COMMANDE(id_commande=999, id_client=None, date_commande=datetime(2025,10,21,12,00,0), statut='En attente', sur_place=True, nombre_personnes=1)
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