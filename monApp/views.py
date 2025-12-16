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
from functools import wraps
from .forms import InscriptionForm, ConnexionForm, EditProfileForm, PlatForm, MenuForm
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import func, desc
from hashlib import sha256
from math import ceil
from datetime import datetime, date, timedelta
import logging as lg
from flask import flash

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash("Vous n'avez pas les droits pour accéder à cette page.", "error")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

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
        query = query.filter(PLAT.gluten.is_(False))
    if sans_lactose:
        query = query.filter(PLAT.lactose.is_(False))
    if sans_fruits_a_coque:
        query = query.filter(PLAT.fruit_a_coque.is_(False))
    if sans_crustaces:
        query = query.filter(PLAT.crustaces.is_(False))

    total = query.count()
    total_pages = max(1, ceil(total / per_page))
    page = max(1, min(page, total_pages))
    produits = query.offset((page - 1) * per_page).limit(per_page).all()

    ids_plats = [p.id_plat for p in produits]
    stocks_db = db.session.query(DEFINIR_STOCK).filter(DEFINIR_STOCK.id_plat.in_(ids_plats), DEFINIR_STOCK.jour == date.today()).all()
    stocks_map = {s.id_plat: s.stock for s in stocks_db}

    for plat in produits:
        plat.stock_disponible = stocks_map.get(plat.id_plat, 0)

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
    plat = db.session.query(PLAT).get(id_plat)
    
    stock_check_date = date.today()
    stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=id_plat, jour=stock_check_date).first()
    
    stock_disponible = stock_entry.stock if stock_entry else 0

    return render_template("detail.html", plat=plat, stock_disponible=stock_disponible)


@app.route('/menus/', methods=['POST', 'GET'])
def menus():
    cat_id = request.args.get('cat_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 9

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
    menu = db.session.query(MENU).get(id_menu)
    entres = db.session.query(CONTENIR).filter_by(id_menu=id_menu, type_plat=0).all()
    plats = db.session.query(CONTENIR).filter_by(id_menu=id_menu, type_plat=1).all()
    desserts = db.session.query(CONTENIR).filter_by(id_menu=id_menu, type_plat=2).all()

    today = date.today()
    all_plat_ids = set()
    for c in (entres or []) + (plats or []) + (desserts or []):
        if c and getattr(c, 'id_plat', None) is not None:
            all_plat_ids.add(c.id_plat)
    if all_plat_ids:
        stocks = db.session.query(DEFINIR_STOCK).filter(DEFINIR_STOCK.id_plat.in_(list(all_plat_ids)), DEFINIR_STOCK.jour == today).all()
        stocks_map = {s.id_plat: s.stock for s in stocks}
    else:
        stocks_map = {}
    for c in (entres or []) + (plats or []) + (desserts or []):
        c.plat.stock_disponible = stocks_map.get(c.id_plat, 0)

    return render_template("detail_menu.html", menu=menu, entres=entres, desserts=desserts, plats=plats)
   
@app.route('/ajouter-menu-selection/', methods=['POST'])
def ajouter_menu_selection():
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "info")
        return redirect(url_for('connexion', next=request.referrer or url_for('produits')))

    entree_id = request.form.get('entree')
    plat_id = request.form.get('plat')
    dessert_id = request.form.get('dessert')
    id_menu = request.form.get('id_menu')

    if not entree_id or not plat_id or not dessert_id or not id_menu:
        flash("Veuillez sélectionner une entrée, un plat principal et un dessert.", "error")
        return redirect(request.referrer or url_for('menus'))

    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if not commande:
        commande = COMMANDE(
            id_client=current_user.id_client,
            statut='En commande'
        )
        db.session.add(commande)
        db.session.commit()

    menu = db.session.query(APPARTENIR_MENUS).filter_by(
        id_commande=commande.id_commande,
        id_menu=id_menu,
        id_entree=entree_id,
        id_plat_choisi=plat_id,
        id_dessert=dessert_id
    ).first()

    if menu:
        menu.quantite = (menu.quantite or 0) + 1
    else:
        menu = APPARTENIR_MENUS(
            id_commande=commande.id_commande,
            id_menu=id_menu,
            quantite=1,
            id_entree=entree_id,
            id_plat_choisi=plat_id,
            id_dessert=dessert_id if dessert_id is not None else None
        )
        db.session.add(menu)
    db.session.commit()

    flash("Menu ajouté au panier.", "success")
    return redirect(request.referrer or url_for('panier'))


