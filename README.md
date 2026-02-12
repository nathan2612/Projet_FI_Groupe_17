# Projet Oumami - Lancer le site localement

Ce dépôt contient une application Flask (Oumami) utilisée pour la gestion d'un menu / panier / commandes.

Ci‑dessous les étapes pour préparer l'environnement, initialiser la base et lancer le site en local.

## Prérequis

- Python 3.10+ (ou 3.8+ compatible avec les dépendances listées)
- MySQL / MariaDB (accessible depuis la machine qui exécute l'application)
- git, un shell (bash)

Fichier de dépendances: `requirements.txt` (utilisé avec pip).

## Installer l'environnement

- pour l'instalation il suffit de cloner le dépôt :

```bash
git clone https://github.com/nathan2612/Projet_FI_Groupe_17
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
## Instalation de l'application

pour installer l'application, il suffit de faire ces commandes dans le terminal : 

```bash
cd Projet_FI_Groupe_17
chmod +x ./app.sh 
./app.sh
```

## Lancer le site
Une fois les étapes précédentes terminées, vous pouvez aller sur le site en ouvrant votre navigateur à l'adresse suivante : 

url : `http://localhost:5000`