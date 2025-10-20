import click
import logging as lg
from .app import app, db

@app.cli.command()
@click.argument('filename')
def loaddb(filename):
    """Creates the tables and populates them with data from a YAML file.

    Expected YAML keys: context, categories, plats, clients, reservations,
    commandes, menus, contenir, appartenir_plats, appartenir_menus, avis, definir_stock
    """

    import yaml
    from datetime import datetime

    # création de toutes les tables
    db.drop_all()
    db.create_all()

    # chargement du YAML
    with open(filename, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)

    # import des modèles locaux
    from .models import (
        Categorie, Plat, Client, Reservation, Commande, Menu,
        Contenir, AppartenirPlats, AppartenirMenus, Avis, DefinirStock
    )

    # helpers pour parsing date/time
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

    # Insertions par sections (ordre pour respecter FK)
    # 1) categories
    for entry in data.get('categories', []) or []:
        obj = Categorie(
            id_categorie=entry.get('id_categorie'),
            nom_categorie=entry.get('nom_categorie'),
            description=entry.get('description')
        )
        db.session.merge(obj)
    db.session.commit()

    # 2) plats
    for entry in data.get('plats', []) or []:
        obj = Plat(
            id_plat=entry.get('id_plat'),
            id_categorie=entry.get('id_categorie'),
            nom_plat=entry.get('nom_plat'),
            description=entry.get('description'),
            prix=entry.get('prix'),
            stock=entry.get('stock'),
            disponible=entry.get('disponible', True)
        )
        db.session.merge(obj)
    db.session.commit()

    # 3) clients
    for entry in data.get('clients', []) or []:
        obj = Client(
            id_client=entry.get('id_client'),
            nom_client=entry.get('nom_client'),
            prenom_client=entry.get('prenom_client'),
            email=entry.get('email'),
            telephone=entry.get('telephone')
        )
        db.session.merge(obj)
    db.session.commit()

    # 4) menus
    for entry in data.get('menus', []) or []:
        obj = Menu(
            id_menu=entry.get('id_menu'),
            nom_menu=entry.get('nom_menu'),
            description=entry.get('description'),
            prix=entry.get('prix')
        )
        db.session.merge(obj)
    db.session.commit()

    # 5) contenir (menu -> plat)
    for entry in data.get('contenir', []) or []:
        obj = Contenir(
            id_menu=entry.get('id_menu'),
            id_plat=entry.get('id_plat')
        )
        db.session.merge(obj)
    db.session.commit()

    # 6) commandes
    for entry in data.get('commandes', []) or []:
        obj = Commande(
            id_commande=entry.get('id_commande'),
            id_client=entry.get('id_client'),
            date_commande=parse_date(entry.get('date_commande')),
            statut=entry.get('statut'),
            montant_total=entry.get('montant_total'),
            sur_place=entry.get('sur_place')
        )
        db.session.merge(obj)
    db.session.commit()

    # 7) appartenir_plats (lignes de commande pour plats)
    for entry in data.get('appartenir_plats', []) or []:
        obj = AppartenirPlats(
            id_commande=entry.get('id_commande'),
            id_plat=entry.get('id_plat'),
            quantite=entry.get('quantite'),
            prix_unitaire=entry.get('prix_unitaire')
        )
        db.session.merge(obj)
    db.session.commit()

    # 8) appartenir_menus (lignes de commande pour menus)
    for entry in data.get('appartenir_menus', []) or []:
        obj = AppartenirMenus(
            id_commande=entry.get('id_commande'),
            id_menu=entry.get('id_menu'),
            quantite=entry.get('quantite'),
            prix_unitaire=entry.get('prix_unitaire')
        )
        db.session.merge(obj)
    db.session.commit()

    # 9) reservations
    for entry in data.get('reservations', []) or []:
        obj = Reservation(
            id_reservation=entry.get('id_reservation'),
            id_client=entry.get('id_client'),
            date_reservation=parse_date(entry.get('date_reservation')),
            heure_reservation=parse_time(entry.get('heure_reservation')),
            nombre_personnes=entry.get('nombre_personnes')
        )
        db.session.merge(obj)
    db.session.commit()

    # 10) avis
    for entry in data.get('avis', []) or []:
        obj = Avis(
            id_avis=entry.get('id_avis'),
            id_client=entry.get('id_client'),
            note=entry.get('note'),
            commentaire=entry.get('commentaire')
        )
        db.session.merge(obj)
    db.session.commit()

    # 11) definir_stock
    for entry in data.get('definir_stock', []) or []:
        obj = DefinirStock(
            id_plat=entry.get('id_plat'),
            jour=parse_date(entry.get('jour')),
            stock=entry.get('stock')
        )
        db.session.merge(obj)
    db.session.commit()

    lg.warning('Database initialized from %s!', filename)

@app.cli.command()
def syncdb():
    '''Creates all missing tables. '''
    db.create_all()
    lg.warning('Database synchronized!')

#@app.cli.command()
#@click.argument('login')
#@click.argument('pwd')
#def newuser (login, pwd):
#    '''Adds a new user'''
#    from . models import User
#    unUser = User(login, pwd)
#    db.session.add(unUser)
#    db.session.commit()
#    lg.warning('User ' + login + ' created!')
#
#@app.cli.command()
#@click.argument('login')
#@click.argument('pwd')
#def newpassword (login, pwd):
#    '''Change the password of an existing user'''
#    from . models import User
#    from hashlib import sha256
#    user = db.session.get(User, login)
#    if user is None:
#        lg.warning('User ' + login + ' does not exist!')
#        return
#    m = sha256()
#    m.update(pwd.encode())
#    user.Password = m.hexdigest()
#    db.session.commit()
#    lg.warning('User ' + login + ' password updated!')