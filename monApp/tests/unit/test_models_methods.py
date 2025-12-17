from monApp.models import CLIENT

def test_client_methods():
    admin = CLIENT(id_client=1, role='admin')
    assert admin.get_id() == 1
    assert admin.is_admin() is True
    
    user = CLIENT(id_client=2, role='user')
    assert user.is_admin() is False