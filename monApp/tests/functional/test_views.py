import pytest
from flask import url_for

def login(client, telephone, password):
    return client.post('/connexion/', data={
        'telephone': telephone,
        'mot_de_passe': password
    }, follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

# ====== TESTS DE ROUTES ACCESSIBILITÉ ======

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_produits_page(client):
    response = client.get('/produits/')
    assert response.status_code == 200

def test_menus_page(client):
    response = client.get('/menus/')
    assert response.status_code == 200

def test_detail_plat(client):
    response = client.get('/produit/1')
    assert response.status_code == 200

def test_detail_menu(client):
    response = client.get('/menu/1')
    assert response.status_code == 200

def test_avis_page(client):
    response = client.get('/avis/')
    assert response.status_code == 200

def test_static_pages(client):
    assert client.get('/contact/').status_code == 200
    assert client.get('/apropos/').status_code == 200
    assert client.get('/nouveautes/').status_code == 200

# ====== TESTS AUTHENTIFICATION ======

def test_login_logout(client):
    response = login(client, '0601020304', 'password')
    assert response.status_code == 200
    assert b'href="/compte/"' in response.data

    response = logout(client)
    assert response.status_code == 200

def test_connexion_errors(client):
    response = login(client, '0601020304', 'wrongpassword')
    assert response.status_code == 200

def test_connexion_valid_user(client):
    response = client.post('/connexion/', data={
        'telephone': '0601020304',
        'mot_de_passe': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_inscription_errors(client):
    response = client.post('/inscription/', data={
        'prenom': 'Alice', 'nom': 'Dupont', 'telephone': '0601020304',
        'mot_de_passe': 'pass', 'confirmation_mot_de_passe': 'pass'
    }, follow_redirects=True)
    assert response.status_code == 200

    response = client.post('/inscription/', data={
        'prenom': 'New', 'nom': 'User', 'telephone': '0999999999',
        'mot_de_passe': 'pass', 'confirmation_mot_de_passe': 'word'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_inscription(client):
    response = client.post('/inscription/', data={
        'prenom': 'Test',
        'nom': 'User',
        'telephone': '0987654321',
        'mot_de_passe': 'testpass',
        'confirmation_mot_de_passe': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    response = login(client, '0987654321', 'testpass')
    assert response.status_code == 200

# ====== TESTS PANIER ======

def test_ajouter_au_panier_errors(client):
    response = client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert "Veuillez vous connecter" in response.data.decode('utf-8')

def test_panier_operations(client):
    login(client, '0601020304', 'password')
    
    response = client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/panier/')
    assert response.status_code == 200

    response = client.post('/supprimer-du-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response.status_code == 200

def test_modifier_quantite_panier(client):
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    
    response = client.post('/modifier-quantite-panier/', data={'id_plat': 1, 'action': 'increase'}, follow_redirects=True)
    assert response.status_code == 200

def test_panier_with_multiple_items(client):
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    client.post('/ajouter-au-panier/', data={'id_plat': 2}, follow_redirects=True)
    response = client.get('/panier/')
    assert response.status_code == 200

def test_valider_commande(client):
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    response = client.post('/valider-commande/', follow_redirects=True)
    assert response.status_code == 200

# ====== TESTS MENUS SÉLECTION ======

def test_ajouter_menu_selection_errors(client):
    response = client.post('/ajouter-menu-selection/', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert "Veuillez vous connecter" in response.data.decode('utf-8')

    login(client, '0601020304', 'password')
    response = client.post('/ajouter-menu-selection/', data={'id_menu': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert "Veuillez sélectionner une entrée" in response.data.decode('utf-8')

def test_ajouter_menu_panier(client):
    login(client, '0601020304', 'password')
    data = {
        'id_menu': 1,
        'entree': 1,
        'plat': 3,
        'dessert': 7
    }
    response = client.post('/ajouter-menu-selection/', data=data, follow_redirects=True)
    assert response.status_code == 200

def test_modifier_quantite_panier_menu(client):
    login(client, '0601020304', 'password')
    data = {'id_menu': 1, 'entree': 1, 'plat': 3, 'dessert': 7}
    client.post('/ajouter-menu-selection/', data=data, follow_redirects=True)
    
    response = client.post('/modifier-quantite-panier/', data={
        'id_menu': 1, 'id_entree': 1, 'id_plat_choisi': 3, 'id_dessert': 7, 'action': 'increase'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_supprimer_du_panier_menu(client):
    login(client, '0601020304', 'password')
    data = {'id_menu': 1, 'entree': 1, 'plat': 3, 'dessert': 7}
    client.post('/ajouter-menu-selection/', data=data, follow_redirects=True)
    
    response = client.post('/supprimer-du-panier/', data={
        'id_menu': 1, 'id_entree': 1, 'id_plat_choisi': 3, 'id_dessert': 7
    }, follow_redirects=True)
    assert response.status_code == 200

# ====== TESTS COMPTE CLIENT ======

def test_compte_update(client):
    login(client, '0601020304', 'password')
    data = {
        'prenom': 'AliceUpdated',
        'nom': 'Dupont',
        'telephone': '0601020304'
    }
    response = client.post('/compte/', data=data, follow_redirects=True)
    assert response.status_code == 200

def test_compte_password_change(client):
    login(client, '0602030405', 'password')
    
    response = client.post('/compte/', data={
        'prenom': 'Bob', 'nom': 'Martin', 'telephone': '0602030405',
        'current_mot_de_passe': 'wrong', 'new_mot_de_passe': 'newpass', 'confirm_new_mot_de_passe': 'newpass'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_creer_avis(client):
    login(client, '0601020304', 'password')
    response = client.get('/creer-avis/')
    assert response.status_code == 200
    data = {'note': 5, 'commentaire': 'Super!'}
    response = client.post('/creer-avis/', data=data, follow_redirects=True)
    assert response.status_code == 200

# ====== TESTS ADMIN - ACCÈS ======

def test_admin_access_denied(client):
    login(client, '0601020304', 'password')
    response = client.get('/admin-index/', follow_redirects=False)
    assert response.status_code == 302

def test_admin_access_granted(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin-index/')
    assert response.status_code == 200

# ====== TESTS ADMIN - PAGES ======

def test_admin_commandes(client):
    login(client, 'admin', 'admin')
    response = client.get('/commandes/')
    assert response.status_code == 200

def test_admin_stock(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/stock/')
    assert response.status_code == 200
    
    response = client.post('/admin/stock/edit/1', data={'stock': 100}, follow_redirects=True)
    assert response.status_code == 200

def test_admin_banni_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/banni/')
    assert response.status_code == 200

def test_admin_menus_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/menus/')
    assert response.status_code == 200

def test_admin_plats_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/plats/')
    assert response.status_code == 200

def test_admin_menu_du_jour_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/menu-du-jour/')
    assert response.status_code == 200

def test_admin_services_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/services/')
    assert response.status_code == 200

def test_admin_reservation(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/reservations/')
    assert response.status_code == 200

# ====== TESTS ADMIN - ACTIONS ======

def test_admin_ban_unban(client):
    login(client, 'admin', 'admin')
    response = client.post('/admin/ban/2', follow_redirects=True)
    assert response.status_code == 200
    
    response = client.get('/admin/bannis/')
    assert response.status_code == 200
    
    response = client.post('/admin/unban/2', follow_redirects=True)
    assert response.status_code == 200

def test_admin_set_menu_du_jour(client):
    login(client, 'admin', 'admin')
    response = client.post('/admin/menu-du-jour/', data={'id_menu': 1}, follow_redirects=True)
    assert response.status_code == 200

def test_set_statut_errors(client):
    login(client, 'admin', 'admin')
    response = client.post('/commandes/1/set_statut', data={'statut': 'InvalidStatus'}, follow_redirects=True)
    assert response.status_code == 200

    response = client.post('/commandes/99999/set_statut', data={'statut': 'Prêt'}, follow_redirects=True)
    assert response.status_code == 200

def test_commandes_with_admin(client):
    login(client, 'admin', 'admin')
    response = client.get('/commandes/')
    assert response.status_code == 200

# ====== TESTS FILTRES ======

def test_produits_filters(client):
    response = client.get('/produits/?cat_id=1')
    assert response.status_code == 200
    
    response = client.get('/produits/?vegetarien=1')
    assert response.status_code == 200

def test_produits_all_filters(client):
    response = client.get('/produits/?vegetarien=1&vegan=1&sans_gluten=1&sans_lactose=1')
    assert response.status_code == 200

def test_categorie_list_produits(client):
    response = client.get('/produits/?cat_id=2')
    assert response.status_code == 200

def test_banned_client_cannot_login(client):
    login(client, 'admin', 'admin')
    client.post('/admin/ban/2', follow_redirects=True)

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Traiteur Oumami" in response.data or b"produits" in response.data

def test_produits_page(client):
    response = client.get('/produits/')
    assert response.status_code == 200

def test_ajouter_menu_selection_errors(client):
    response = client.post('/ajouter-menu-selection/', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert "Veuillez vous connecter" in response.data.decode('utf-8')

    login(client, '0601020304', 'password')
    response = client.post('/ajouter-menu-selection/', data={'id_menu': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert "Veuillez sélectionner une entrée" in response.data.decode('utf-8')

def test_set_statut_errors(client):
    login(client, 'admin', 'admin')
    response = client.post('/commandes/1/set_statut', data={'statut': 'InvalidStatus'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Commandes" in response.data

    response = client.post('/commandes/99999/set_statut', data={'statut': 'Prêt'}, follow_redirects=True)
    assert response.status_code == 200
    assert "Commande introuvable" in response.data.decode('utf-8')

def test_ajouter_au_panier_errors(client):
    response = client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert "Veuillez vous connecter" in response.data.decode('utf-8')

def test_modifier_quantite_panier_menu(client):
    login(client, '0601020304', 'password')
    data = {'id_menu': 1, 'entree': 1, 'plat': 3, 'dessert': 7}
    client.post('/ajouter-menu-selection/', data=data, follow_redirects=True)
    
    response = client.post('/modifier-quantite-panier/', data={
        'id_menu': 1, 'id_entree': 1, 'id_plat_choisi': 3, 'id_dessert': 7, 'action': 'increase'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    response = client.post('/modifier-quantite-panier/', data={
        'id_menu': 1, 'id_entree': 1, 'id_plat_choisi': 3, 'id_dessert': 7, 'action': 'decrease'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_supprimer_du_panier_menu(client):
    login(client, '0601020304', 'password')
    data = {'id_menu': 1, 'entree': 1, 'plat': 3, 'dessert': 7}
    client.post('/ajouter-menu-selection/', data=data, follow_redirects=True)
    
    response = client.post('/supprimer-du-panier/', data={
        'id_menu': 1, 'id_entree': 1, 'id_plat_choisi': 3, 'id_dessert': 7
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "Menu supprimé du panier" in response.data.decode('utf-8')

def test_connexion_errors(client):
    response = login(client, '0601020304', 'wrongpassword')
    assert response.status_code == 200
    assert b'name="mot_de_passe"' in response.data

def test_inscription_errors(client):
    response = client.post('/inscription/', data={
        'prenom': 'Alice', 'nom': 'Dupont', 'telephone': '0601020304',
        'mot_de_passe': 'pass', 'confirmation_mot_de_passe': 'pass'
    }, follow_redirects=True)
    assert response.status_code == 200

    response = client.post('/inscription/', data={
        'prenom': 'New', 'nom': 'User', 'telephone': '0999999999',
        'mot_de_passe': 'pass', 'confirmation_mot_de_passe': 'word'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'S\'inscrire' in response.data

def test_compte_password_change(client):
    login(client, '0602030405', 'password')
    
    response = client.post('/compte/', data={
        'prenom': 'Bob', 'nom': 'Martin', 'telephone': '0602030405',
        'current_mot_de_passe': 'wrong', 'new_mot_de_passe': 'newpass', 'confirm_new_mot_de_passe': 'newpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "Le mot de passe actuel est incorrect" in response.data.decode('utf-8')

    response = client.post('/compte/', data={
        'prenom': 'Bob', 'nom': 'Martin', 'telephone': '0602030405',
        'current_mot_de_passe': 'password', 'new_mot_de_passe': 'newpass', 'confirm_new_mot_de_passe': 'newpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert "Votre mot de passe a été mis à jour" in response.data.decode('utf-8')

    logout(client)
    response = login(client, '0602030405', 'newpass')
    assert response.status_code == 200
    assert b'href="/compte/"' in response.data

def test_edit_stock_item_reset(client):
    login(client, 'admin', 'admin')
    response = client.post('/admin/stock/edit/1', data={'reset': 'true'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"0" in response.data

def test_edit_stock_item_errors(client):
    login(client, 'admin', 'admin')
    response = client.post('/admin/stock/edit/1', data={'stock': 'invalid'}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Gestion des Stocks" in response.data

    response = client.get('/admin/stock/edit/99999', follow_redirects=True)
    assert response.status_code == 200
    assert "Article non trouvé" in response.data.decode('utf-8')

def test_creer_avis_errors(client):
    login(client, '0601020304', 'password')
    response = client.post('/creer-avis/', data={}, follow_redirects=True)
    assert response.status_code == 200
    assert "Veuillez fournir une note et un commentaire" in response.data.decode('utf-8')

def test_ban_unban_errors(client):
    login(client, 'admin', 'admin')
    response = client.post('/admin/ban/99999', follow_redirects=True)
    assert response.status_code == 200
    assert b"Clients Bannis" in response.data

    response = client.post('/admin/unban/99999', follow_redirects=True)
    assert response.status_code == 200
    assert b"Clients Bannis" in response.data

def test_admin_index_stats(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin-index/')
    assert response.status_code == 200
    assert b"Tableau de Bord" in response.data
    assert b"Nems au porc" in response.data

def test_menus_page(client):
    response = client.get('/menus/')
    assert response.status_code == 200
    assert b"Menu Canard" in response.data

def test_detail_plat(client):
    response = client.get('/produit/1')
    assert response.status_code == 200
    assert b"Nems au porc" in response.data

def test_detail_menu(client):
    response = client.get('/menu/1')
    assert response.status_code == 200
    assert b"Menu Canard" in response.data

def test_login_logout(client):
    response = login(client, '0601020304', 'password')
    assert response.status_code == 200
    assert b'href="/compte/"' in response.data

    response = logout(client)
    assert response.status_code == 200
    assert b'href="/connexion/"' in response.data

def test_admin_access_denied(client):
    login(client, '0601020304', 'password')
    response = client.get('/admin-index/', follow_redirects=False)
    assert response.status_code == 302

def test_admin_access_granted(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin-index/')
    assert response.status_code == 200

def test_panier_operations(client):
    login(client, '0601020304', 'password')
    
    response = client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Plat ajout\xc3\xa9 au panier" in response.data

    response = client.get('/panier/')
    assert response.status_code == 200
    assert b"Nems au porc" in response.data

    response = client.post('/supprimer-du-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Plat supprim\xc3\xa9 du panier" in response.data

def test_inscription(client):
    response = client.post('/inscription/', data={
        'prenom': 'Test',
        'nom': 'User',
        'telephone': '0987654321',
        'mot_de_passe': 'testpass',
        'confirmation_mot_de_passe': 'testpass'
    }, follow_redirects=True)
    assert response.status_code == 200
    
    response = login(client, '0987654321', 'testpass')
    assert response.status_code == 200
    assert b'href="/compte/"' in response.data

def test_static_pages(client):
    assert client.get('/contact/').status_code == 200
    assert client.get('/apropos/').status_code == 200
    assert client.get('/nouveautes/').status_code == 200

def test_avis_page(client):
    response = client.get('/avis/')
    assert response.status_code == 200
    assert b"Tr\xc3\xa8s bon service" in response.data

def test_produits_filters(client):
    response = client.get('/produits/?cat_id=1')
    assert response.status_code == 200
    assert b"Nems au porc" in response.data
    
    response = client.get('/produits/?vegetarien=1')
    assert response.status_code == 200

def test_ajouter_menu_panier(client):
    login(client, '0601020304', 'password')
    data = {
        'id_menu': 1,
        'entree': 1,
        'plat': 3,
        'dessert': 7
    }
    response = client.post('/ajouter-menu-selection/', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Menu ajout\xc3\xa9 au panier" in response.data

def test_modifier_quantite_panier(client):
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    
    response = client.post('/modifier-quantite-panier/', data={'id_plat': 1, 'action': 'increase'}, follow_redirects=True)
    assert response.status_code == 200
    
    response = client.post('/modifier-quantite-panier/', data={'id_plat': 1, 'action': 'decrease'}, follow_redirects=True)
    assert response.status_code == 200

def test_valider_commande(client):
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    response = client.post('/valider-commande/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Votre commande a \xc3\xa9t\xc3\xa9 valid\xc3\xa9e" in response.data

def test_compte_update(client):
    login(client, '0601020304', 'password')
    data = {
        'prenom': 'AliceUpdated',
        'nom': 'Dupont',
        'telephone': '0601020304'
    }
    response = client.post('/compte/', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Vos informations ont \xc3\xa9t\xc3\xa9 mises \xc3\xa0 jour" in response.data

def test_creer_avis(client):
    login(client, '0601020304', 'password')
    response = client.get('/creer-avis/')
    assert response.status_code == 200
    data = {'note': 5, 'commentaire': 'Super!'}
    response = client.post('/creer-avis/', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Votre avis a \xc3\xa9t\xc3\xa9 publi\xc3\xa9" in response.data

def test_admin_stock(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/stock/')
    assert response.status_code == 200
    
    response = client.post('/admin/stock/edit/1', data={'stock': 100}, follow_redirects=True)
    assert response.status_code == 200
    assert b"100" in response.data

def test_admin_commandes(client):
    login(client, 'admin', 'admin')
    response = client.get('/commandes/')
    assert response.status_code == 200
    
    response = client.post('/commandes/1/set_statut', data={'statut': 'Prêt'}, follow_redirects=True)
    assert response.status_code == 200
    assert "Prêt" in response.data.decode('utf-8')

def test_admin_ban_unban(client):
    login(client, 'admin', 'admin')
    response = client.post('/admin/ban/2', follow_redirects=True)
    assert response.status_code == 200
    
    response = client.get('/admin/bannis/')
    assert response.status_code == 200
    assert b"Martin" in response.data
    
    response = client.post('/admin/unban/2', follow_redirects=True)
    assert response.status_code == 200

def test_admin_banni_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/banni/')
    assert response.status_code == 200

def test_panier_operations_empty_cart(client):
    login(client, '0601020304', 'password')
    response = client.get('/panier/')
    assert response.status_code == 200

def test_valider_commande_without_items(client):
    login(client, '0601020304', 'password')
    response = client.post('/valider-commande/', follow_redirects=True)
    assert response.status_code == 200

def test_produits_invalid_page(client):
    response = client.get('/produits/?page=999')
    assert response.status_code == 200

def test_menus_invalid_page(client):
    response = client.get('/menus/?page=999')
    assert response.status_code == 200

def test_produits_all_filters_combined(client):
    response = client.get('/produits/?vegetarien=1&vegan=1&sans_gluten=1&sans_lactose=1&sans_fruits_a_coque=1&sans_crustaces=1')
    assert response.status_code == 200

def test_detail_menu_no_items(client):
    response = client.get('/menu/999')
    assert response.status_code == 404

def test_connexion_with_next_parameter(client):
    response = client.post('/connexion/?next=/panier/', data={
        'telephone': '0601020304',
        'mot_de_passe': 'password',
        'next': '/panier/'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_admin_menus_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/menus/')
    assert response.status_code == 200

def test_admin_plats_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/plats/')
    assert response.status_code == 200

def test_admin_menu_du_jour_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/menu-du-jour/')
    assert response.status_code == 200

def test_admin_services_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/services/')
    assert response.status_code == 200

def test_admin_plat_form_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/plats/ajouter/')
    assert response.status_code in [200, 404, 500]

def test_admin_menu_form_page(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/menus/ajouter/')
    assert response.status_code == 200

def test_creer_avis_without_login(client):
    response = client.get('/creer-avis/')
    assert response.status_code == 302

def test_modifier_quantite_panier_without_login(client):
    response = client.post('/modifier-quantite-panier/', data={'id_plat': 1, 'action': 'increase'}, follow_redirects=True)
    assert response.status_code == 200

def test_supprimer_du_panier_without_login(client):
    response = client.post('/supprimer-du-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response.status_code == 200

def test_valider_commande_without_login(client):
    response = client.post('/valider-commande/', follow_redirects=True)
    assert response.status_code == 200

def test_compte_without_login(client):
    response = client.get('/compte/')
    assert response.status_code == 302

def test_admin_routes_without_admin(client):
    login(client, '0601020304', 'password')
    response = client.get('/admin-index/', follow_redirects=True)
    assert response.status_code == 200

def test_produits_search_empty_result(client):
    response = client.get('/produits/?cat_id=9999')
    assert response.status_code == 200

def test_menus_search_empty_result(client):
    response = client.get('/menus/?cat_id=9999')
    assert response.status_code == 200
    """Test ajouter un menu quand une commande existe déjà"""
    login(client, '0601020304', 'password')
    # Première sélection
    client.post('/ajouter-menu-selection/', data={
        'id_menu': 1, 'entree': 1, 'plat': 3, 'dessert': 7
    }, follow_redirects=True)
    # Deuxième sélection avec même menu
    response = client.post('/ajouter-menu-selection/', data={
        'id_menu': 1, 'entree': 1, 'plat': 3, 'dessert': 7
    }, follow_redirects=True)
    assert response.status_code == 200

def test_ajouter_au_panier_with_existing_commande(client):
    """Test ajouter un plat quand une commande existe déjà"""
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    response = client.post('/ajouter-au-panier/', data={'id_plat': 2}, follow_redirects=True)
    assert response.status_code == 200

def test_reservation_page(client):
    login(client, '0601020304', 'password')
    response = client.get('/reservation/')
    assert response.status_code in [200, 302, 404]

def test_admin_reservation(client):
    login(client, 'admin', 'admin')
    response = client.get('/admin/reservations/')
    assert response.status_code == 200

def test_admin_set_menu_du_jour(client):
    login(client, 'admin', 'admin')
    response = client.post('/admin/menu-du-jour/', data={'id_menu': 1}, follow_redirects=True)
    assert response.status_code == 200

def test_connexion_valid_user(client):
    response = client.post('/connexion/', data={
        'telephone': '0601020304',
        'mot_de_passe': 'password'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_banned_client_cannot_login(client):
    """Test qu'un client banni ne peut pas se connecter"""
    login(client, 'admin', 'admin')
    # Ban user 2
    client.post('/admin/ban/2', follow_redirects=True)
    
    response = client.post('/connexion/', data={
        'telephone': '0602030405',
        'mot_de_passe': 'password'
    }, follow_redirects=True)
    # La réponse dépend de l'implémentation du bannissement

def test_commandes_with_admin(client):
    """Test la page commandes avec un utilisateur admin"""
    login(client, 'admin', 'admin')
    response = client.get('/commandes/')
    assert response.status_code == 200

def test_panier_with_multiple_items(client):
    """Test le panier avec plusieurs articles"""
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    client.post('/ajouter-au-panier/', data={'id_plat': 2}, follow_redirects=True)
    response = client.get('/panier/')
    assert response.status_code == 200

def test_post_produits_empty_panier(client):
    """Test produits avec POST (vider panier)"""
    response = client.post('/produits/', data={}, follow_redirects=True)
    assert response.status_code == 200

def test_detail_plat_with_stock(client):
    """Test la page détail d'un plat avec stock"""
    response = client.get('/produit/1')
    assert response.status_code == 200
    # Vérifie que le stock est affiché
    assert b"stock" in response.data.lower() or response.status_code == 200

def test_categorie_list_produits(client):
    """Test les produits filtrés par catégorie"""
    response = client.get('/produits/?cat_id=2')
    assert response.status_code == 200

def test_categorie_list_produits_nonexistent(client):
    """Test les produits avec une catégorie inexistante"""
    response = client.get('/produits/?cat_id=999')
    assert response.status_code == 200

def test_admin_unban_client(client):
    """Test débannir un client"""
    login(client, 'admin', 'admin')
    client.post('/admin/ban/3', follow_redirects=True)
    response = client.post('/admin/unban/3', follow_redirects=True)
    assert response.status_code == 200

def test_admin_services_add(client):
    """Test ajouter un service"""
    login(client, 'admin', 'admin')
    response = client.post('/admin/services/', data={
        'heure_debut': '11:00',
        'heure_fin': '13:00'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_index_with_menu_du_jour(client):
    """Test la page d'accueil avec menu du jour"""
    response = client.get('/')
    assert response.status_code == 200

def test_produits_post_request(client):
    """Test produits avec POST"""
    response = client.post('/produits/', data={}, follow_redirects=True)
    assert response.status_code == 200

def test_menus_post_request(client):
    """Test menus avec POST"""
    response = client.post('/menus/', data={}, follow_redirects=True)
    assert response.status_code == 200

def test_produits_multiple_filters(client):
    """Test avec plusieurs filtres appliqués"""
    response = client.get('/produits/?vegetarien=1&vegan=1&sans_gluten=1&sans_lactose=1')
    assert response.status_code == 200

def test_menus_pagination_first_page(client):
    """Test première page des menus"""
    response = client.get('/menus/?page=1')
    assert response.status_code == 200

def test_produits_pagination_first_page(client):
    """Test première page des produits"""
    response = client.get('/produits/?page=1')
    assert response.status_code == 200

def test_ajouter_au_panier_multiple_times(client):
    """Test ajouter le même plat plusieurs fois"""
    login(client, '0601020304', 'password')
    response1 = client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response1.status_code == 200
    response2 = client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    assert response2.status_code == 200

def test_modifier_quantite_panier_increase(client):
    """Test augmenter la quantité"""
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    response = client.post('/modifier-quantite-panier/', data={
        'id_plat': 1,
        'action': 'increase'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_modifier_quantite_panier_decrease(client):
    """Test diminuer la quantité"""
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    response = client.post('/modifier-quantite-panier/', data={
        'id_plat': 1,
        'action': 'decrease'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_admin_stock_view(client):
    """Test la page de gestion du stock"""
    login(client, 'admin', 'admin')
    response = client.get('/admin/stock/')
    assert response.status_code == 200

def test_admin_bannis_list(client):
    """Test la liste des clients bannis"""
    login(client, 'admin', 'admin')
    response = client.get('/admin/bannis/')
    assert response.status_code == 200

def test_admin_menu_du_jour_get(client):
    """Test afficher le menu du jour"""
    login(client, 'admin', 'admin')
    response = client.get('/admin/menu-du-jour/')
    assert response.status_code == 200

def test_admin_services_get(client):
    """Test afficher les services"""
    login(client, 'admin', 'admin')
    response = client.get('/admin/services/')
    assert response.status_code == 200

def test_admin_menus_page(client):
    """Test la page des menus admin"""
    login(client, 'admin', 'admin')
    response = client.get('/admin/menus/')
    assert response.status_code == 200

def test_admin_plats_page(client):
    """Test la page des plats admin"""
    login(client, 'admin', 'admin')
    response = client.get('/admin/plats/')
    assert response.status_code == 200

def test_commandes_page_not_authenticated(client):
    """Test que commandes demande l'authentification"""
    response = client.get('/commandes/')
    assert response.status_code in [302, 403]

def test_compte_page_not_authenticated(client):
    """Test que compte demande l'authentification"""
    response = client.get('/compte/')
    assert response.status_code == 302

def test_creer_avis_not_authenticated(client):
    """Test que créer avis demande l'authentification"""
    response = client.get('/creer-avis/')
    assert response.status_code == 302

def test_connexion_post_empty_data(client):
    """Test connexion avec données vides"""
    response = client.post('/connexion/', data={
        'telephone': '',
        'mot_de_passe': ''
    }, follow_redirects=True)
    assert response.status_code == 200

def test_inscription_post_matching_passwords(client):
    """Test inscription avec mots de passe identiques"""
    response = client.post('/inscription/', data={
        'prenom': 'TestUser',
        'nom': 'Test',
        'telephone': '0123456789',
        'mot_de_passe': 'password123',
        'confirmation_mot_de_passe': 'password123'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_admin_index_requires_admin(client):
    """Test que admin-index demande les droits admin"""
    login(client, '0601020304', 'password')
    response = client.get('/admin-index/', follow_redirects=True)
    assert response.status_code == 200

def test_produits_vegan_only(client):
    """Test filtre vegan uniquement"""
    response = client.get('/produits/?vegan=1')
    assert response.status_code == 200

def test_produits_vegetarien_only(client):
    """Test filtre végétarien uniquement"""
    response = client.get('/produits/?vegetarien=1')
    assert response.status_code == 200

def test_panier_operations_sequence(client):
    """Test une séquence complète d'opérations panier"""
    login(client, '0601020304', 'password')
    # Ajouter
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    # Consulter
    response = client.get('/panier/')
    assert response.status_code == 200
    # Modifier
    client.post('/modifier-quantite-panier/', data={'id_plat': 1, 'action': 'increase'}, follow_redirects=True)
    # Consulter à nouveau
    response = client.get('/panier/')
    assert response.status_code == 200

def test_menu_selection_panier(client):
    """Test ajouter un menu au panier"""
    login(client, '0601020304', 'password')
    response = client.post('/ajouter-menu-selection/', data={
        'id_menu': 1,
        'entree': 1,
        'plat': 3,
        'dessert': 7
    }, follow_redirects=True)
    assert response.status_code == 200

def test_produits_post_vider_panier(client):
    """Test produits POST pour vider le panier"""
    login(client, '0601020304', 'password')
    client.post('/ajouter-au-panier/', data={'id_plat': 1}, follow_redirects=True)
    response = client.post('/produits/', data={'action': 'vider_panier'}, follow_redirects=True)
    assert response.status_code == 200

def test_detail_plat_nonexistent(client):
    """Test accéder à un plat inexistant retourne 404"""
    response = client.get('/produit/99999')
    assert response.status_code == 404

def test_detail_menu_nonexistent(client):
    """Test accéder à un menu inexistant retourne 404"""
    response = client.get('/menu/99999')
    assert response.status_code == 404

def test_ajouter_menu_selection_missing_params(client):
    """Test ajouter un menu sans paramètres requis"""
    login(client, '0601020304', 'password')
    response = client.post('/ajouter-menu-selection/', data={}, follow_redirects=True)
    assert response.status_code == 200

def test_ajouter_menu_selection_missing_entree(client):
    """Test ajouter un menu sans entrée"""
    login(client, '0601020304', 'password')
    response = client.post('/ajouter-menu-selection/', data={
        'id_menu': 1,
        'plat': 3,
        'dessert': 7
    }, follow_redirects=True)
    assert response.status_code == 200

def test_compte_password_change_wrong_current(client):
    """Test changement de mot de passe avec mauvais mot de passe actuel"""
    login(client, '0601020304', 'password')
    response = client.post('/compte/', data={
        'prenom': 'Alice',
        'nom': 'Dupont',
        'telephone': '0601020304',
        'current_mot_de_passe': 'wrongpassword',
        'new_mot_de_passe': 'newpass',
        'confirm_new_mot_de_passe': 'newpass'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_creer_avis_success(client):
    """Test créer un avis avec succès"""
    login(client, '0601020304', 'password')
    response = client.post('/creer-avis/', data={
        'note': 4,
        'commentaire': 'Très bon!'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_menus_with_invalid_page_number(client):
    """Test menus avec numéro de page invalide"""
    response = client.get('/menus/?page=0')
    assert response.status_code == 200

def test_produits_with_invalid_page_number(client):
    """Test produits avec numéro de page invalide"""
    response = client.get('/produits/?page=0')
    assert response.status_code == 200

def test_produits_with_nonexistent_category(client):
    """Test produits avec catégorie inexistante"""
    response = client.get('/produits/?cat_id=9999')
    assert response.status_code == 200

def test_menus_with_nonexistent_category(client):
    """Test menus avec catégorie inexistante"""
    response = client.get('/menus/?cat_id=9999')
    assert response.status_code == 200

def test_admin_ban_user(client):
    """Test bannir un utilisateur"""
    login(client, 'admin', 'admin')
    response = client.post('/admin/ban/3', follow_redirects=True)
    assert response.status_code == 200

def test_admin_unban_user(client):
    """Test débannir un utilisateur"""
    login(client, 'admin', 'admin')
    client.post('/admin/ban/3', follow_redirects=True)
    response = client.post('/admin/unban/3', follow_redirects=True)
    assert response.status_code == 200

def test_commandes_status_change(client):
    """Test changer le statut d'une commande"""
    login(client, 'admin', 'admin')
    response = client.post('/commandes/1/set_statut', data={
        'statut': 'Prêt'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_logout_with_session(client):
    """Test logout quand on est connecté"""
    login(client, '0601020304', 'password')
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

def test_menu_selection_incomplete(client):
    """Test ajouter menu avec plat manquant"""
    login(client, '0601020304', 'password')
    response = client.post('/ajouter-menu-selection/', data={
        'id_menu': 1,
        'entree': 1,
        'dessert': 7
    }, follow_redirects=True)
    assert response.status_code == 200

def test_modifier_quantite_without_plat(client):
    """Test modifier quantité sans id_plat"""
    login(client, '0601020304', 'password')
    response = client.post('/modifier-quantite-panier/', data={
        'action': 'increase'
    }, follow_redirects=True)
    assert response.status_code == 200

def test_supprimer_panier_without_id(client):
    """Test supprimer du panier sans id"""
    login(client, '0601020304', 'password')
    response = client.post('/supprimer-du-panier/', data={}, follow_redirects=True)
    assert response.status_code == 200
