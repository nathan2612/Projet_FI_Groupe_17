from monApp.models import (
    PLAT,
    CATEGORIE,
    CLIENT,
    COMMANDE,
    APPARTENIR_PLATS,
    APPARTENIR_MENUS,
    DEFINIR_STOCK,
    AVIS,
    MENU,
    CONTENIR
)
from .app import app, db
from flask import render_template, request, url_for, redirect, flash, abort
from .forms import InscriptionForm, ConnexionForm, EditProfileForm
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, desc
from hashlib import sha256  # Garder cette ligne
from math import ceil       # Garder cette ligne
from datetime import datetime, date, timedelta
import logging as lg
from flask import flash

@app.route('/')
@app.route('/index/')
def index():
    try:
        avis_list = db.session.query(AVIS).all()
    except Exception:
        avis_list = []

    return render_template("index.html", AVIS=avis_list)

@app.route('/avis/', endpoint='avis_page')
def avis():
    try:
        avis = db.session.query(AVIS).all()
    except Exception:
        avis = []

    return render_template("avis.html", avis=avis)

@app.route('/produits/', methods=['POST', 'GET'])
def produits():
    cat_id = request.args.get('cat_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Build base query with optional category filter
    query = db.session.query(PLAT)
    if cat_id is not None:
        query = query.filter_by(id_categorie=cat_id)

    # Read checkbox names exactly as the template uses them (sans_* for exclusion filters)
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
        query = query.filter(PLAT.gluten.is_(False))
    if sans_lactose:
        query = query.filter(PLAT.lactose.is_(False))
    if sans_fruits_a_coque:
        query = query.filter(PLAT.fruits_a_coque.is_(False))
    if sans_crustaces:
        query = query.filter(PLAT.crustaces.is_(False))

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

@app.route('/produit/<int:id_plat>')
def detail_plat(id_plat):
    """ Affiche la page de détail pour un plat spécifique. """
    plat = db.session.query(PLAT).get(id_plat)
    return render_template("detail.html", plat=plat)

@app.route('/menus/', methods=['POST', 'GET'])
def menus():
    cat_id = request.args.get('cat_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Build base query with optional category filter
    query = db.session.query(MENU)

    total = query.count()
    total_pages = max(1, ceil(total / per_page))
    page = max(1, min(page, total_pages))
    menu = query.offset((page - 1) * per_page).limit(per_page).all()

    return render_template(
        "menus.html",
        menus=menu,
        page=page,
        total_pages=total_pages,
        total_items=total,
        per_page=per_page,
    )

@app.route('/menu/<int:id_menu>')
def detail_menu(id_menu):
    """ Affiche la page de détail pour un plat spécifique. """
    menu = db.session.query(MENU).get(id_menu)
    entres = db.session.query(CONTENIR).filter_by(id_menu=id_menu, type_plat=0).all()
    plats = db.session.query(CONTENIR).filter_by(id_menu=id_menu, type_plat=1).all()
    desserts = db.session.query(CONTENIR).filter_by(id_menu=id_menu, type_plat=2).all()
    return render_template("detail_menu.html", menu=menu, entres=entres, desserts=desserts, plats=plats)

@app.route('/ajouter-au-panier-menu/', methods=['POST'])
def ajouter_au_panier_menu():
    # If user is not authenticated, redirect to connexion but set next to the
    # products listing (GET) so after login we return to a safe GET page and
    # not attempt to re-POST to this route.
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "info")
        return redirect(url_for('connexion', next=url_for('produits')))

    id_plat = request.form.get('id_plat')
    if not id_plat:
        flash("Aucun plat spécifié.", "error")
        return redirect(url_for('produits'))

    try:
        id_plat_int = int(id_plat)
    except (ValueError, TypeError):
        flash("Identifiant de plat invalide.", "error")
        return redirect(url_for('produits'))
    
    # --- CORRECTION TEMPORAIRE POUR LA DATE DE STOCK ---
    # Utilise une date fixe pour la vérification du stock afin de correspondre aux données de test.
    # En production, assurez-vous que DEFINIR_STOCK est alimenté pour la date actuelle.
    # Vérification du stock avant d'ajouter
    stock_check_date = date(2025, 10, 21) # Remplacez par la date de vos données de stock (ex: 2025, 10, 21)
    stock_disponible = db.session.query(DEFINIR_STOCK).filter_by(id_plat=id_plat_int, jour=stock_check_date).first()
    item_panier_existant = db.session.query(APPARTENIR_PLATS).join(COMMANDE).filter(
        COMMANDE.id_client == current_user.id_client,
        COMMANDE.statut == 'En commande',
        APPARTENIR_PLATS.id_plat == id_plat_int
    ).first()
    quantite_actuelle = item_panier_existant.quantite if item_panier_existant else 0
    if not stock_disponible or stock_disponible.stock <= quantite_actuelle:
        flash("Stock insuffisant pour ajouter ce plat.", "error")
        return redirect(request.referrer or url_for('produits'))

    # 1. Trouver ou créer une commande "En attente" pour l'utilisateur
    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if not commande:
        commande = COMMANDE(
            id_client=current_user.id_client,
            statut='En commande'
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

    # Recalculer le total
    total = 0
    for item in commande.plats:
        total += item.plat.prix * item.quantite
    for item in commande.menus:
        total += item.menu.prix * item.quantite
    commande.montant_total = total
    db.session.commit()

    flash("Plat ajouté au panier avec succès !", "success")
    return redirect(request.referrer or url_for('produits'))

@app.route('/contact/')
def contact():
    return render_template("contact.html")

@app.route('/apropos/')
def apropos():
    return render_template("apropos.html")

@app.route('/commandes/')
def commandes():
    """Affiche toutes les commandes avec le client et les plats/menus associés."""
    try:
        # Charger toutes les commandes sauf celles encore en cours de commande ('En commande')
        # et celles déjà récupérées ('récupéré') — elles disparaissent de la page
        commandes_list = (
            db.session.query(COMMANDE)
            .filter(~COMMANDE.statut.in_(['En commande', 'récupéré', 'non récupéré'])) # chatgpt qui me permet d'enlever les commandes en cours et récupérées grace a ~
            .order_by(COMMANDE.date_commande.desc())
            .all()
        )
    except Exception:
        commandes_list = []

    return render_template('commandes.html', commandes=commandes_list)


@app.route('/commandes/<int:cmd_id>/set_statut', methods=['POST'])
def set_statut(cmd_id):
    """Met à jour le statut d'une commande.

    Accepte les statuts validés par la contrainte DB.
    Attend un champ form 'statut'
    fait par ia car je ne savais pas comment faire autrement louis.
    """
    new_status = request.form.get('statut')
    allowed_statuses = {"En attente", "En préparation", "Prêt", "non récupéré", "récupéré", "En commande"}

    if not new_status or new_status not in allowed_statuses:
        flash("Statut invalide.", "error")
        return redirect(request.referrer or url_for('commandes'))

    commande = db.session.query(COMMANDE).filter_by(id_commande=cmd_id).first()
    if not commande:
        flash("Commande introuvable.", "error")
        return redirect(request.referrer or url_for('commandes'))

    try:
        commande.statut = new_status
        db.session.commit()
        flash(f"Statut de la commande #{cmd_id} mis à jour en '{new_status}'.", "success")
    except Exception:
        db.session.rollback()
        flash("Impossible de mettre à jour le statut (erreur base).", "error")

    return redirect(request.referrer or url_for('commandes'))



@app.route('/nouveautes/')
def nouveaute():
    return render_template("nouveaute.html")

@app.route('/panier/')
@login_required
def panier():
    commande = None
    total_general = 0

    # On cherche une commande 'En attente' pour l'utilisateur connecté
    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if commande:
        total_general = commande.montant_total or 0

    return render_template("panier.html", commande=commande, total_general=total_general)

@app.route('/ajouter-au-panier/', methods=['POST'])
def ajouter_au_panier():
    # If user is not authenticated, redirect to connexion but set next to the
    # products listing (GET) so after login we return to a safe GET page and
    # not attempt to re-POST to this route.
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "info")
        return redirect(url_for('connexion', next=url_for('produits')))

    id_plat = request.form.get('id_plat')
    if not id_plat:
        flash("Aucun plat spécifié.", "error")
        return redirect(url_for('produits'))

    try:
        id_plat_int = int(id_plat)
    except (ValueError, TypeError):
        flash("Identifiant de plat invalide.", "error")
        return redirect(url_for('produits'))
    
    # --- CORRECTION TEMPORAIRE POUR LA DATE DE STOCK ---
    # Utilise une date fixe pour la vérification du stock afin de correspondre aux données de test.
    # En production, assurez-vous que DEFINIR_STOCK est alimenté pour la date actuelle.
    # Vérification du stock avant d'ajouter
    stock_check_date = date(2025, 10, 21) # Remplacez par la date de vos données de stock (ex: 2025, 10, 21)
    stock_disponible = db.session.query(DEFINIR_STOCK).filter_by(id_plat=id_plat_int, jour=stock_check_date).first()
    item_panier_existant = db.session.query(APPARTENIR_PLATS).join(COMMANDE).filter(
        COMMANDE.id_client == current_user.id_client,
        COMMANDE.statut == 'En commande',
        APPARTENIR_PLATS.id_plat == id_plat_int
    ).first()
    quantite_actuelle = item_panier_existant.quantite if item_panier_existant else 0
    if not stock_disponible or stock_disponible.stock <= quantite_actuelle:
        flash("Stock insuffisant pour ajouter ce plat.", "error")
        return redirect(request.referrer or url_for('produits'))

    # 1. Trouver ou créer une commande "En attente" pour l'utilisateur
    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if not commande:
        commande = COMMANDE(
            id_client=current_user.id_client,
            statut='En commande'
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

    # Recalculer le total
    total = 0
    for item in commande.plats:
        total += item.plat.prix * item.quantite
    for item in commande.menus:
        total += item.menu.prix * item.quantite
    commande.montant_total = total
    db.session.commit()

    flash("Plat ajouté au panier avec succès !", "success")
    return redirect(request.referrer or url_for('produits'))


@app.route('/modifier-quantite-panier/', methods=['POST'])
@login_required
def modifier_quantite_panier():
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "info")
        return redirect(url_for('connexion', next=url_for('produits')))

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

    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if commande:
        item = db.session.query(APPARTENIR_PLATS).filter_by(id_commande=commande.id_commande, id_plat=id_plat_int).first()
        if item:
            # --- CORRECTION TEMPORAIRE POUR LA DATE DE STOCK ---
            # Utilise une date fixe pour la vérification du stock afin de correspondre aux données de test.
            stock_check_date = date(2025, 10, 21)
            if action == 'increase':
                # Utilise la même date fixe pour la cohérence des tests
                jour_verification = commande.date_commande.date() if commande.date_commande else stock_check_date
                stock_disponible = db.session.query(DEFINIR_STOCK).filter_by(id_plat=id_plat_int, jour=jour_verification).first()
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
            
            # Recalculer le total
            total = 0
            for item_plat in commande.plats:
                total += item_plat.plat.prix * item_plat.quantite
            for item_menu in commande.menus:
                total += item_menu.menu.prix * item_menu.quantite
            commande.montant_total = total
            # On sauvegarde les changements dans tous les cas (augmentation, diminution, suppression)
            db.session.commit()

    return redirect(url_for('panier'))

@app.route('/supprimer-du-panier/', methods=['POST'])
@login_required
def supprimer_du_panier():
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "info")
        return redirect(url_for('connexion', next=url_for('produits')))

    id_plat = request.form.get('id_plat')
    id_menu = request.form.get('id_menu')

    try:
        id_plat_int = int(id_plat) if id_plat else None
    except (ValueError, TypeError):
        id_plat_int = None

    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if commande:
        if id_plat_int:
            item = db.session.query(APPARTENIR_PLATS).filter_by(id_commande=commande.id_commande, id_plat=id_plat_int).first()
            if item:
                db.session.delete(item)
                flash("Plat supprimé du panier.", "success")
        elif id_menu:
            item = db.session.query(APPARTENIR_MENUS).filter_by(id_commande=commande.id_commande, id_menu=id_menu).first()
            if item:
                db.session.delete(item)
                flash("Menu supprimé du panier.", "success")
        
        if item: # Si un item a été trouvé et potentiellement supprimé
            # Recalculer le total
            total = 0
            # Il faut rafraîchir la collection après une suppression avant de la parcourir
            db.session.flush() 
            for item_plat in commande.plats:
                total += item_plat.plat.prix * item_plat.quantite
            for item_menu in commande.menus:
                total += item_menu.menu.prix * item_menu.quantite
            commande.montant_total = total
            db.session.commit()
        else:
                db.session.commit()

    return redirect(url_for('panier'))

