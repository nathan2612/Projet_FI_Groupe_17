import click
import logging as lg
from .app import app, db

@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    import yaml
    from datetime import datetime

    db.drop_all()
    db.create_all()

    with open(filename, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    from .models import (
        CATEGORIE, PLAT, CLIENT, COMMANDE, MENU,
        CONTENIR, APPARTENIR_PLATS, APPARTENIR_MENUS, AVIS, DEFINIR_STOCK
    )

    def parse_date(s):
        if s is None:
            return None
        if isinstance(s, datetime):
            return s.date()
        try:
            return datetime.strptime(s, '%Y-%m-%d').date()
        except Exception:
            return None

    def parse_time(s):
        if s is None:
            return None
        if isinstance(s, datetime):
            return s.time()
        try:
            return datetime.strptime(s, '%H:%M:%S').time()
        except Exception:
            return None

    for entry in data.get('categories', []) or []:
        obj = CATEGORIE(
            id_categorie=entry.get('id_categorie'),
            nom_categorie=entry.get('nom_categorie'),
            image_categorie=entry.get('image_categorie', 'default_categorie.png')
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('plats', []) or []:
        obj = PLAT(
            id_plat=entry.get('id_plat'),
            id_categorie=entry.get('id_categorie'),
            nom_plat=entry.get('nom_plat'),
            description=entry.get('description'),
            longue_description=entry.get('longue_description'),
            prix=entry.get('prix'),
            disponible=entry.get('disponible', True),
            image_url=entry.get('image_url', 'default_plat.png'),
            vegetarien=entry.get('vegetarien', False),
            vegan=entry.get('vegan', False),
            gluten=entry.get('gluten', False),
            lactose=entry.get('lactose', False),
            fruit_a_coque=entry.get('fruit_a_coque', False),
            crustaces=entry.get('crustaces', False)
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('definir_stock', []) or []:
        obj = DEFINIR_STOCK(
            id_plat=entry.get('id_plat'),
            jour=parse_date(entry.get('jour')),
            stock=entry.get('stock')
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('clients', []) or []:
        obj = CLIENT(
            id_client=entry.get('id_client'),
            nom=entry.get('nom'),
            prenom=entry.get('prenom'),
            telephone=entry.get('telephone'),
            mot_de_passe=entry.get('mot_de_passe'),
            banni=entry.get('banni', False),
            # Rôle de l'utilisateur : 'user' (par défaut) ou 'admin'
            role=entry.get('role', 'user')
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('menus', []) or []:
        obj = MENU(
            id_menu=entry.get('id_menu'),
            nom_menu=entry.get('nom_menu'),
            description=entry.get('description'),
            image_url=entry.get('image_url', 'default_menu.jpg'),
            prix=entry.get('prix')
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('contenir', []) or []:
        obj = CONTENIR(
            id_menu=entry.get('id_menu'),
            id_plat=entry.get('id_plat'),
            type_plat=entry.get('type_plat')
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('commandes', []) or []:
        obj = COMMANDE(
            id_commande=entry.get('id_commande'),
            id_client=entry.get('id_client'),
            date_commande=datetime.strptime(entry.get('date_commande'), '%Y-%m-%d %H:%M:%S'),
            statut=entry.get('statut'),
            montant_total=entry.get('montant_total'),
            sur_place=entry.get('sur_place'),
            nombre_personnes=entry.get('nombre_personnes')
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('appartenir_plats', []) or []:
        obj = APPARTENIR_PLATS(
            id_commande=entry.get('id_commande'),
            id_plat=entry.get('id_plat'),
            quantite=entry.get('quantite'),
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('appartenir_menus', []) or []:
        obj = APPARTENIR_MENUS(
            id_commande=entry.get('id_commande'),
            id_menu=entry.get('id_menu'),
            quantite=entry.get('quantite'),
        )
        db.session.merge(obj)
    db.session.commit()

    for entry in data.get('avis', []) or []:
        obj = AVIS(
            id_avis=entry.get('id_avis'),
            id_client=entry.get('id_client'),
            note=entry.get('note'),
            commentaire=entry.get('commentaire')
        )
        db.session.merge(obj)
    db.session.commit()

    lg.warning('Database initialized from %s!', filename)

@app.cli.command()
def syncdb():
    db.create_all()
    lg.warning('Database synchronized!')