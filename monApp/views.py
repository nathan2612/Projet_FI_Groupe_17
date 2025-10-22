from monApp.models import PLAT,CATEGORIE
from .app import app
from flask import render_template,request
from .app import db

@app.route('/')
@app.route('/index/')
def index():
    return render_template("index.html")

@app.route('/produits/')
def produits():
    cat_id = request.args.get('cat_id', type=int)
    if cat_id == 5:
        produits = db.session.query(PLAT).all()
    elif cat_id:
        produits = db.session.query(PLAT).filter_by(id_categorie=cat_id).all()
    else:
        produits = db.session.query(PLAT).all()
    categories = db.session.query(CATEGORIE).all()
    return render_template("produits.html", produits=produits, cat_id=cat_id, categories=categories)

if __name__ == "__main__":
    app.run()