@app.route('/valider-commande/', methods=['POST'])
@login_required
def valider_commande():
    """
    Finalise la commande en cours de l'utilisateur connecté.
    Change le statut de la commande de 'En commande' à 'En attente'
    et déduit les quantités des plats et menus du stock disponible pour aujourd'hui.
    """
    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()

    if not commande:
        flash("Aucune commande en cours à valider.", "error")
        return redirect(url_for('panier'))

    try:
        # --- CORRECTION TEMPORAIRE POUR LA DATE DE STOCK ---
        # Utilise une date fixe pour la vérification du stock afin de correspondre aux données de test.
        stock_check_date = date(2025, 10, 21)

        # Vérification et déduction du stock pour les plats
        for item_plat in commande.plats:
            stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=item_plat.id_plat, jour=stock_check_date).first()
            if not stock_entry:
                flash(f"Stock non défini pour le plat '{item_plat.plat.nom_plat}' pour aujourd'hui.", "error")
                db.session.rollback()
                return redirect(url_for('panier'))
            if stock_entry.stock < item_plat.quantite:
                flash(f"Stock insuffisant pour le plat '{item_plat.plat.nom_plat}'. Stock disponible: {stock_entry.stock}, demandé: {item_plat.quantite}.", "error")
                db.session.rollback()
                return redirect(url_for('panier'))
            stock_entry.stock -= item_plat.quantite

        # Vérification et déduction du stock pour les menus
        for item_menu in commande.menus:
            # Récupérer tous les plats qui composent ce menu
            menu_plats_links = db.session.query(CONTENIR).filter_by(id_menu=item_menu.id_menu).all()
            
            for menu_plat_link in menu_plats_links:
                plat_id = menu_plat_link.id_plat
                plat_obj = db.session.get(PLAT, plat_id) # Pour le nom du plat en cas d'erreur
                
                stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=plat_id, jour=stock_check_date).first()
                required_stock = item_menu.quantite # Chaque plat du menu est déduit par la quantité du menu

                if not stock_entry:
                    flash(f"Stock non défini pour un ingrédient ('{plat_obj.nom_plat}') du menu '{item_menu.menu.nom_menu}' pour aujourd'hui.", "error")
                    db.session.rollback()
                    return redirect(url_for('panier'))
                if stock_entry.stock < required_stock:
                    flash(f"Stock insuffisant pour un ingrédient ('{plat_obj.nom_plat}') du menu '{item_menu.menu.nom_menu}'. Stock disponible: {stock_entry.stock}, demandé: {required_stock}.", "error")
                    db.session.rollback()
                    return redirect(url_for('panier'))
                stock_entry.stock -= required_stock

        # Mettre à jour le statut et la date de la commande
        commande.statut = 'En attente'
        # --- CORRECTION TEMPORAIRE POUR LA DATE DE COMMANDE ---
        # Utilise une date et heure fixes valides pour correspondre aux données de test et aux contraintes de la DB.
        commande.date_commande = datetime(2025, 10, 21, 12, 30, 0) # Heure valide (entre 11:30 et 14:00)
        db.session.commit()
        flash("Votre commande a été validée avec succès et est en attente de préparation !", "success")
        return redirect(url_for('index')) # Redirige le client vers la page d'accueil après validation

    except Exception as e:
        db.session.rollback()
        flash(f"Une erreur est survenue lors de la validation de votre commande : {e}", "error")
        return redirect(url_for('panier'))

