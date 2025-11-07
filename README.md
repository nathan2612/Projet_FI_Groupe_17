# Projet Oumami - Lancer le site localement

Ce dépôt contient une application Flask (Oumami) utilisée pour la gestion d'un menu / panier / commandes.

Ci‑dessous les étapes pour préparer l'environnement, initialiser la base et lancer le site en local.

## Prérequis

- Python 3.10+ (ou 3.8+ compatible avec les dépendances listées)
- MySQL / MariaDB (accessible depuis la machine qui exécute l'application)
- git, un shell (bash)

Fichier de dépendances: `requirement.txt` (utilisé avec pip).

## Installer l'environnement

1. Créer et activer un environnement virtuel (recommandé) :

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Installer les dépendances :

```bash
pip install -r requirement.txt
```

## Configuration de la base de données

L'application lit la variable `SQLALCHEMY_DATABASE_URI` depuis `config.py`, qui par défaut pointe vers :

```
mysql+pymysql://nathan:nathan@localhost:3306/oumami?charset=utf8mb4
```

Il faut changer cette ligne selon vos login et votre base de donné, comme ceci : 

```bash
'mysql+pymysql://user:password@host:3306/nom_de_la_base?charset=utf8mb4'
```

### Préparer la base (création + données de test)

L'application fournit une commande pour charger les fixtures YAML :

```bash
flask loaddb monApp/data/data.yml
```

Attention : `flask loaddb` fait `drop_all()` puis `create_all()` — il **efface** la base existante avant de la recréer.

## Lancer l'application

En développement :

```bash
flask run
```