@app.route('/contact/')
def contact():
    return render_template("contact.html")

@app.route('/apropos/')
def apropos():
    return render_template("apropos.html")

@app.route('/commandes/')
def commandes():
    try:
        commandes_list = (
            db.session.query(COMMANDE)
            .filter(~COMMANDE.statut.in_(['En commande', 'récupéré', 'non récupéré']))
            .order_by(COMMANDE.date_commande.desc())
            .all()
        )
    except Exception:
        commandes_list = []

    return render_template('commandes.html', commandes=commandes_list)


@app.route('/commandes/<int:cmd_id>/set_statut', methods=['POST'])
def set_statut(cmd_id):
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

    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if commande:
        total_general = commande.montant_total or 0

    return render_template("panier.html", commande=commande, total_general=total_general)

@app.route('/ajouter-au-panier/', methods=['POST'])
def ajouter_au_panier():
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "info")
        return redirect(url_for('connexion', next=url_for('produits')))

    id_plat = request.form.get('id_plat')

    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if not commande:
        commande = COMMANDE(
            id_client=current_user.id_client,
            statut='En commande'
        )
        db.session.add(commande)
        db.session.commit()

    item_panier = db.session.query(APPARTENIR_PLATS).filter_by(id_commande=commande.id_commande, id_plat=id_plat).first()

    try:
        if item_panier:
            item_panier.quantite += 1
        else:
            item_panier = APPARTENIR_PLATS(id_commande=commande.id_commande, id_plat=id_plat, quantite=1)
            db.session.add(item_panier)
            db.session.commit()
    except Exception:
        lg.warning("Erreur lors de l'ajout au panier : pas de stock disponible.")
        db.session.rollback()

    flash("Plat ajouté au panier avec succès !", "success")
    return redirect(request.referrer or url_for('produits'))


@app.route('/modifier-quantite-panier/', methods=['POST'])
@login_required
def modifier_quantite_panier():
    id_plat = request.form.get('id_plat')
    id_menu = request.form.get('id_menu')
    id_entree = request.form.get('id_entree')
    id_plat_choisi = request.form.get('id_plat_choisi')
    id_dessert = request.form.get('id_dessert')
    action = request.form.get('action')
    commande = db.session.query(COMMANDE).filter_by(
        id_client=current_user.id_client, statut='En commande').first()
    if id_plat:
        item = db.session.query(APPARTENIR_PLATS).filter_by(
            id_commande=commande.id_commande, id_plat=id_plat).first()
    elif id_menu:
        item = db.session.query(APPARTENIR_MENUS).filter_by(
            id_commande=commande.id_commande,
            id_menu=id_menu,
            id_entree=id_entree,
            id_plat_choisi=id_plat_choisi,
            id_dessert=id_dessert
        ).first()

    if action == 'increase':
        item.quantite += 1
    else:
        item.quantite -= 1

    if item.quantite <= 0:
        db.session.delete(item)

    try:
        db.session.commit()
    except Exception:
        lg.warning("Erreur lors de la modification de la quantité dans le panier.")
        db.session.rollback()
    return redirect(url_for('panier'))

@app.route('/supprimer-du-panier/', methods=['POST'])
@login_required
def supprimer_du_panier():
    if not current_user.is_authenticated:
        flash("Veuillez vous connecter pour ajouter des articles au panier.", "info")
        return redirect(url_for('connexion', next=url_for('produits')))

    id_plat = request.form.get('id_plat')
    id_menu = request.form.get('id_menu')
    id_entree = request.form.get('id_entree')
    id_plat_choisi = request.form.get('id_plat_choisi')
    id_dessert = request.form.get('id_dessert')

    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    if id_plat:
        item = db.session.query(APPARTENIR_PLATS).filter_by(id_commande=commande.id_commande, id_plat=id_plat).first()
        if item:
            db.session.delete(item)
            flash("Plat supprimé du panier.", "success")
    elif id_menu:
        item = db.session.query(APPARTENIR_MENUS).filter_by(id_commande=commande.id_commande, id_menu=id_menu, id_entree=id_entree, id_plat_choisi=id_plat_choisi, id_dessert=id_dessert).first()
        if item:
            db.session.delete(item)
            flash("Menu supprimé du panier.", "success")
        
    db.session.commit()
    return redirect(url_for('panier'))