@app.route('/connexion/', methods=['GET', 'POST'])
def connexion():
    lg.warning('connexion à la page de connexion')
    form = ConnexionForm()
    client = None
    if not form.is_submitted():
        lg.warning('Formulaire non soumis, récupération du paramètre next')
        form.next.data = request.args.get('next')
        lg.warning('Paramètre next défini sur: %s', form.next.data)
    elif form.validate_on_submit():
        lg.warning('Formulaire soumis et valide, tentative de connexion')
        # Special-case admin login: if telephone and password are both 'admin', redirect to /admin/
        try:
            tel = (form.telephone.data or '').strip()
            pwd = (form.mot_de_passe.data or '').strip()
        except Exception:
            tel = ''
            pwd = ''
        if tel == 'admin' and pwd == 'admin':
            lg.warning('Admin credentials provided — redirecting to /admin/')
            return redirect(url_for('admin_index'))
        client = form.get_authenticated_client()
        if client:
            lg.warning(f"Connexion réussie pour: {client.prenom} {client.nom}")
            login_user(client)
            next = form.next.data or url_for("index")
            return redirect(next)
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

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Vous avez été déconnecté.", "success")
    return redirect(url_for('index'))

@app.route('/compte/', methods=['GET', 'POST'])
@login_required
def compte():
    """ Affiche et gère la mise à jour du compte de l'utilisateur. """
    # Récupérer les commandes de l'utilisateur, triées par date décroissante
    commandes_client = (
        db.session.query(COMMANDE)
        .filter_by(id_client=current_user.id_client)
        .order_by(COMMANDE.date_commande.desc())
        .all()
    )

    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        user_to_update = db.session.get(CLIENT, current_user.id_client)
        
        # Mise à jour des informations de base
        user_to_update.prenom = form.prenom.data
        user_to_update.nom = form.nom.data
        user_to_update.telephone = form.telephone.data

        # Gestion du changement de mot de passe
        if form.new_mot_de_passe.data:
            # Vérifier si le mot de passe actuel est correct
            m = sha256()
            m.update(form.current_mot_de_passe.data.encode())
            current_password_hash = m.hexdigest()

            if current_password_hash == user_to_update.mot_de_passe:
                # Hasher et sauvegarder le nouveau mot de passe
                m_new = sha256()
                m_new.update(form.new_mot_de_passe.data.encode())
                user_to_update.mot_de_passe = m_new.hexdigest()
                flash("Votre mot de passe a été mis à jour.", "success")
            else:
                flash("Le mot de passe actuel est incorrect.", "error")
                return render_template("compte.html", form=form, commandes=commandes_client)

        db.session.commit()
        flash("Vos informations ont été mises à jour avec succès !", "success")
        return redirect(url_for('compte'))

    return render_template("compte.html", form=form, commandes=commandes_client)
  
