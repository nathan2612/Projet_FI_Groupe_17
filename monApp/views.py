from monApp.models import PLAT,CATEGORIE,CLIENT, COMMANDE, APPARTENIR_PLATS, DEFINIR_STOCK
from .app import app
from flask import render_template, request, url_for, redirect, flash, session
from .app import db
from .forms import InscriptionForm, ConnexionForm
from flask_login import login_user,logout_user,login_required, current_user
from hashlib import sha256
from math import ceil
from datetime import datetime
import logging as lg

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")

@app.route('/produits/', methods=['POST', 'GET'])
def produits():
    cat_id = request.args.get('cat_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Build base query with optional category filter
    query = db.session.query(PLAT)
    if cat_id is not None:
        query = query.filter_by(id_categorie=cat_id)

    vegetarien = request.values.get('vegetarien', '0') == '1'
    vegan = request.values.get('vegan', '0') == '1'
    sans_gluten = request.values.get('sans_gluten', '0') == '1'
    sans_lactose = request.values.get('sans_lactose', '0') == '1'
    sans_fruits_a_coque = request.values.get('sans_fruits_a_coque', '0') == '1'
    sans_crustaces = request.values.get('sans_crustaces', '0') == '1'

    if vegetarien:
        query = query.filter(PLAT.vegetarien.is_(True))
    if vegan:
        query = query.filter(PLAT.vegan.is_(True))
    if sans_gluten:
        query = query.filter(PLAT.sans_gluten.is_(True))
    if sans_lactose:
        query = query.filter(PLAT.sans_lactose.is_(True))
    if sans_fruits_a_coque:
        query = query.filter(PLAT.sans_fruits_a_coque.is_(True))
    if sans_crustaces:
        query = query.filter(PLAT.sans_crustaces.is_(True))

    total = query.count()
    total_pages = max(1, ceil(total / per_page))
    page = max(1, min(page, total_pages))
    produits = query.offset((page - 1) * per_page).limit(per_page).all()
    categories = db.session.query(CATEGORIE).all()

    return render_template(
        "produits.html",
        produits=produits,
        cat_id=cat_id,
        categories=categories,
        page=page,
        total_pages=total_pages,
        total_items=total,
        per_page=per_page,
        filters={
            'vegetarien': vegetarien,
            'vegan': vegan,
            'sans_gluten': sans_gluten,
            'sans_lactose': sans_lactose,
            'sans_fruits_a_coque': sans_fruits_a_coque,
            'sans_crustaces': sans_crustaces,
        }
    )
                       
@app.route('/contact/')
def contact():
    return render_template("contact.html")

@app.route('/apropos/')
def apropos():
    return render_template("propos.html")

@app.route('/nouveautes/')
def nouveaute():
    return render_template("nouveaute.html")

@app.route('/panier/')
@login_required
def panier():
    commande = None
    total_general = 0

    # On cherche une commande 'En attente' pour l'utilisateur connecté
    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En attente').first()
    if commande:
        total_general = commande.montant_total or 0

    return render_template("panier.html", commande=commande, total_general=total_general)

@app.route('/ajouter-au-panier/', methods=['POST'])
def ajouter_au_panier():
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "info")
        return redirect(url_for('connexion'))

    id_plat = request.form.get('id_plat')
    if not id_plat:
        flash("Aucun plat spécifié.", "error")
        return redirect(url_for('produits'))

    try:
        id_plat_int = int(id_plat)
    except (ValueError, TypeError):
        flash("Identifiant de plat invalide.", "error")
        return redirect(url_for('produits'))

    # 1. Trouver ou créer une commande "En attente" pour l'utilisateur
    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En attente').first()
    if not commande:
        commande = COMMANDE(
            id_client=current_user.id_client,
            date_commande=datetime.now(),
            statut='En attente'
        )
        db.session.add(commande)
        db.session.commit() # On commit pour que la commande ait un ID

    # 2. Vérifier si le plat est déjà dans la commande
    item_panier = db.session.query(APPARTENIR_PLATS).filter_by(id_commande=commande.id_commande, id_plat=id_plat_int).first()

    if item_panier:
        # Si oui, on incrémente la quantité
        item_panier.quantite += 1
    else:
        # Sinon, on crée une nouvelle ligne dans appartenir_plats
        item_panier = APPARTENIR_PLATS(id_commande=commande.id_commande, id_plat=id_plat_int, quantite=1)
        db.session.add(item_panier)

    db.session.commit()

    flash("Plat ajouté au panier avec succès !", "success")
    return redirect(request.referrer or url_for('produits'))

