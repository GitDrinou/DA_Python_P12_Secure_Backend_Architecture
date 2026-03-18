from security.passwords import hash_password, verify_password


def test_password_hash():
    password = "MonMotDePasseTresFort95"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(hashed, password) is True
    assert verify_password(hashed, "mauvais_mot_de_passe") is False