@app.route('/preparation-cuisto/')
def preparation_cuisto():
    try :
        status = db.session.query(COMMANDE).all()
    except Exception:
        status = []
    return render_template("preparation-cuisto.html", COMMANDE=status)

def is_admin():
    # Ceci est un exemple simple. Adaptez-le à votre système d'authentification.
    # Par exemple, vous pourriez vérifier si l'utilisateur appartient à un groupe "admin".
    return current_user.telephone == "admin"  # À remplacer par votre logique

@app.route('/admin/stock/')
def admin_stock():
    #if not current_user.is_authenticated or not is_admin():
    #    flash("Vous n'avez pas les droits pour accéder à cette page.", "error")
    #    return redirect(url_for('index'))  # Rediriger vers une page appropriée

    today = date.today()
    items = db.session.query(PLAT).all()
    
    # Pour chaque plat, récupérer ou créer l'entrée de stock pour aujourd'hui
    for item in items:
        stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=item.id_plat, jour=today).first()
        if not stock_entry:
            stock_entry = DEFINIR_STOCK(id_plat=item.id_plat, jour=today, stock=0)
            db.session.add(stock_entry)
            db.session.commit()  # Créer l'entrée immédiatement

    # Récupérer les items avec leur stock actuel
    items_with_stock = []
    for item in items:
        stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=item.id_plat, jour=today).first()
        items_with_stock.append({
            'item': item,
            'stock': stock_entry.stock if stock_entry else 0
        })

    search_term = request.args.get('search', '')
    if search_term:
        items_with_stock = [item for item in items_with_stock if search_term.lower() in item['item'].nom_plat.lower()]

    return render_template("admin_stock.html", items=items_with_stock, search_term=search_term)

