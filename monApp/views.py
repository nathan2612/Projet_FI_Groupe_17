from monApp.models import PLAT,CATEGORIE
from .app import app
from flask import render_template,request
from .app import db
from math import ceil

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")

@app.route('/produits/')
def produits():
    cat_id = request.args.get('cat_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 9

    # Build base query with optional category filter
    query = db.session.query(PLAT)
    if cat_id is not None:
        query = query.filter_by(id_categorie=cat_id)

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
    )

if __name__ == "__main__":
    app.run()