@app.route('/valider-commande/', methods=['POST'])
@login_required
def valider_commande():
    commande = db.session.query(COMMANDE).filter_by(id_client=current_user.id_client, statut='En commande').first()
    try:
        commande.statut = 'En attente'
        commande.date_commande = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)   #remplacer par datetime.now() pour l'heure actuelle plus tard
        db.session.commit()
        flash("Votre commande a été validée avec succès et est en attente de préparation !", "success")
        return redirect(url_for('index'))
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
        form.next.data = request.args.get('next')
    elif form.validate_on_submit():
        try:
            tel = (form.telephone.data or '').strip()
            pwd = (form.mot_de_passe.data or '').strip()
        except Exception:
            tel = ''
            pwd = ''
        if tel == 'admin' and pwd == 'admin':
            return redirect(url_for('admin_index'))
        client = form.get_authenticated_client()
        if client:
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
    commandes_client = (
        db.session.query(COMMANDE)
        .filter_by(id_client=current_user.id_client)
        .order_by(COMMANDE.date_commande.desc())
        .all()
    )

    form = EditProfileForm(obj=current_user)

    if form.validate_on_submit():
        user_to_update = db.session.get(CLIENT, current_user.id_client)
        
        user_to_update.prenom = form.prenom.data
        user_to_update.nom = form.nom.data
        user_to_update.telephone = form.telephone.data

        if form.new_mot_de_passe.data:
            m = sha256()
            m.update(form.current_mot_de_passe.data.encode())
            current_password_hash = m.hexdigest()

            if current_password_hash == user_to_update.mot_de_passe:
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

@app.route('/admin/stock/')
@admin_required
def admin_stock():
    today = date.today()
    items = db.session.query(PLAT).all()
    
    for item in items:
        stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=item.id_plat, jour=today).first()
        if not stock_entry:
            stock_entry = DEFINIR_STOCK(id_plat=item.id_plat, jour=today, stock=0)
            db.session.add(stock_entry)
            db.session.commit()

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
@admin_required

def view_stock_item(item_id):
    item = db.session.get(PLAT, item_id)
    today = date.today()
    stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=item_id, jour=today).first()

    if not item:
        flash("Article non trouvé.", "error")
        return redirect(url_for('admin_stock'))

    return render_template("view_stock_item.html", item=item, stock=stock_entry.stock if stock_entry else 0)


