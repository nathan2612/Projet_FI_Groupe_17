from monApp.models import CLIENT
from monApp.forms import (
    InscriptionForm, ConnexionForm, EditProfileForm, 
    PlatForm, MenuForm, ReservationForm, ServiceForm
)
import pytest

def test_client_methods():
    admin = CLIENT(id_client=1, role='admin')
    assert admin.get_id() == 1
    assert admin.is_admin() is True
    
    user = CLIENT(id_client=2, role='user')
    assert user.is_admin() is False

def test_inscription_form_fields(testapp):
    with testapp.app_context():
        form = InscriptionForm()
        assert hasattr(form, 'id_client')
        assert hasattr(form, 'prenom')
        assert hasattr(form, 'nom')
        assert hasattr(form, 'telephone')
        assert hasattr(form, 'mot_de_passe')
        assert hasattr(form, 'confirmation_mot_de_passe')

def test_connexion_form_fields(testapp):
    with testapp.app_context():
        form = ConnexionForm()
        assert hasattr(form, 'telephone')
        assert hasattr(form, 'mot_de_passe')
        assert hasattr(form, 'next')

def test_edit_profile_form_fields(testapp):
    with testapp.app_context():
        form = EditProfileForm()
        assert hasattr(form, 'prenom')
        assert hasattr(form, 'nom')
        assert hasattr(form, 'telephone')
        assert hasattr(form, 'current_mot_de_passe')
        assert hasattr(form, 'new_mot_de_passe')
        assert hasattr(form, 'confirm_new_mot_de_passe')

def test_plat_form_fields(testapp):
    with testapp.app_context():
        form = PlatForm()
        assert hasattr(form, 'id_plat')
        assert hasattr(form, 'nom_plat')
        assert hasattr(form, 'id_categorie')
        assert hasattr(form, 'description')
        assert hasattr(form, 'prix')
        assert hasattr(form, 'disponible')
        assert hasattr(form, 'vegetarien')
        assert hasattr(form, 'vegan')
        assert hasattr(form, 'gluten')
        assert hasattr(form, 'lactose')

def test_plat_form_validate_prix_valid(testapp):
    with testapp.app_context():
        form = PlatForm()
        form.prix.data = '12.50'
        try:
            form.validate_prix(form.prix)
        except ValueError:
            pytest.fail("validate_prix raised ValueError for valid price")

def test_plat_form_validate_prix_comma(testapp):
    with testapp.app_context():
        form = PlatForm()
        form.prix.data = '12,50'
        try:
            form.validate_prix(form.prix)
        except ValueError:
            pytest.fail("validate_prix raised ValueError for valid comma-separated price")

def test_plat_form_validate_prix_negative(testapp):
    with testapp.app_context():
        form = PlatForm()
        form.prix.data = '-5.50'
        with pytest.raises(ValueError):
            form.validate_prix(form.prix)

def test_plat_form_validate_prix_invalid(testapp):
    with testapp.app_context():
        form = PlatForm()
        form.prix.data = 'invalid'
        with pytest.raises(ValueError):
            form.validate_prix(form.prix)

def test_menu_form_fields(testapp):
    with testapp.app_context():
        form = MenuForm()
        assert hasattr(form, 'id_menu')
        assert hasattr(form, 'nom_menu')
        assert hasattr(form, 'description')
        assert hasattr(form, 'prix')
        assert hasattr(form, 'entrees')
        assert hasattr(form, 'plats')
        assert hasattr(form, 'desserts')

def test_menu_form_validate_prix_valid(testapp):
    with testapp.app_context():
        form = MenuForm()
        form.prix.data = '19.99'
        try:
            form.validate_prix(form.prix)
        except ValueError:
            pytest.fail("validate_prix raised ValueError for valid price")

def test_menu_form_validate_prix_negative(testapp):
    with testapp.app_context():
        form = MenuForm()
        form.prix.data = '-10'
        with pytest.raises(ValueError):
            form.validate_prix(form.prix)

def test_menu_form_validate_prix_invalid(testapp):
    with testapp.app_context():
        form = MenuForm()
        form.prix.data = 'notanumber'
        with pytest.raises(ValueError):
            form.validate_prix(form.prix)