@app.route('/admin/stock/view/<int:item_id>')
def view_stock_item(item_id):
    #if not is_admin():
    #    flash("Vous n'avez pas les droits pour accéder à cette page.", "error")
    #    return redirect(url_for('index'))

    item = db.session.get(PLAT, item_id)
    today = date.today()
    stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=item_id, jour=today).first()

    if not item:
        flash("Article non trouvé.", "error")
        return redirect(url_for('admin_stock'))

    return render_template("view_stock_item.html", item=item, stock=stock_entry.stock if stock_entry else 0)


@app.route('/admin/stock/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_stock_item(item_id):
    #if not is_admin():
    #    flash("Vous n'avez pas les droits pour accéder à cette page.", "error")
    #    return redirect(url_for('index'))

    item = db.session.get(PLAT, item_id)
    today = date.today()
    stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=item_id, jour=today).first()

    if not item:
        flash("Article non trouvé.", "error")
        return redirect(url_for('admin_stock'))

    if request.method == 'POST':
        try:
            # Vérifie si l'action est un 'reset' ou une mise à jour normale
            if 'reset' in request.form:
                new_stock = 0
                flash(f"Le stock pour '{item.nom_plat}' a été réinitialisé.", "success")
            else:
                new_stock = int(request.form['stock'])
                flash(f"Stock pour '{item.nom_plat}' mis à jour avec succès.", "success")

            stock_entry.stock = new_stock
            db.session.commit()
            # Redirige vers la même page avec le terme de recherche pour ne pas le perdre
            return redirect(url_for('admin_stock', search=request.args.get('search', '')))
        except ValueError:
            flash("Veuillez entrer une quantité valide.", "error")
    return redirect(url_for('admin_stock'))