@app.route('/admin/stock/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_stock_item(item_id):
    item = db.session.get(PLAT, item_id)
    today = date.today()
    stock_entry = db.session.query(DEFINIR_STOCK).filter_by(id_plat=item_id, jour=today).first()

    if not item:
        flash("Article non trouvé.", "error")
        return redirect(url_for('admin_stock'))

    if request.method == 'POST':
        try:
            if 'reset' in request.form:
                new_stock = 0
                flash(f"Le stock pour '{item.nom_plat}' a été réinitialisé.", "success")
            else:
                new_stock = int(request.form['stock'])
                flash(f"Stock pour '{item.nom_plat}' mis à jour avec succès.", "success")

            stock_entry.stock = new_stock
            db.session.commit()
            return redirect(url_for('admin_stock', search=request.args.get('search', '')))
        except ValueError:
            flash("Veuillez entrer une quantité valide.", "error")
    return redirect(url_for('admin_stock'))

@app.route('/creer-avis/', methods=['GET', 'POST'])
@login_required
def creer_avis():
    if request.method == 'POST':
        note = request.form.get('note')
        commentaire = request.form.get('commentaire')

        if not note or not commentaire:
            flash("Veuillez fournir une note et un commentaire.", "error")
            return redirect(url_for('creer_avis'))

        nouvel_avis = AVIS(
            id_client=current_user.id_client,
            note=int(note),
            commentaire=commentaire
        )
        db.session.add(nouvel_avis)
        db.session.commit()
        flash("Merci ! Votre avis a été publié avec succès.", "success")
        return redirect(url_for('avis_page'))

    return render_template("creation_avis.html")

@app.route('/admin/banni/')
@admin_required
def admin_banni():
    results = (
        db.session.query(CLIENT, func.count(COMMANDE.id_commande).label('nb_non_recup'))
        .join(COMMANDE)
        .filter(COMMANDE.statut == 'non récupéré', CLIENT.banni.is_(False))
        .group_by(CLIENT.id_client)
        .order_by(desc('nb_non_recup'))
        .all()
    )
    clients = [
        {
            'client': r[0],
            'nb_non_recup': int(r[1])
        }
        for r in results
    ]
    return render_template("admin_banni.html", clients=clients)


@app.route('/admin/ban/<int:client_id>', methods=['POST'])
@admin_required
def ban_client(client_id):
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
@admin_required
def admin_bannis():
    clients = db.session.query(CLIENT).filter_by(banni=True).all()
    return render_template('admin_bannis.html', clients=clients)


@app.route('/admin/unban/<int:client_id>', methods=['POST'])
@admin_required
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
@admin_required
def admin_index():
    today = date.today()
    yesterday = today - timedelta(days=1)
    current_month_start = today.replace(day=1)
    last_month_end = current_month_start - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    current_year_start = today.replace(day=1, month=1)
    last_year_start = current_year_start.replace(year=today.year - 1)
    last_year_end = current_year_start - timedelta(days=1)

    def get_stats(start_date, end_date):
        stats = db.session.query(
            func.count(COMMANDE.id_commande),
            func.sum(COMMANDE.montant_total)
        ).filter(
            COMMANDE.statut == "récupéré",
            COMMANDE.date_commande.between(start_date, end_date)
        ).first()
        return stats[0] or 0, float(stats[1]) if stats[1] is not None else 0.0

    lst_recup_auj, ca_auj = get_stats(today, today + timedelta(days=1))
    lst_recup_mois, ca_mois = get_stats(current_month_start, today + timedelta(days=1))
    lst_recup_annee, ca_annee = get_stats(current_year_start, today + timedelta(days=1))

    _, ca_hier = get_stats(yesterday, today)
    _, ca_mois_dernier = get_stats(last_month_start, last_month_end)
    _, ca_annee_derniere = get_stats(last_year_start, last_year_end)

    ca_pourcentage_hier_auj = round((ca_auj - ca_hier) / ca_hier * 100) if ca_hier != 0 else 0
    ca_pourcentage_mois = round((ca_mois - ca_mois_dernier) / ca_mois_dernier * 100) if ca_mois_dernier != 0 else 0
    ca_pourcentage_annee_derniere = round((ca_annee - ca_annee_derniere) / ca_annee_derniere * 100) if ca_annee_derniere != 0 else 0

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
        plats = db.session.query(PLAT).filter(PLAT.id_plat.in_(ids_top)).all()
        plats_map = {p.id_plat: p for p in plats}
        for pid, qte in top_items:
            top_5_ventes.append((plats_map.get(pid), qte))

    liste_plat = (
    db.session.query(PLAT.nom_plat, DEFINIR_STOCK.stock, DEFINIR_STOCK.jour)
    .join(DEFINIR_STOCK, PLAT.id_plat == DEFINIR_STOCK.id_plat)
    .all()
    )

    tout_plats = db.session.query(PLAT.nom_plat).all()

    plats_a_exclure = set()
    for nom, stock, jour in liste_plat:
        if stock != 0 and jour == today:
            plats_a_exclure.add(nom)

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


@app.route('/admin/plats/')
@admin_required
def admin_plats():
    plats = db.session.query(PLAT).all()
    return render_template('admin_plats.html', plats=plats)


@app.route('/admin/plats/ajouter/', methods=['GET', 'POST'])
@admin_required
def admin_add_plat():
    form = PlatForm()
    categories = db.session.query(CATEGORIE).all()
    form.id_categorie.choices = [(c.id_categorie, c.nom_categorie) for c in categories]
    if form.validate_on_submit():
        p = PLAT(
            nom_plat=form.nom_plat.data,
            id_categorie=form.id_categorie.data or None,
            description=form.description.data,
            longue_description=form.longue_description.data,
            prix=form.prix.data,
            disponible=(form.disponible.data == '1'),
            image_url=form.image_url.data,
            vegetarien=form.vegetarien.data,
            vegan=form.vegan.data,
            gluten=form.gluten.data,
            lactose=form.lactose.data,
            fruit_a_coque=form.fruit_a_coque.data,
            crustaces=form.crustaces.data
        )
        db.session.add(p)
        db.session.commit()
        flash("Plat ajouté.", "success")
        return redirect(url_for('admin_plats'))
    return render_template('admin_plat_form.html', form=form, action='Ajouter')


@app.route('/admin/plats/<int:id_plat>/editer/', methods=['GET', 'POST'])
@admin_required
def admin_edit_plat(id_plat):
    plat = db.session.query(PLAT).get(id_plat)
    if not plat:
        flash("Plat introuvable.", "error")
        return redirect(url_for('admin_plats'))
    form = PlatForm(obj=plat)
    categories = db.session.query(CATEGORIE).all()
    form.id_categorie.choices = [(c.id_categorie, c.nom_categorie) for c in categories]
    if form.validate_on_submit():
        plat.nom_plat = form.nom_plat.data
        plat.id_categorie = form.id_categorie.data or None
        plat.description = form.description.data
        plat.longue_description = form.longue_description.data
        plat.prix = form.prix.data
        plat.disponible = (form.disponible.data == '1')
        plat.image_url = form.image_url.data
        plat.vegetarien = form.vegetarien.data
        plat.vegan = form.vegan.data
        plat.gluten = form.gluten.data
        plat.lactose = form.lactose.data
        plat.fruit_a_coque = form.fruit_a_coque.data
        plat.crustaces = form.crustaces.data
        db.session.add(plat)
        db.session.commit()
        flash("Plat modifié.", "success")
        return redirect(url_for('admin_plats'))
    form.disponible.data = '1' if plat.disponible else '0'
    return render_template('admin_plat_form.html', form=form, action='Éditer', plat=plat)


@app.route('/admin/plats/<int:id_plat>/supprimer/', methods=['POST'])
@admin_required
def admin_delete_plat(id_plat):
    plat = db.session.query(PLAT).get(id_plat)
    if not plat:
        flash("Plat introuvable.", "error")
        return redirect(url_for('admin_plats'))
    try:
        db.session.delete(plat)
        db.session.commit()
        flash("Plat supprimé.", "success")
    except Exception:
        db.session.rollback()
        flash("Impossible de supprimer le plat (dépendances).", "error")
    return redirect(url_for('admin_plats'))




@app.route('/admin/menus/')
@admin_required
def admin_menus():
    menus = db.session.query(MENU).all()
    return render_template('admin_menus.html', menus=menus)


@app.route('/admin/menus/ajouter/', methods=['GET', 'POST'])
@admin_required
def admin_add_menu():
    form = MenuForm()
    plats = db.session.query(PLAT).all()
    plats_choices = [(p.id_plat, p.nom_plat) for p in plats]
    form.entrees.choices = plats_choices
    form.plats.choices = plats_choices
    form.desserts.choices = plats_choices
    if form.validate_on_submit():
        m = MENU(
            nom_menu=form.nom_menu.data,
            description=form.description.data,
            prix=form.prix.data,
            image_url=form.image_url.data
        )
        db.session.add(m)
        db.session.commit()
        # Ajouter les plats associés
        for plat_id in form.entrees.data:
            contenir = CONTENIR(id_menu=m.id_menu, id_plat=plat_id, type_plat=0)
            db.session.add(contenir)
        for plat_id in form.plats.data:
            contenir = CONTENIR(id_menu=m.id_menu, id_plat=plat_id, type_plat=1)
            db.session.add(contenir)
        for plat_id in form.desserts.data:
            contenir = CONTENIR(id_menu=m.id_menu, id_plat=plat_id, type_plat=2)
            db.session.add(contenir)
        db.session.commit()
        flash("Menu ajouté.", "success")
        return redirect(url_for('admin_menus'))
    return render_template('admin_menu_form.html', form=form, action='Ajouter')


@app.route('/admin/menus/<int:id_menu>/editer/', methods=['GET', 'POST'])
@admin_required
def admin_edit_menu(id_menu):
    menu = db.session.query(MENU).get(id_menu)
    if not menu:
        flash("Menu introuvable.", "error")
        return redirect(url_for('admin_menus'))
    form = MenuForm(obj=menu)
    plats = db.session.query(PLAT).all()
    plats_choices = [(p.id_plat, p.nom_plat) for p in plats]
    form.entrees.choices = plats_choices
    form.plats.choices = plats_choices
    form.desserts.choices = plats_choices
    # Pré-remplir les sélections
    entrees_ids = [c.id_plat for c in menu.contenir if c.type_plat == 0]
    plats_ids = [c.id_plat for c in menu.contenir if c.type_plat == 1]
    desserts_ids = [c.id_plat for c in menu.contenir if c.type_plat == 2]
    form.entrees.data = entrees_ids
    form.plats.data = plats_ids
    form.desserts.data = desserts_ids
    if form.validate_on_submit():
        menu.nom_menu = form.nom_menu.data
        menu.description = form.description.data
        menu.prix = form.prix.data
        menu.image_url = form.image_url.data
        # Supprimer les anciennes associations
        db.session.query(CONTENIR).filter_by(id_menu=id_menu).delete()
        # Ajouter les nouvelles
        for plat_id in form.entrees.data:
            contenir = CONTENIR(id_menu=id_menu, id_plat=plat_id, type_plat=0)
            db.session.add(contenir)
        for plat_id in form.plats.data:
            contenir = CONTENIR(id_menu=id_menu, id_plat=plat_id, type_plat=1)
            db.session.add(contenir)
        for plat_id in form.desserts.data:
            contenir = CONTENIR(id_menu=id_menu, id_plat=plat_id, type_plat=2)
            db.session.add(contenir)
    if form.validate_on_submit():
        menu.nom_menu = form.nom_menu.data
        menu.description = form.description.data
        menu.prix = form.prix.data
        menu.image_url = form.image_url.data
        # Supprimer les anciennes associations
        db.session.query(CONTENIR).filter_by(id_menu=id_menu).delete()
        # Ajouter les nouvelles
        for plat_id in form.entrees.data:
            contenir = CONTENIR(id_menu=id_menu, id_plat=plat_id, type_plat=0)
            db.session.add(contenir)
        for plat_id in form.plats.data:
            contenir = CONTENIR(id_menu=id_menu, id_plat=plat_id, type_plat=1)
            db.session.add(contenir)
        for plat_id in form.desserts.data:
            contenir = CONTENIR(id_menu=id_menu, id_plat=plat_id, type_plat=2)
            db.session.add(contenir)
        db.session.commit()
        flash(f"Menu modifié. Entrées: {len(form.entrees.data)}, Plats: {len(form.plats.data)}, Desserts: {len(form.desserts.data)}", "success")
        return redirect(url_for('admin_menus'))
    return render_template('admin_menu_form.html', form=form, action='Éditer', menu=menu)


@app.route('/admin/menus/<int:id_menu>/supprimer/', methods=['POST'])
@admin_required
def admin_delete_menu(id_menu):
    menu = db.session.query(MENU).get(id_menu)
    if not menu:
        flash("Menu introuvable.", "error")
        return redirect(url_for('admin_menus'))
    try:
        db.session.delete(menu)
        db.session.commit()
        flash("Menu supprimé.", "success")
    except Exception:
        db.session.rollback()
        flash("Impossible de supprimer le menu (dépendances).", "error")
    return redirect(url_for('admin_menus'))




if __name__ == "__main__":
    app.run()