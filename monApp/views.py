from monApp.models import PLAT,CATEGORIE,CLIENT,COMMANDE
from .app import app
from flask import render_template, request, url_for, redirect, flash
from .app import db
from .forms import InscriptionForm, ConnexionForm
from flask_login import login_user,logout_user,login_required
from sqlalchemy import func, desc
from hashlib import sha256
from math import ceil
import logging as lg
from flask import flash

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

@app.route('/connexion/',  methods =("GET","POST" ,))
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

@app.route('/panier/')
def panier():
    return render_template("index.html")

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

if __name__ == "__main__":
    app.run()