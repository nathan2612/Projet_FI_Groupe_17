from monApp.models import PLAT,CATEGORIE
from .app import app
from flask import render_template, request, url_for
from .app import db
from math import ceil

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
def propos():
    return render_template("propos.html")

@app.route('/nouveautes/')
def nouveaute():
    return render_template("nouveaute.html")



if __name__ == "__main__":
    app.run()