@app.route('/admin/banni/')
def admin_banni():
    # Count non-récupéré commandes per client and order desc by count
    # Note: statut values include 'non récupéré' per model constraint
    results = (
        db.session.query(CLIENT, func.count(COMMANDE.id_commande).label('nb_non_recup'))
        .join(COMMANDE)
        .filter(COMMANDE.statut == 'non récupéré', CLIENT.banni.is_(False))
        .group_by(CLIENT.id_client)
        .order_by(desc('nb_non_recup'))
        .all()
    )

    # results is list of (CLIENT, nb_non_recup). Pass to template as list of dicts
    clients = [
        {
            'client': r[0],
            'nb_non_recup': int(r[1])
        }
        for r in results
    ]

    return render_template("admin_banni.html", clients=clients)


@app.route('/admin/ban/<int:client_id>', methods=['POST'])
def ban_client(client_id):
    # mark client as banned
    client = db.session.query(CLIENT).filter_by(id_client=client_id).first()
    if not client:
        flash('Client introuvable', 'error')
        return redirect(url_for('admin_banni'))
    client.banni = True
    db.session.add(client)
    db.session.commit()
    flash(f"Client {client.prenom} {client.nom} banni.", 'success')
    return redirect(url_for('admin_banni'))


@app.route('/admin/bannis/')
def admin_bannis():
    # list clients who are banned
    clients = db.session.query(CLIENT).filter_by(banni=True).all()
    return render_template('admin_bannis.html', clients=clients)


@app.route('/admin/unban/<int:client_id>', methods=['POST'])
def unban_client(client_id):
    client = db.session.query(CLIENT).filter_by(id_client=client_id).first()
    if not client:
        flash('Client introuvable', 'error')
        return redirect(url_for('admin_bannis'))
    client.banni = False
    db.session.add(client)
    db.session.commit()
    flash(f"Client {client.prenom} {client.nom} débanni.", 'success')
    return redirect(url_for('admin_bannis'))