@app.route('/modifier-quantite-panier/', methods=['POST'])
def modifier_quantite_panier():
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour modifier votre panier.", "info")
        return redirect(url_for('connexion'))

    id_plat = request.form.get('id_plat')
    action = request.form.get('action')

    if not id_plat or not action:
        flash("Action invalide.", "error")
        return redirect(url_for('panier'))

    try:
        id_plat_int = int(id_plat)
    except (ValueError, TypeError):
        flash("Identifiant de plat invalide.", "error")
        return redirect(url_for('panier'))

    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En attente').first()
    if commande:
        item = db.session.query(APPARTENIR_PLATS).filter_by(id_commande=commande.id_commande, id_plat=id_plat_int).first()
        if item:
            if action == 'increase':
                stock_disponible = db.session.query(DEFINIR_STOCK).filter_by(id_plat=id_plat_int, jour=commande.date_commande.date()).first()
                if stock_disponible and item.quantite < stock_disponible.stock:
                    item.quantite += 1
                    flash("Quantité mise à jour.", "success")
                else:
                    flash("Stock insuffisant pour ajouter cet article.", "error")
            elif action == 'decrease':
                item.quantite -= 1

            # On vérifie si l'article doit être supprimé
            if item.quantite <= 0:
                db.session.delete(item)
                flash("Plat supprimé du panier.", "success")
            
            # On sauvegarde les changements dans tous les cas (augmentation, diminution, suppression)
            db.session.commit()

    return redirect(url_for('panier'))

@app.route('/supprimer-du-panier/', methods=['POST'])
def supprimer_du_panier():
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour modifier votre panier.", "info")
        return redirect(url_for('connexion'))

    id_plat = request.form.get('id_plat')
    id_menu = request.form.get('id_menu')

    try:
        id_plat_int = int(id_plat) if id_plat else None
    except (ValueError, TypeError):
        id_plat_int = None

    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En attente').first()
    if commande:
        if id_plat_int:
            item = db.session.query(APPARTENIR_PLATS).filter_by(id_commande=commande.id_commande, id_plat=id_plat_int).first()
            if item:
                db.session.delete(item)
                db.session.commit()
                flash("Plat supprimé du panier.", "success")
        elif id_menu:
            item = db.session.query(APPARTENIR_MENUS).filter_by(id_commande=commande.id_commande, id_menu=id_menu).first()
            if item:
                db.session.delete(item)
                db.session.commit()
                flash("Menu supprimé du panier.", "success")

    return redirect(url_for('panier'))

@app.route('/connexion/', methods=['GET', 'POST'])
def connexion():
    lg.warning('connexion à la page de connexion')
    form = ConnexionForm()
    client = None
    if not form.is_submitted():
        lg.warning('Formulaire non soumis, récupération du paramètre next')
        form.next.data = request.args.get('next')
    elif form.validate_on_submit():
        lg.warning('Formulaire soumis et valide, tentative de connexion')
        client = form.get_authenticated_client()
        if client:
            lg.warning(f"Connexion réussie pour: {client.prenom} {client.nom}")
            login_user(client)
            return redirect(url_for('index'))
    return render_template("connexion.html", form=form)


@app.route('/inscription/', methods=['GET', 'POST'])
def inscription():
    form = InscriptionForm()
    if form.validate_on_submit():
        if not db.session.query(CLIENT).filter_by(telephone=form.telephone.data).first() and form.mot_de_passe.data == form.confirmation_mot_de_passe.data:
            from hashlib import sha256
            m = sha256()
            m.update(form.mot_de_passe.data.encode())
            new_client = CLIENT(
                prenom=form.prenom.data,
                nom=form.nom.data,
                telephone=form.telephone.data,
                mot_de_passe=m.hexdigest()
            )
            db.session.add(new_client)
            db.session.commit()
        return redirect(url_for('connexion'))
    return render_template("inscription.html", form=form)


if __name__ == "__main__":
    app.run()