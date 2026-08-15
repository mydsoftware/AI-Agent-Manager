from manager.auth import APIAuthenticator


def test_api_authenticator_rejects_missing_key():
    auth = APIAuthenticator()
    assert auth.validate(None) is False


def test_api_authenticator_rejects_empty_key():
    auth = APIAuthenticator()
    assert auth.validate("") is False
