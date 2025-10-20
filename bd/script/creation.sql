
CREATE TABLE CATEGORIES (
    id_categorie INT PRIMARY KEY,
    nom_categorie VARCHAR(100),
    description TEXT
);

CREATE TABLE PLATS (
    id_plat INT,
    id_categorie INT,
    nom_plat VARCHAR(150),
    description TEXT,
    prix DECIMAL(10,2),
    stock_ventes INT,
    stock_reservation INT,
    vegetarien BOOLEAN,
    sans_gluten BOOLEAN,
    PRIMARY KEY (id_plat, id_categorie)
);

create table CLIENTS(
    id_client INT,
    nom_client VARCHAR(100),
    prenom_client VARCHAR(100),
    email VARCHAR(150),
    telephone VARCHAR(15),
    banni BOOLEAN default false,
    PRIMARY KEY (id_client)
);

create table RESERVATION(
    id_reservation INT,
    id_client INT,
    date_reservation DATE,
    heure_reservation TIME,
    nombre_personnes INT CHECK (nombre_personnes < 13),
    PRIMARY KEY (id_reservation)
);

CREATE TABLE COMMANDES (
    id_commande INT,
    id_client INT,
    date_commande DATE,
    statut VARCHAR(50) DEFAULT 'En attente',
    montant_total DECIMAL(10,2),
    sur_place BOOLEAN,
    PRIMARY KEY (id_commande)
);

CREATE TABLE MENU(
    id_menu INT,
    nom_menu VARCHAR(150),
    description TEXT,
    prix DECIMAL(10,2),
    PRIMARY KEY (id_menu)
);

create table CONTENIR(
    id_menu INT,
    id_plat INT,
    PRIMARY KEY (id_menu, id_plat)
);

CREATE TABLE APPARTENIR_PLATS (
    id_commande INT,
    id_plat INT,
    quantite INT,
    prix_unitaire DECIMAL(10,2),
    PRIMARY KEY (id_commande, id_plat)
);

CREATE TABLE APPARTENIR_MENUS (
    id_commande INT,
    id_menu INT,
    quantite INT,
    prix_unitaire DECIMAL(10,2),
    PRIMARY KEY (id_commande, id_menu)
);

CREATE TABLE AVIS (
    id_avis INT,
    id_client INT,
    note INT CHECK (note >= 1 AND note <= 5),
    commentaire TEXT,
    PRIMARY KEY (id_avis)
);

CREATE TABLE DEFINIR_STOCK(
    id_plat INT,
    jour DATE,
    stock INT,
    PRIMARY KEY (id_plat, jour)
)

ALTER TABLE APPARTENIR_MENUS ADD FOREIGN KEY (id_commande) REFERENCES COMMANDES(id_commande);
ALTER TABLE APPARTENIR_MENUS ADD FOREIGN KEY (id_menu) REFERENCES MENU(id_menu);
ALTER TABLE APPARTENIR_PLATS ADD FOREIGN KEY (id_commande) REFERENCES COMMANDES(id_commande);
ALTER TABLE APPARTENIR_PLATS ADD FOREIGN KEY (id_plat) REFERENCES PLATS(id_plat);
ALTER TABLE CONTENIR ADD FOREIGN KEY (id_menu) REFERENCES MENU(id_menu);
ALTER TABLE CONTENIR ADD FOREIGN KEY (id_plat) REFERENCES PLATS(id_plat);
ALTER TABLE COMMANDES ADD FOREIGN KEY (id_client) REFERENCES CLIENTS(id_client);
ALTER TABLE RESERVATION ADD FOREIGN KEY (id_client) REFERENCES CLIENTS(id_client);
ALTER TABLE AVIS ADD FOREIGN KEY (id_client) REFERENCES CLIENTS(id_client);