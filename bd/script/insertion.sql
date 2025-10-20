-- Script d'insertion pour la base de données Restaurant

-- ============================================
-- Insertion des CATEGORIES
-- ============================================
INSERT INTO CATEGORIES (id_categorie, nom_categorie, description) VALUES
(1, 'Entrées', 'Plats servis en début de repas'),
(2, 'Plats principaux', 'Plats de résistance'),
(3, 'Desserts', 'Plats sucrés en fin de repas'),
(4, 'Boissons', 'Boissons chaudes et froides'),
(5, 'Salades', 'Salades composées et fraîches');

-- ============================================
-- Insertion des PLATS
-- ============================================
INSERT INTO PLATS (id_plat, id_categorie, nom_plat, description, prix, stock) VALUES
-- Entrées
(1, 1, 'Salade de papaye (Som Tam)', 'Salade de papaye verte, cacahuètes, piment', 8.50, 25),
(2, 1, 'Soupe miso', 'Soupe miso traditionnelle avec tofu et algues', 6.00, 30),
(3, 1, 'Gyoza vapeur', 'Raviolis japonais farcis au porc et légumes', 7.00, 20),
(4, 1, 'Tataki de thon', 'Thon mi-cuit, sauce soja, sésame', 12.00, 15),

-- Plats principaux
(5, 2, 'Curry rouge thaï au boeuf', 'Boeuf sauté au curry rouge, riz jasmin', 18.00, 30),
(6, 2, 'Poulet teriyaki', 'Poulet laqué teriyaki, légumes sautés', 15.50, 25),
(7, 2, 'Saumon grillé au gingembre', 'Pavé de saumon, sauce soja-gingembre, riz basmati', 19.50, 20),
(8, 2, 'Pad Thai crevettes', 'Nouilles sautées, crevettes, pousses de soja, cacahuètes', 11.00, 40),
(9, 2, 'Boeuf basilic thaï (Pad Kra Pao)', 'Boeuf haché, basilic thaï, piment, riz', 13.50, 22),
(10, 2, 'Riz cantonais', 'Riz sauté aux œufs, jambon, petits pois', 14.00, 18),

-- Desserts
(11, 3, 'Mochi glacé', 'Pâtisserie japonaise fourrée glacée', 6.50, 35),
(12, 3, 'Mango sticky rice', 'Riz gluant à la mangue et lait de coco', 7.00, 28),
(13, 3, 'Panna cotta coco', 'Panna cotta au lait de coco, coulis de fruits', 5.50, 40),
(14, 3, 'Flan au matcha', 'Flan onctueux parfumé au thé matcha', 6.00, 30),
(15, 3, 'Dorayaki', 'Pancake japonais fourré à la pâte de haricot', 7.50, 25),

-- Boissons
(16, 4, 'Thé matcha', 'Thé matcha japonais préparé traditionnellement', 2.50, 100),
(17, 4, 'Thé vert sencha', 'Thé vert japonais sencha', 3.00, 80),
(18, 4, 'Jus de litchi', 'Jus de litchi frais', 4.50, 50),
(19, 4, 'Bubble tea au lait', 'Thé au lait avec perles de tapioca', 3.50, 60),
(20, 4, 'Eau de coco', 'Noix de coco fraîche', 2.00, 100),

-- Salades
(21, 5, 'Salade wakame', 'Salade d''algues wakame, vinaigrette au sésame', 12.50, 20),
(22, 5, 'Salade thaïe aux crevettes', 'Crevettes, mangue, menthe, sauce nuoc mam', 11.00, 25),
(23, 5, 'Salade vietnamienne', 'Salade croquante avec boeuf mariné et herbes fraîches', 9.50, 30);

-- ============================================
-- Insertion des CLIENTS
-- ============================================
INSERT INTO CLIENTS (id_client, nom_client, prenom_client, email, telephone) VALUES
(1, 'Dupont', 'Jean', 'jean.dupont@email.com', '0601020304'),
(2, 'Martin', 'Sophie', 'sophie.martin@email.com', '0612345678'),
(3, 'Bernard', 'Pierre', 'pierre.bernard@email.com', '0623456789'),
(4, 'Dubois', 'Marie', 'marie.dubois@email.com', '0634567890'),
(5, 'Laurent', 'Luc', 'luc.laurent@email.com', '0645678901'),
(6, 'Simon', 'Julie', 'julie.simon@email.com', '0656789012'),
(7, 'Michel', 'Thomas', 'thomas.michel@email.com', '0667890123'),
(8, 'Lefebvre', 'Emma', 'emma.lefebvre@email.com', '0678901234'),
(9, 'Leroy', 'Antoine', 'antoine.leroy@email.com', '0689012345'),
(10, 'Moreau', 'Camille', 'camille.moreau@email.com', '0690123456');