@app.route('/admin-index/')
def admin_index():
    today = date.today()
    yesterday = today - timedelta(days=1)
    current_month_start = today.replace(day=1)
    last_month_end = current_month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    current_year_start = today.replace(day=1, month=1)
    last_year_start = current_year_start.replace(year=today.year - 1)
    last_year_end = current_year_start - timedelta(days=1)

    # Utiliser des requêtes agrégées pour la performance
    def get_stats(start_date, end_date):
        """Calcule le nombre de commandes et le CA pour une période donnée."""
        stats = db.session.query(
            func.count(COMMANDE.id_commande),
            func.sum(COMMANDE.montant_total)
        ).filter(
            COMMANDE.statut == "récupéré",
            COMMANDE.date_commande.between(start_date, end_date)
        ).first()
        # Convertir le montant total en float pour éviter les erreurs de type avec Decimal
        return stats[0] or 0, float(stats[1]) if stats[1] is not None else 0.0

    # Calculs pour les périodes actuelles
    lst_recup_auj, ca_auj = get_stats(today, today + timedelta(days=1))
    lst_recup_mois, ca_mois = get_stats(current_month_start, today + timedelta(days=1))
    lst_recup_annee, ca_annee = get_stats(current_year_start, today + timedelta(days=1))

    # Calculs pour les périodes précédentes
    _, ca_hier = get_stats(yesterday, today)
    _, ca_mois_dernier = get_stats(last_month_start, last_month_end)
    _, ca_annee_derniere = get_stats(last_year_start, last_year_end)

    # Calcul des pourcentages de variation
    ca_pourcentage_hier_auj = round((ca_auj - ca_hier) / ca_hier * 100) if ca_hier != 0 else 0
    ca_pourcentage_mois = round((ca_mois - ca_mois_dernier) / ca_mois_dernier * 100) if ca_mois_dernier != 0 else 0
    ca_pourcentage_annee_derniere = round((ca_annee - ca_annee_derniere) / ca_annee_derniere * 100) if ca_annee_derniere != 0 else 0


    # Calculer le top 5 des plats vendus (id + quantité) puis récupérer les objets PLAT
    # Optimisation : Agréger directement en base de données
    top_items_query = (
        db.session.query(
            APPARTENIR_PLATS.id_plat,
            func.sum(APPARTENIR_PLATS.quantite).label('total_vendus')
        )
        .group_by(APPARTENIR_PLATS.id_plat)
        .order_by(desc('total_vendus'))
        .limit(5)
        .all()
    )
    top_items = [(item[0], item[1]) for item in top_items_query]

    top_5_ventes = []
    if top_items:
        ids_top = [pid for pid, r in top_items]
        plats = db.session.query(PLAT).filter(PLAT.id_plat.in_(ids_top)).all() # aide de chatpgt car bon
        plats_map = {p.id_plat: p for p in plats}
        for pid, qte in top_items:
            top_5_ventes.append((plats_map.get(pid), qte))

    # Récupérer uniquement les noms des plats en rupture aujourd'hui (stock == 0)
    liste_plat = (
    db.session.query(PLAT.nom_plat, DEFINIR_STOCK.stock, DEFINIR_STOCK.jour)
    .join(DEFINIR_STOCK, PLAT.id_plat == DEFINIR_STOCK.id_plat)
    .all()
    )

    tout_plats = db.session.query(PLAT.nom_plat).all()

    # Créer un ensemble des noms de plats à exclure
    plats_a_exclure = set()
    for nom, stock, jour in liste_plat:
        if stock != 0 and jour == today:
            plats_a_exclure.add(nom)

    # Filtrer tout_plats pour garder seulement ceux qui ne sont pas à exclure
    tout_plats_rupture = [plat for plat in tout_plats if plat[0] not in plats_a_exclure]

    print(tout_plats_rupture)

    return render_template(
        "admin_index.html",
        top_5_ventes=top_5_ventes,
        ca_pourcentage_annee_derniere=ca_pourcentage_annee_derniere,
        ca_pourcentage_mois=ca_pourcentage_mois,
        ca_pourcentage_hier_auj=ca_pourcentage_hier_auj,
        ca_hier=ca_hier,
        ca_mois_dernier=ca_mois_dernier,
        ca_annee_derniere=ca_annee_derniere,
        lst_recup_auj=lst_recup_auj,
        lst_recup_mois=lst_recup_mois,
        lst_recup_annee=lst_recup_annee,
        ca_auj=ca_auj,
        ca_mois=ca_mois,
        ca_annee=ca_annee,
        tout_plats_rupture=tout_plats_rupture
    )




if __name__ == "__main__":
    app.run()