def test_reservation_form_fields(testapp):
    with testapp.app_context():
        form = ReservationForm()
        assert hasattr(form, 'id_client')
        assert hasattr(form, 'date_reservation')
        assert hasattr(form, 'id_service')
        assert hasattr(form, 'nb_personne')

def test_service_form_fields(testapp):
    with testapp.app_context():
        form = ServiceForm()
        assert hasattr(form, 'heure_debut')
        assert hasattr(form, 'heure_fin')

def test_plat_form_validate_prix_zero(testapp):
    """Test que le prix 0 est accepté"""
    with testapp.app_context():
        form = PlatForm()
        form.prix.data = '0'
        try:
            form.validate_prix(form.prix)
        except ValueError:
            pytest.fail("validate_prix should accept 0")

def test_plat_form_validate_prix_large_number(testapp):
    """Test avec un grand nombre"""
    with testapp.app_context():
        form = PlatForm()
        form.prix.data = '999999.99'
        try:
            form.validate_prix(form.prix)
        except ValueError:
            pytest.fail("validate_prix should accept large numbers")

def test_menu_form_validate_prix_zero(testapp):
    """Test que le prix 0 est accepté"""
    with testapp.app_context():
        form = MenuForm()
        form.prix.data = '0'
        try:
            form.validate_prix(form.prix)
        except ValueError:
            pytest.fail("validate_prix should accept 0")

def test_connexion_form_get_authenticated_client_success(testapp):
    """Test que get_authenticated_client retourne le client avec le bon mot de passe"""
    with testapp.app_context():
        form = ConnexionForm()
        form.telephone.data = '0601020304'
        form.mot_de_passe.data = 'password'
        result = form.get_authenticated_client()
        assert result is not None
        assert result.id_client == 1

def test_connexion_form_get_authenticated_client_wrong_password(testapp):
    """Test que get_authenticated_client retourne None avec mauvais mot de passe"""
    with testapp.app_context():
        form = ConnexionForm()
        form.telephone.data = '0601020304'
        form.mot_de_passe.data = 'wrongpassword'
        result = form.get_authenticated_client()
        assert result is None

def test_connexion_form_get_authenticated_client_nonexistent(testapp):
    """Test que get_authenticated_client retourne None si le client n'existe pas"""
    with testapp.app_context():
        form = ConnexionForm()
        form.telephone.data = '9999999999'
        form.mot_de_passe.data = 'password'
        result = form.get_authenticated_client()
        assert result is None

def test_plat_form_all_allergies_fields(testapp):
    """Test que tous les champs allergie existent"""
    with testapp.app_context():
        form = PlatForm()
        assert hasattr(form, 'gluten')
        assert hasattr(form, 'lactose')
        assert hasattr(form, 'fruit_a_coque')
        assert hasattr(form, 'crustaces')

def test_plat_form_description_fields(testapp):
    """Test tous les champs de description"""
    with testapp.app_context():
        form = PlatForm()
        assert hasattr(form, 'description')
        assert hasattr(form, 'longue_description')
        assert hasattr(form, 'image_url')

def test_menu_form_validate_prix_comma(testapp):
    """Test prix avec virgule"""
    with testapp.app_context():
        form = MenuForm()
        form.prix.data = '19,99'
        try:
            form.validate_prix(form.prix)
        except ValueError:
            pytest.fail("validate_prix should accept comma-separated price")

def test_edit_profile_form_password_fields(testapp):
    """Test les champs de mot de passe du profil"""
    with testapp.app_context():
        form = EditProfileForm()
        assert hasattr(form, 'current_mot_de_passe')
        assert hasattr(form, 'new_mot_de_passe')
        assert hasattr(form, 'confirm_new_mot_de_passe')

def test_plat_form_with_categories(testapp):
    """Test que le formulaire a un champ catégorie"""
    with testapp.app_context():
        form = PlatForm()
        assert hasattr(form, 'id_categorie')

def test_reservation_form_service_choices(testapp):
    """Test que les choix de service sont initialisés"""
    with testapp.app_context():
        form = ReservationForm()
        assert form.id_service.choices == []

def test_menu_form_plats_choices(testapp):
    """Test que les choix de plats sont initialisés"""
    with testapp.app_context():
        form = MenuForm()
        assert hasattr(form, 'plats')
        assert hasattr(form, 'entrees')
        assert hasattr(form, 'desserts')