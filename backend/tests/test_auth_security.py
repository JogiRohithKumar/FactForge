from app.core.security import create_access_token, decode_access_token, hash_password, verify_password

def test_password_hash_is_not_plaintext_and_verifies():
    password = "correct horse battery staple"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong password", hashed)

def test_signed_session_token_round_trip():
    token = create_access_token("user-123")
    assert decode_access_token(token) == "user-123"
    assert decode_access_token("not-a-token") is None
