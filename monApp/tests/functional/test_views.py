import pytest
from flask import url_for

def login(client, telephone, password):
    return client.post('/connexion/', data=dict(
        telephone=telephone,
        mot_de_passe=password
    ), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

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