-- ============================================
-- Insertion des RESERVATIONS
-- ============================================
INSERT INTO RESERVATION (id_reservation, id_client, date_reservation, heure_reservation, nombre_personnes) VALUES
(1, 1, '2025-10-25', '19:00:00', 4),
(2, 2, '2025-10-25', '20:00:00', 2),
(3, 3, '2025-10-26', '19:30:00', 6),
(4, 4, '2025-10-26', '20:30:00', 3),
(5, 5, '2025-10-27', '19:00:00', 8),
(6, 6, '2025-10-27', '21:00:00', 2),
(7, 7, '2025-10-28', '19:30:00', 5),
(8, 8, '2025-10-28', '20:00:00', 4),
(9, 9, '2025-10-29', '19:00:00', 12),
(10, 10, '2025-10-29', '20:30:00', 2);

-- ============================================
-- Insertion des MENUS
-- ============================================
INSERT INTO MENU (id_menu, nom_menu, description, prix) VALUES
(1, 'Menu Découverte', 'Entrée + Plat + Dessert', 28.00),
(2, 'Menu Express', 'Plat + Dessert', 20.00),
(3, 'Menu Enfant', 'Plat + Dessert + Boisson', 12.00),
(4, 'Menu Végétarien', 'Entrée + Plat végétarien + Dessert', 25.00),
(5, 'Menu Gastronomique', 'Entrée + Plat premium + Dessert + Café', 45.00);

-- ============================================
-- Insertion table CONTENIR (Menu-Plats)
-- ============================================
INSERT INTO CONTENIR (id_menu, id_plat) VALUES
-- Menu Découverte
(1, 1), (1, 5), (1, 11),
-- Menu Express
(2, 6), (2, 12),
-- Menu Enfant
(3, 8), (3, 13), (3, 19),
-- Menu Végétarien
(4, 3), (4, 10), (4, 14),
-- Menu Gastronomique
(5, 4), (5, 7), (5, 15), (5, 16);

-- ============================================
-- Insertion des COMMANDES
-- ============================================
INSERT INTO COMMANDES (id_commande, id_client, date_commande, statut, montant_total, sur_place) VALUES
(1, 1, '2025-10-20', 'Livrée', 45.50, TRUE),
(2, 2, '2025-10-20', 'En cours', 32.00, FALSE),
(3, 3, '2025-10-19', 'Livrée', 67.50, TRUE),
(4, 4, '2025-10-19', 'Annulée', 25.00, FALSE),
(5, 5, '2025-10-18', 'Livrée', 89.00, TRUE),
(6, 6, '2025-10-18', 'En attente', 28.00, TRUE),
(7, 7, '2025-10-17', 'Livrée', 52.50, FALSE),
(8, 8, '2025-10-17', 'En cours', 41.00, TRUE),
(9, 9, '2025-10-16', 'Livrée', 95.00, TRUE),
(10, 10, '2025-10-16', 'Livrée', 34.50, FALSE);

-- ============================================
-- Insertion table APPARTENIR (Commande-Plats)
-- ============================================
INSERT INTO APPARTENIR (id_commande, id_plat, quantite, prix_unitaire) VALUES
-- Commande 1
(1, 5, 2, 18.00),
(1, 11, 2, 6.50),
(1, 16, 2, 2.50),
-- Commande 2
(2, 8, 2, 11.00),
(2, 13, 2, 5.50),
-- Commande 3
(3, 7, 2, 19.50),
(3, 12, 2, 7.00),
(3, 1, 2, 8.50),
(3, 17, 2, 3.00),
-- Commande 4
(4, 9, 1, 13.50),
(4, 11, 1, 6.50),
(4, 16, 1, 2.50),
-- Commande 5
(5, 5, 3, 18.00),
(5, 6, 2, 15.50),
(5, 11, 3, 6.50),
-- Commande 6
(6, 1, 1, 8.50),
(6, 10, 1, 14.00),
(6, 16, 1, 2.50),
-- Commande 7
(7, 7, 2, 19.50),
(7, 14, 2, 6.00),
-- Commande 8
(8, 21, 2, 12.50),
(8, 15, 2, 7.50),
-- Commande 9
(9, 4, 3, 12.00),
(10, 6, 2, 15.50),
(10, 13, 2, 5.50);

-- ============================================
-- Insertion des AVIS
-- ============================================
INSERT INTO AVIS (id_avis, id_client, note, commentaire) VALUES
(1, 1, 5, 'Excellent restaurant ! Service impeccable et plats délicieux.'),
(2, 2, 4, 'Très bon, je recommande le saumon grillé.'),
(3, 3, 5, 'Parfait pour un dîner en famille. Ambiance chaleureuse.'),
(4, 5, 5, 'Les meilleurs steaks de la ville ! Je reviendrai.'),
(5, 7, 4, 'Bonne qualité prix. Le tiramisu est à tomber.'),
(6, 8, 3, 'Correct mais un peu d''attente pour être servi.'),
(7, 9, 5, 'Idéal pour les grandes tablées. Menu gastronomique excellent.'),
(8, 10, 4, 'Pizzas délicieuses et bien garnies.'),
(9, 4, 2, 'Déçu par ma commande, pas assez copieux.'),
(10, 6, 5, 'Service rapide et personnel très agréable !');

-- ============================================
-- Fin du script d'insertion
-- ============================================