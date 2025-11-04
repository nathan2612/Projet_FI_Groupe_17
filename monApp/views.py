from monApp.models import PLAT,CATEGORIE,CLIENT, DEFINIR_STOCK
from .app import app
from flask import render_template, request, url_for, redirect, flash
from .app import db
from .forms import InscriptionForm, ConnexionForm
from flask_login import login_user,logout_user,login_required, current_user
from hashlib import sha256
from math import ceil
import logging as lg
from datetime import datetime, date

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


if __name__ == "__main__":
    app.run()